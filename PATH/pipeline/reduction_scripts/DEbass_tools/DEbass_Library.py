# A library of useful code for DEbass
import os

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

def makeDir(dir):
    try:
        os.makedirs(dir)
        print('Created %s' % dir)
    except:
        print('INFO: %s already exists' % dir)

    return

def getObsDateDirName(inputFile):
    dirName="%s%s%sT%s:%s" % (inputFile[7:11],months[inputFile[11:13]],inputFile[13:15],inputFile[16:18],inputFile[18:20])

    return dirName

def getObsDate(inputFile):
    dirName="%s" % (inputFile[7:15])

    return dirName

def getPipelineVersion():
    pipelineDir='%s/current' % (os.environ['DEBASSPIPLINE'])

    return os.readlink(pipelineDir)
