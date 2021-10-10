#!/pkg/linux/anaconda/bin/python
# Python program to insert keywods into headers into data that were processed before v01 of the pipeline was fully finalised

import DEbass_Library as DEbass
import argparse
import os
import shutil as sh
import astropy.io.fits as fits

def main(args):

    # Some important paths
    DEbassReducedDir="%s/%s" % (os.environ['DEBASSREDUCED'], args.SN)
    DEbassAnalysisDir="%s/%s" % (os.environ['DEBASSANALYSIS'], args.SN)

    # Paths for the reduced direcrtories
    # Since, we've only processed data with v01 using metdata m01, we harcode these"
    redMetaDatatDir="%s/%s/v01/m01" % (DEbassReducedDir,args.dateDir)

    # Create the directory in the analysis directory
    DEbass.makeDir(DEbassAnalysisDir)
    
    analDateDir="%s/%s" % (DEbassAnalysisDir,args.dateDir)
    DEbass.makeDir(analDateDir)

    # Since, we've only processed data with v01 using metdata m01, we harcode these"
    analVersionDir="%s/v01" % (analDateDir)
    DEbass.makeDir(analVersionDir)
    
    analMetaDataDir="%s/m01" % (analVersionDir)
    DEbass.makeDir(analMetaDataDir)

    # Make the snid, marz, snid, and superfit dirctories

    for technique in ['marz','superfit','snid', 'dash']:
        DEbass.makeDir("%s/%s" %(analMetaDataDir,technique))
    

    redDate=DEbass.getUTC()

    if args.ToO is not None:
        ToO=True
        ToOTime = args.ToO
    else:
        ToO=False
 
    # Update the FITS files
    files=os.listdir(redMetaDatatDir)
    for f in files:
        if f[-5:]==".fits":
            inputFile="%s/%s" % (redMetaDatatDir,f)
            hdu=fits.open(inputFile,mode='update')
            hdu[0].header['REDUCBY']=args.reducedBy
            hdu[0].header['OBSERVBY']=args.observedBy
            hdu[0].header['REDDATE']=redDate
            hdu[0].header['PIPELINE']='v01'
            hdu[0].header['METADATA']='m01'
            hdu[0].header['TOO']=ToO
            if ToO:
                hdu[0].header['TOOTIME']=args.ToO
            hdu.close()
        elif f[-4:]==".dat":
            # Update the data file
            # Write out header information
            inputFile="%s/%s" % (redMetaDatatDir,f)
            outputFile="%s/%s_mod" % (redMetaDatatDir,f)
            input=open(inputFile)
            inputData=input.readlines()
            input.close()

            output=open(outputFile,'w')
            
            output.write("# Observed by %s\n" % (args.observedBy))
            output.write("# Reduced by %s\n" % (args.reducedBy))
            output.write("# On %s\n" % (redDate))
            output.write("# Using DEbass pipeline: v01\n")
            output.write("# Using metadata: m01\n")
            output.write("#\n")
            output.write("# Wavelength Flux Error\n")
            for line in inputData:
                if line[0] != '#':
                    output.write(line)
  
            output.close()

            # Overwrite the old file
            sh.move(outputFile, inputFile)
        
            # Copy it to the superfit directory
            
            sh.copy(inputFile, "%s/superfit/" % (analMetaDataDir))

    return

    
if __name__ == '__main__':
    
    parser=argparse.ArgumentParser(description="Collate the recduced data")

    parser.add_argument('--SN', dest='SN',
                        default=None,
                        help='SN name')

    parser.add_argument('--dateDir', dest='dateDir',
                        default=None,
                        help='Directory of Observation')

    parser.add_argument('--reducedBy', dest='reducedBy',
                        default=None,
                        help='Person who processed the data')

    parser.add_argument('--observedBy', dest='observedBy',
                        default=None,
                        help='Person who observed')

    parser.add_argument('--ToO', dest='ToO',
                        default=None,
                        help='Time spent on ToO (minutes)')

    args=parser.parse_args()

    main(args)
