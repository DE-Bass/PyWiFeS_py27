# A library of useful code for DEbass
import os
import time

months={"01":"Jan",
        "02":"Feb",
        "03":"Mar",
        "04":"Apr",
        "05":"May",
        "06":"Jun",
        "07":"Jul",
        "08":"Aug",
        "09":"Sep",
        "10":"Oct",
        "11":"Nov",
        "12":"Dec"}

reducers={"clidman":"C. Lidman"}


def makeDir(dir):
    try:
        os.makedirs(dir)
        print('Created %s' % dir)
    except:
        print('INFO: %s already exists' % dir)

    return

def getObsDateDirName(inputFile):
    dirName="%s%s%sT%s:%s" % (inputFile[7:11],months[inputFile[11:13]],inputFile[13:15],inputFile[16:18],inputFile[18:20])
    #Adjusted for the new pipeline naming convention
    #index=inputFile.find("UT")
    #dirName="%s%s%sT%s:%s" % (inputFile[index+2:index+6],months[inputFile[index+6:index+8]],inputFile[index+8:index+10],inputFile[index+11:index+13],inputFile[index+13:index+15])

    return dirName

def getObsDate(inputFile):
    dirName="%s" % (inputFile[7:15])
    #Adjusted for the new pipeline naming convention
    #index=inputFile.find("UT")
    #dirName="%s" % (inputFile[index+2:index+10])


    return dirName

def getPipelineVersion():
    pipelineDir='%s/current' % (os.environ['DEBASSPIPELINE'])

    return os.readlink(pipelineDir)

def getMetadataVersion():
    # Assumes that one is in the correct directory
    metaDataVersion=os.getcwd()[-3:]
    rawInput=raw_input("Enter the metaData version if it is not %s, otherwise hit return " % metaDataVersion)
    if rawInput != '':
        return rawInput
    else:
        return metaDataVersion

def setName():
    #Sets the reducer name based on the user name
    user=os.path.expanduser("~").split("/")[-1]
    return reducers[user]

def getUTC():
    return time.strftime("%d/%m/%Y, %H:%M:%S", time.gmtime())

def touch(fname):
    if os.path.exists(fname):
        os.utime(fname, None)
    else:
        open(fname, 'a').close()
