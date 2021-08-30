#!/pkg/linux/anaconda/bin/python

import DEbass_Library as DEbass
import argparse
import os
import pickle
import shutil as sh

def main(args):

    # Move to the appropriate directory
    DEbassData=os.environ['DEBASSDATA']
    pipelineVersion=DEbass.getPipelineVersion()

    outputDir='%s/working/%s/%s/%s/raw_data' % \
        (DEbassData,args.date,pipelineVersion,args.metadataVersion)
    os.chdir(outputDir)

    # Read in the pickle files
    wifesB='wifesB_%s_metadata.pkl' % args.date
    wifesR='wifesR_%s_metadata.pkl' % args.date

    f1 = open(wifesB, 'r')
    blue_metadata = pickle.load(f1)
    f1.close()

    f1 = open(wifesR, 'r')
    red_metadata = pickle.load(f1)
    f1.close()

    blueFileList=[]
    redFileList=[]

    # Extract the files from the pickle object
    for obs_type in blue_metadata:
        if obs_type in ['sci','std']:
            for index,obs in enumerate(blue_metadata[obs_type]):
                for key in obs:
                    if key in ['sci','sky']:
                        blueFileList+=obs[key]
        else:
            blueFileList+=blue_metadata[obs_type]

    # Extract the files from the pickle object
    for obs_type in red_metadata:
        if obs_type in ['sci','std']:
            for index,obs in enumerate(red_metadata[obs_type]):
                for key in obs:
                    if key in ['sci','sky']:
                        redFileList+=obs[key]
        else:
            redFileList+=red_metadata[obs_type]

    fileList=blueFileList+redFileList

    # Create data with logical links to the raw data
    DEbassRawData=os.environ['DEBASSRAW']        

    for f in fileList:
        inputDir='%s/%s' % (DEbassRawData,DEbass.getObsDate(f))

        try:
            os.symlink('%s/%s.fits' % (inputDir,f), '%s/%s.fits' % (outputDir,f))
            print("INFO: Creating logical link for file %s" % f)
        except OSError:
            print("INFO: Logical link exists for file %s" % f)

    # Copy accross the reduction scripts
    # Move to the appropriate directory
    outputDir='%s/working/%s/%s/%s/' % \
        (DEbassData,args.date,pipelineVersion,args.metadataVersion)
    os.chdir(outputDir)

    PYWIFESPATH=os.environ['PYWIFESPATH']
    outputRed='reduce_red_data.py'
    outputBlue='reduce_blue_data.py'
    if args.offsetSky:
        inputRed='%s/pipeline/reduction_scripts/reduce_red_data_offsetSky.py' % (PYWIFESPATH)
        inputBlue='%s/pipeline/reduction_scripts/reduce_blue_data_offsetSky.py' % (PYWIFESPATH)
    else:
        inputRed='%s/pipeline/reduction_scripts/reduce_red_data_NandS.py' % (PYWIFESPATH)
        inputBlue='%s/pipeline/reduction_scripts/reduce_blue_data_NandS.py' % (PYWIFESPATH)
        
    sh.copy(inputRed, outputRed)
    sh.copy(inputBlue, outputBlue)

    return


if __name__ == '__main__':
    
    parser=argparse.ArgumentParser(description="Create the config files")

    parser.add_argument("--date", dest="date",default=None, help="Civil date (YYYYMMDD) at the start of the night")

    parser.add_argument("--meta", dest="metadataVersion",default='m01', help="Metadata version")

    parser.add_argument("--offsetSky", dest="offsetSky",default=False, 
                        action='store_true', help="Set this if observations are not NodAndShuffle")

    args=parser.parse_args()

    if args.date is None:
        print("\nERROR: Please enter the civil data\n")
        exit()

    main(args)
