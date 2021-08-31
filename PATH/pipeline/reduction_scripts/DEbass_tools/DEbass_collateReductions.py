#!/pkg/linux/anaconda/bin/python

import DEbass_Library as DEbass
import argparse
import os
import shutil as sh

def main(args):

    # Some important paths
    DEbassReducedDir=os.environ['DEBASSREDUCED']
    DEbassWorkingDir=os.environ['DEBASSWORKING']

    # Reduced directory path
    SNpathReducedDir="%s/%s" % (DEbassReducedDir,args.SNname)

    # ObsPaths
    obsDate=DEbass.getObsDate(args.blueArm)
    obsDateDirName=DEbass.getObsDateDirName(args.blueArm)
    ObsPathWorkingDir="%s/%s" % (DEbassWorkingDir,obsDate)
    ObsPathReducedDir="%s/%s" % (SNpathReducedDir,obsDateDirName)

    # Retrieve the pipeline version and metadata version numbers
    cwd=os.getcwd()
    if args.metadataVersion is None:
        metaDataVersion=cwd[-3:]
    else:
        metaDataVersion=args.metadataVersion
    if args.pipelineVersion is None:
        pipelineVersion=cwd[-7:-4]
    else:
        pipelineVersion=args.pipelineVersion
        
    print(metaDataVersion,pipelineVersion)


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
    # If the red arm is not set, we assume that it has the same filename strucure as the blue arm
    if args.redArm is not None:
        sh.copy(src="%s/reduc_r/%s" % \
                (origin,args.redArm), dst=destination)
        sh.copy(src="%s/reduc_b/%s" % \
                (origin,args.blueArm), dst=destination)
    else:
        sh.copy(src="%s/reduc_b/%s" % \
                    (origin,args.blueArm), dst=destination)
        sh.copy(src="%s/reduc_r/%s" % \
                    (origin,args.blueArm.replace('T2m3wb','T2m3wr')), dst=destination)
    
    # Copy accross the extracted and spliced data
    sh.copy(src="%s/reduc_s/%s" % \
                (origin,args.blueArm.replace('p11','p12').replace('T2m3wb','T2m3ws')), dst=destination)


    # Metadata
    sh.copy(src="%s/raw_data/save_blue_metadata.py" % (origin), dst=destination)
    sh.copy(src="%s/raw_data/save_red_metadata.py" % (origin), dst=destination)

    blueMetaDataFile="wifesB_%s_metadata.pkl" % (obsDate)
    redMetaDataFile="wifesR_%s_metadata.pkl" % (obsDate)
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

    parser.add_argument('--redArm', dest='redArm',
                        default=None,
                        help='Red arm of WiFeS')

    parser.add_argument('--blueArm', dest='blueArm',
                        default=None,
                        help='Blue arm of WiFeS')

    parser.add_argument("--cleanup", dest="cleanup",default=False, action='store_true',
                        help="Remove the working directory")

    parser.add_argument("--meta", dest="metadataVersion",default=None, help="Metadata version")

    parser.add_argument("--pipline", dest="pipelineVersion",default=None, help="Pipeline version")


    args=parser.parse_args()

    if args.SNname is None:
        print("ERROR: Please enter the name of the SN")
        exit()

    if args.cleanup:
        print("WARNING: Cleanup not yet implimented")

    

    main(args)
