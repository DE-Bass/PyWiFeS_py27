#!/pkg/linux/anaconda-20191122/anaconda2/bin/python2
# Replaces
#/usr/bin/env python2 

"""
DEBass -- Calls the following codes

DEbass_extractSpec.py
DEbass_spliceSpec.py
DEbass_covert2ASCII.py
DEbass_collateReductions.py

"""

import argparse
import copy
import DEbass_extractSpec as extract
import DEbass_spliceSpec as splice
import DEbass_convert2ASCII as convert2ASCII
import DEbass_collateReductions as collateReductions

class options:
    def __init__(self):
        return

def main(args):

    # Extract the SN
    args.suffix="SN"
    args_extract=copy.copy(args)
    extract.main(args_extract)

    # Splice the SN
    args_splice=copy.copy(args)
    args_splice.blueArm=args.blueArm.replace("p11.fits","p12_SN.fits")
    args_splice.redArm=args.redArm.replace("p11.fits","p12_SN.fits")

    splice.main(args_splice)

    # Write out the ascii file
    opt=options
    opt.inputSpectrum=args_splice.blueArm.replace("Blue","Splice").replace("reduc_b/","")
    opt.errFloor=0.1
    convert2ASCII.main(opt)
                        
    # Then the host
    # Need to ask if a host is to be extracted.
    rawInput=raw_input("Type Y if you want to also extract the host galaxy. Otherwise hit return: ")
    if rawInput=='':
        pass
    else:
        args_extract.suffix="host"
        # Extract
        extract.main(args_extract)
        # Splice the host
        args_splice.blueArm=args.blueArm.replace("p11.fits","p12_host.fits")
        args_splice.redArm=args.redArm.replace("p11.fits","p12_host.fits")
        splice.main(args_splice)

    # Collate the results
    args_collate=copy.copy(args)    
    args_splice.blueArm=args.blueArm.replace("reduc_b/","")
    args_splice.redArm=args.redArm.replace("reduc_r/","")
    collateReductions.main(args_splice)

    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Coadd single-object spectra')


    parser.add_argument('--redArm', dest='redArm',
                        default=None,
                        help='Red arm of WiFeS')

    parser.add_argument('--blueArm', dest='blueArm',
                        default=None,
                        help='Red arm of WiFeS')

    parser.add_argument('--scale', dest='scale',
                        default=20, type=int,
                        help='scale')

    parser.add_argument('--reducedBy', dest='reducedBy',
                        default=None,
                        help='Person who processed the data')

    parser.add_argument('--submittedBy', dest='observedBy',
                        default=None,
                        help='Person who observed')

    parser.add_argument('--metadataVersion', dest='metadataVersion',
                        default='m01',
                        help='The verson of the metadata used to process the data')

    parser.add_argument('--skySub', dest='skySub',
                        default=False, action='store_true',
                        help='Subtract Sky')

    parser.add_argument("--SN", dest="SNname",default=None, 
                        help="SN name")

    parser.add_argument('--ToO', dest='ToO',
                        default=None,
                        help='Time spent on ToO (minutes)')

    args = parser.parse_args()

    args.redArm="reduc_r/%s" % (args.redArm)
    args.blueArm="reduc_b/%s" % (args.blueArm)


    main(args)
