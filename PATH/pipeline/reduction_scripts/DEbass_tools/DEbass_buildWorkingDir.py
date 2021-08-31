#!/pkg/linux/anaconda/bin/python

import DEbass_Library as DEbass
import argparse
import os

def main(args):

    # Create the directory structure
    DEbassData=os.environ['DEBASSDATA']
    os.chdir(DEbassData)
    DEbass.makeDir('working')

    # SN observing date
    os.chdir('working')
    DEbass.makeDir(args.date)

    # Pipeline version
    os.chdir(args.date)
    # Get the pipeline version
    pipelineVersion=DEbass.getPipelineVersion()
    DEbass.makeDir(pipelineVersion)

    # Data version
    # The version of the datafiles that went into the pipeline.
    metadataVersion=args.metadataVersion
    os.chdir(pipelineVersion)
    DEbass.makeDir(metadataVersion)

    # Data reduction directories for PyWiFes
    os.chdir(metadataVersion)
    DEbass.makeDir("reduc_r")
    DEbass.makeDir("reduc_b")
    DEbass.makeDir("reduc_s")
    DEbass.makeDir("raw_data")
        
    return

if __name__ == '__main__':
    
    parser=argparse.ArgumentParser(description="Build the Directory Structure for working directory")

    parser.add_argument("--date", dest="date",default=None, help="Civil date (YYYYMMDD) at the start of the night")

    parser.add_argument("--meta", dest="metadataVersion",default='m01', help="Metadata version")

    args=parser.parse_args()

    if args.date is None:
        print("\nERROR: Please enter the civil data\n")
        exit()

    main(args)
