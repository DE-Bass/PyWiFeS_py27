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

    # Retrieve the pipeline version and metadata version numbers
    # This is will fail if you are not already in the correct directory
    
    cwd=os.getcwd()
    if args.metadataVersion is None:
        metaDataVersion=cwd[-3:]
    else:
        metaDataVersion=args.metadataVersion
    if args.pipelineVersion is None:
        pipelineVersion=cwd[-7:-4]
    else:
        pipelineVersion=args.pipelineVersion

    # Retrieve the data, error and important keywords

    inputFile="%s/%s/%s/reduc_s/%s" % (ObsPathWorkingDir,pipelineVersion,metaDataVersion,args.inputSpectrum)
    outputFile=inputFile.replace(".fits",".dat")
    spectrum=fits.getdata(inputFile,0)
    variance=fits.getdata(inputFile,1)
    CRPIX1=fits.getval(inputFile,'CRPIX1',0)
    CRVAL1=fits.getval(inputFile,'CRVAL1',0)
    CDELT1=fits.getval(inputFile,'CDELT1',0)
    NAXIS1=fits.getval(inputFile,'NAXIS1',0)

    wavelength=CRVAL1+(np.arange(NAXIS1)+1.0-CRPIX1)*CDELT1

    scaling=1e16
    

    f=open(outputFile,'w')
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

    parser.add_argument("--errFloor", dest="errFloor",default=0.1, help="errFloor")

    parser.add_argument("--meta", dest="metadataVersion",default=None, help="Metadata version")

    parser.add_argument("--pipline", dest="pipelineVersion",default=None, help="Pipeline version")


    args=parser.parse_args()

    main(args)
