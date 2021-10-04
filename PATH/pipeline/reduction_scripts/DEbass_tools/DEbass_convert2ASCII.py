#!/pkg/linux/anaconda/bin/python
# Convert the SN specrtum to ASCII to be used with superfit

import DEbass_Library as DEbass
import astropy.io.fits as fits
import argparse
import numpy as np
import os
import shutil as sh

def main(args):
    # Some important paths
    DEbassWorkingDir=os.environ['DEBASSWORKING']

    # ObsPaths
    obsDate=DEbass.getObsDate(args.inputSpectrum)
    obsDateDirName=DEbass.getObsDateDirName(args.inputSpectrum)
    ObsPathWorkingDir="%s/%s" % (DEbassWorkingDir,obsDate)
    pipelineVersion=DEbass.getPipelineVersion()
    # Fragile code - depends on CWD
    
    # Retrieve the data, error and important keywords
    
    inputFile="reduc_s/%s" % (args.inputSpectrum)
    try:
        metaDataVersion=fits.getval(inputFile,'METADATA',0)
    except:
        print("Are you in the correct Directory")
        exit()
        
#    inputFile="%s/%s/%s/reduc_s/%s" % (ObsPathWorkingDir,pipelineVersion,metaDataVersion,args.inputSpectrum)

    outputFile=inputFile.replace(".fits",".dat")
    spectrum=fits.getdata(inputFile,0)
    variance=fits.getdata(inputFile,1)
    CRPIX1=fits.getval(inputFile,'CRPIX1',0)
    CRVAL1=fits.getval(inputFile,'CRVAL1',0)
    CDELT1=fits.getval(inputFile,'CDELT1',0)
    NAXIS1=fits.getval(inputFile,'NAXIS1',0)
    reducedBy=fits.getval(inputFile,'REDUCBY',0)
    redDate=fits.getval(inputFile,'REDDATE',0)
    
    wavelength=CRVAL1+(np.arange(NAXIS1)+1.0-CRPIX1)*CDELT1

    scaling=1e16

    f=open(outputFile,'w')
    # Write out header information
    f.write("# Reduced by %s\n" % (reducedBy))
    f.write("# On %s\n" % (redDate))
    f.write("# Using DEbass pipeline: %s\n" % (pipelineVersion))
    f.write("# Using metadata: %s\n" % (metaDataVersion))
    f.write("#\n")
    f.write("# Wavelength Flux Error\n")
    
    # Then the date
    
    for wave,flux,var in zip(wavelength,spectrum,variance):
        if np.isnan(var) or var < 0:
            pass
        else:
            f.write("%7.2f\t%6.4e\t%6.4e\n" % (wave,flux*scaling,np.sqrt(var)*scaling+args.errFloor))
    
    f.close()
    
    return

if __name__ == '__main__':
    
    parser=argparse.ArgumentParser(description="Collate the recduced data")

    parser.add_argument('--inputSpectrum', dest='inputSpectrum',
                        default=None,
                        help='Input Spectrum')

#    parser.add_argument('--ignoreDir', dest='ignoreDir',
#                        default=False, action='store_true',
#                        help='Input Spectrum')

    parser.add_argument("--errFloor", dest="errFloor",default=0.1, help="errFloor")

    args=parser.parse_args()

    main(args)
