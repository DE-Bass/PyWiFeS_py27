#!/pkg/linux/anaconda/bin/python

import DEbass_Library as DEbass
import argparse
import os
import shutil as sh

def main(args):

    # Some important paths
    DEbassReducedDir=os.environ['DEBASSREDUCED']
    DEbassWorkingDir=os.environ['DEBASSWORKING']

    # SNpaths
    SNpathWorkingDir="%s/%s" % (DEbassWorkingDir,args.SNname)
    SNpathReducedDir="%s/%s" % (DEbassReducedDir,args.SNname)

    # ObsPaths
    obsDateDirName=DEbass.getObsDateDirName(args.file)
    ObsPathWorkingDir="%s/%s" % (SNpathWorkingDir,obsDateDirName)
    ObsPathReducedDir="%s/%s" % (SNpathReducedDir,obsDateDirName)
    
    # Retrieve the pipeline version and metadata version numbers
    pipelineVersion=os.listdir(ObsPathWorkingDir)[0]
    metaDataVersion=os.listdir("%s/%s" % (ObsPathWorkingDir,pipelineVersion))[0]
    
    # Create the data structure
    DEbass.makeDir(DEbassReducedDir)
    DEbass.makeDir(SNpathReducedDir)
    DEbass.makeDir(ObsPathReducedDir)
    DEbass.makeDir("%s/%s" %(ObsPathReducedDir,pipelineVersion))
    DEbass.makeDir("%s/%s/%s" %(ObsPathReducedDir,pipelineVersion,metaDataVersion))

    # Copy aross the data
    origin="%s/%s/%s" % (ObsPathWorkingDir,pipelineVersion,metaDataVersion)
    destination="%s/%s/%s" % (ObsPathReducedDir,pipelineVersion,metaDataVersion)

    # Copy accross reduced data
    sh.copy(src="%s/reduc_r/%s.p11.fits" % \
                (origin,args.file.replace('.fits','')), dst=destination)
    sh.copy(src="%s/reduc_b/%s.p11.fits" % \
                (origin,args.file.replace('.fits','').replace('T2m3wr','T2m3wb')), dst=destination)
    
    # Copy accross the extracted and spliced data
    sh.copy(src="%s/reduc_s/%s.p12.fits" % \
                (origin,args.file.replace('.fits','').replace('T2m3wr','T2m3ws')), dst=destination)


    # Metadata
    blueMetaDataFile="wifesB_%s_%s_metadata.pkl" % (args.SNname,obsDateDirName)
    redMetaDataFile="wifesR_%s_%s_metadata.pkl" % (args.SNname,obsDateDirName)
    sh.copy(src="%s/raw_data/%s" % (origin,blueMetaDataFile), dst=destination)
    sh.copy(src="%s/raw_data/%s" % (origin,redMetaDataFile), dst=destination)

    # Reduction scripts
    sh.copy(src="%s/reduce_red_data.py" % (origin), dst=destination)
    sh.copy(src="%s/reduce_blue_data.py" % (origin), dst=destination)



    return

if __name__ == '__main__':
    
    parser=argparse.ArgumentParser(description="Collate the recduced data")

    parser.add_argument("--SN", dest="SNname",default=None, 
                        help="SN name")

    parser.add_argument("--file", dest="file",default=None, 
                        help="File containing the UT time and date of observation")

    parser.add_argument("--cleanup", dest="cleanup",default=False, action='store_true',
                        help="Remove the working directory")


    args=parser.parse_args()

    if args.SNname is None:
        print("ERROR: Please enter the name of the SN")
        exit()

    if args.file is None:
        print("ERROR: Please enter the file name of the first scientific observation")
        exit()

    if args.cleanup:
        print("WARNING: Cleanup not yet implimented")

    main(args)
