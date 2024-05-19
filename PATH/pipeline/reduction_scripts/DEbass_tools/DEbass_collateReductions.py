#!/pkg/linux/anaconda-20191122/anaconda2/bin/python2

import DEbass_Library as DEbass
import argparse
import os
import shutil as sh
import astropy.io.fits as fits

def checkObjectName(obsFile,obj):
    if fits.getval(obsFile,'OBJECT',0) != obj:
        print("WARNING: Object name mismatch - %s vs %s" % (fits.getval(obsFile,'OBJECT',0),obj))
    return

def main(args):

    # Some important paths
    DEbassReducedDir=os.environ['DEBASSREDUCED']
    DEbassWorkingDir=os.environ['DEBASSWORKING']
    DEbassAnalysisDir=os.environ['DEBASSANALYSIS']

    # Reduced directory path
    SNpathReducedDir="%s/%s" % (DEbassReducedDir,args.SNname)
    SNpathAnalysisDir="%s/%s" % (DEbassAnalysisDir,args.SNname)

    # ObsPaths
    if args.baseDir is None:
        obsDate=DEbass.getObsDate(args.blueArm)
    else:
        obsDate=args.baseDir
    obsDateDirName=DEbass.getObsDateDirName(args.blueArm)
    ObsPathWorkingDir="%s/%s" % (DEbassWorkingDir,obsDate)
    ObsPathReducedDir="%s/%s" % (SNpathReducedDir,obsDateDirName)
    ObsPathAnalysisDir="%s/%s" % (SNpathAnalysisDir,obsDateDirName)

    # Retrieve the pipeline version and metadata version numbers
    pipelineVersion=DEbass.getPipelineVersion()
    # Fragile code - depends on CWD
    if args.metadataVersion is None:
        metaDataVersion=DEbass.getMetadataVersion()
    else:
        metaDataVersion=args.metadataVersion


    # Create the data structure - first for the reduced data, then for the analysis dir
    DEbass.makeDir(DEbassReducedDir)
    DEbass.makeDir(SNpathReducedDir)
    DEbass.makeDir(ObsPathReducedDir)
    DEbass.makeDir("%s/%s" %(ObsPathReducedDir,pipelineVersion))
    DEbass.makeDir("%s/%s/%s" %(ObsPathReducedDir,pipelineVersion,metaDataVersion))

    DEbass.makeDir(DEbassAnalysisDir)
    DEbass.makeDir(SNpathAnalysisDir)
    DEbass.makeDir(ObsPathAnalysisDir)
    DEbass.makeDir("%s/%s" %(ObsPathAnalysisDir,pipelineVersion))
    DEbass.makeDir("%s/%s/%s" %(ObsPathAnalysisDir,pipelineVersion,metaDataVersion))

    # Create subdirectories for Superfit, etc.
    for technique in ['marz','superfit','snid', 'dash']:
        DEbass.makeDir("%s/%s/%s/%s" %(ObsPathAnalysisDir,pipelineVersion,metaDataVersion,technique))
    
    # Create a comment file
    DEbass.touch("%s/notes.txt" % SNpathAnalysisDir)
        
    
    # Copy aross the data
    origin="%s/%s/%s" % (ObsPathWorkingDir,pipelineVersion,metaDataVersion)
    ## CLi
    ##origin="/priv/debass/database/working/Anais/v01/m01"
    destination="%s/%s/%s" % (ObsPathReducedDir,pipelineVersion,metaDataVersion)
    analysisDestination="%s/%s/%s" % (ObsPathAnalysisDir,pipelineVersion,metaDataVersion)

    
    # Copy accross reduced data
    # If the red arm is not set, we assume that it has the same filename structure as the blue arm
    
    if args.redArm is not None:
        inputRed="%s/reduc_r/%s" % (origin,args.redArm)
        inputBlue="%s/reduc_b/%s" % (origin,args.blueArm)
        sh.copy(src=inputRed, dst=destination)
        sh.copy(src=inputBlue, dst=destination)
    else:
        inputRed="%s/reduc_r/%s" % (origin,args.blueArm.replace('T2m3wb','T2m3wr'))
        inputBlue="%s/reduc_b/%s" % (origin,args.blueArm)
        sh.copy(src=inputBlue, dst=destination)
        sh.copy(src=inputRed, dst=destination)

    # We check that the Object name in the FITS header matches the Object name used in the command line
    # If they differ, we issue warning.
    # In v02 of the pipeline, we'll ensure that the correct name is included in the p11 file.
    checkObjectName(inputRed,args.SNname)
    checkObjectName(inputBlue,args.SNname)
    
    # Copy across the extracted and spliced data
    # The extracted and spliced data will have the form *p12_ID.fits where ID could be anything,
    # but is generally SN, host, AGN or nothing
    # Search for all files containing the string args.blueArm

#    stub = args.blueArm.replace('T2m3wb','T2m3ws').replace('.p11.fits','')
    stub = args.blueArm.replace('Blue','Splice').replace('.p11.fits','')
    dirContents=os.listdir("%s/reduc_s" % origin)
    for f in dirContents:
        if stub in f:
            sh.copy(src="%s/reduc_s/%s" % \
                    (origin,f), dst=destination)

    # Copy accross the extracted data for superfit
    for f in dirContents:
        if stub in f and 'dat' in f:
            sh.copy(src="%s/reduc_s/%s" % \
                    (origin,f), dst="%s/superfit/" % analysisDestination)
            
    # Metadata
    sh.copy(src="%s/raw_data/save_blue_metadata.py" % (origin), dst=destination)
    sh.copy(src="%s/raw_data/save_red_metadata.py" % (origin), dst=destination)

    blueMetaDataFile="wifesB_%s_metadata.pkl" % (obsDate)
    redMetaDataFile="wifesR_%s_metadata.pkl" % (obsDate)
    ## CLi
    ##blueMetaDataFile="wifesB_%s_metadata.pkl" % ("20231006")
    ##redMetaDataFile="wifesR_%s_metadata.pkl" % ("20231006")
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

    parser.add_argument("--baseDir", dest="baseDir",default=None, 
                        help="Directory where data is processed. Leave blank if using the date")

    parser.add_argument('--redArm', dest='redArm',
                        default=None,
                        help='Red arm of WiFeS')

    parser.add_argument('--blueArm', dest='blueArm',
                        default=None,
                        help='Blue arm of WiFeS')

    parser.add_argument("--cleanup", dest="cleanup",default=False, action='store_true',
                        help="Remove the working directory")

    parser.add_argument("--metadataVersion", dest="metadataVersion",default='m01', help="Metadata version")

    parser.add_argument("--pipline", dest="pipelineVersion",default=None, help="Pipeline version")


    args=parser.parse_args()

    if args.SNname is None:
        print("ERROR: Please enter the name of the SN")
        exit()

    if args.cleanup:
        print("WARNING: Cleanup not yet implimented")

    

    main(args)
