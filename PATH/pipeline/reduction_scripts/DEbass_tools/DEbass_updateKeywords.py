#!/pkg/linux/anaconda/bin/python
# Python program to insert keywods into headers into data that were processed before v01 of the pipeline was fully finalised

import DEbass_Library as DEbass
import argparse
import os
import shutil as sh
import astropy.io.fits as fits
import numpy as np

def main(args):

    # Some important paths
    DEbassReducedDir="%s/%s" % (os.environ['DEBASSREDUCED'], args.SN)
    DEbassAnalysisDir="%s/%s" % (os.environ['DEBASSANALYSIS'], args.SN)

    # Paths for the reduced direcrtories
    # Since, we've only processed data with v01, we hardcoded this"
    redMetaDatatDir="%s/%s/v01/%s" % (DEbassReducedDir,args.dateDir,args.metaData)

    # Create the directory in the analysis directory
    DEbass.makeDir(DEbassAnalysisDir)
    
    analDateDir="%s/%s" % (DEbassAnalysisDir,args.dateDir)
    DEbass.makeDir(analDateDir)

    # Since, we've only processed data with v01 using metdata m01, we harcode these"
    analVersionDir="%s/v01" % (analDateDir)
    DEbass.makeDir(analVersionDir)
    
    analMetaDataDir="%s/%s" % (analVersionDir,args.metaData)
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
            hdu[0].header['METADATA']=args.metaData
            hdu[0].header['TOO']=ToO
            if ToO:
                hdu[0].header['TOOTIME']=args.ToO
            hdu.close()
            if args.createASCII and 'T2m3ws' in f:
                # Only select the spliced spectrum
                spectrum=fits.getdata(inputFile,0)
                variance=fits.getdata(inputFile,1)
                CRPIX1=fits.getval(inputFile,'CRPIX1',0)
                CRVAL1=fits.getval(inputFile,'CRVAL1',0)
                CDELT1=fits.getval(inputFile,'CDELT1',0)
                NAXIS1=fits.getval(inputFile,'NAXIS1',0)
                # Create the ASCII file
                outputFile=open(inputFile.replace('.fits','.dat'),'w')
                outputFile.write("# Observed by %s\n" % (args.observedBy))
                outputFile.write("# Reduced by %s\n" % (args.reducedBy))
                outputFile.write("# On %s\n" % (redDate))
                outputFile.write("# Using DEbass pipeline: v01\n")
                outputFile.write("# Using metadata: %s\n" % (args.metaData))
                outputFile.write("#\n")
                outputFile.write("# Wavelength Flux Error\n")
                wavelength=CRVAL1+(np.arange(NAXIS1)+1.0-CRPIX1)*CDELT1
                scaling=1e16

                # Then the data
    
                for wave,flux,var in zip(wavelength,spectrum,variance):
                    if np.isnan(var) or var < 0:
                        pass
                    else:
                        outputFile.write("%7.2f\t%6.4e\t%6.4e\n" % (wave,flux*scaling,np.sqrt(var)*scaling+args.errFloor))
    
                outputFile.close()
                # Copy it to the superfit directory
            
                sh.copy(inputFile.replace('.fits','.dat'), "%s/superfit/" % (analMetaDataDir))


        elif f[-4:]==".dat" and not args.createASCII:
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

    parser.add_argument('--metaData', dest='metaData',
                        default='m01',
                        help='metaData')

    parser.add_argument('--ToO', dest='ToO',
                        default=None,
                        help='Time spent on ToO (minutes)')

    parser.add_argument('--createASCII', dest='createASCII',
                        default=False,action= 'store_true',
                        help='Time spent on ToO (minutes)')

    parser.add_argument("--errFloor", dest="errFloor",default=0.1, help="errFloor")

    args=parser.parse_args()

    main(args)
