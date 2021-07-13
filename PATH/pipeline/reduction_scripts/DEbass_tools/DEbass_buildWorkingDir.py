#!/pkg/linux/anaconda/bin/python

import DEbass_Library as DEbass
import argparse
import os

def main(args):

    # Create the directory structure
    DEbassData=os.environ['DEBASSDATA']
    os.chdir(DEbassData)
    DEbass.makeDir('working')

    # SN directory
    os.chdir('working')
    DEbass.makeDir(args.SNname)

    # SN observing date
    os.chdir(args.SNname)
    obsDateDirName=DEbass.getObsDateDirName(args.file)
    DEbass.makeDir(obsDateDirName)

    # Pipeline version
    os.chdir(obsDateDirName)
    # Get the pipeline version
    # This could be an environment variable that we set up with another python script, or
    # it could query the version number of the current version being used
    # It is fixed for now
    pipelineVersion="v01"
    DEbass.makeDir(pipelineVersion)

    # Data version
    # The version of the datafiles that went into the pipeline.
    # It is fixed for now
    # We need a clever way of tagging this
    metadataVersion="m01"
    os.chdir(pipelineVersion)
    DEbass.makeDir(metadataVersion)

    # Data reduction directories for PyWiFes
    os.chdir(metadataVersion)
    DEbass.makeDir("reduc_r")
    DEbass.makeDir("reduc_b")
    DEbass.makeDir("reduc_c")
    DEbass.makeDir("raw_data")
        
    return

if __name__ == '__main__':
    
    parser=argparse.ArgumentParser(description="Build the Directory Structure for working directory")

    parser.add_argument("--SN", dest="SNname",default=None, help="SN name")

    parser.add_argument("--file", dest="file",default=None, help="File containing the UT time and date of observation")

    args=parser.parse_args()

    if args.SNname is None:
        print("\nERROR: Please enter the name of the SN\n")
        exit()

    if args.file is None:
        print("\nERROR: Please enter the file name of the first scientific observation\n")
        exit()

    main(args)
