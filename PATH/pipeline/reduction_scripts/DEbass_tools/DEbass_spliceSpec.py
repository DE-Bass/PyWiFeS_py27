#!/pkg/linux/anaconda-20191122/anaconda2/bin/python2

"""
DEbass -- Splicing the red and blue ends of WiFeS data
"""

import astropy.io.fits as fits
import argparse
import numpy as np
import scipy.sparse as sp
import DEbass_Library as DEbass

#from helcorr import heliocorr
#from time import gmtime, strftime
# ============================================================================
#              Universal constants - static wavelength solution
# ============================================================================

#print numpy.__version__

# ============================================================================
#                   Baseline helper functions and classes
# ============================================================================

version_tag = "v01"

# v01 - Modified version of combinedspec.py code used in OzDES


class DEbassExcept(Exception):
    """
    Simple exception class
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "{0}: {1}".format(self.__class__.__name__, msg)


class VerboseMessager(object):
    """
    Verbose messaging for routines below
    """

    def __init__(self, verbose=False):
        self.verbose = verbose

    def __call__(self, *args):
        if self.verbose:
            print " ".join([str(a) for a in args])
            sys.stdout.flush()


def is_evenly_sampled(_x):
    dx = _x[1:] - _x[:-1]
    return (abs((dx.max() - dx.min())/np.median(dx)) < 1e-3)

def _A_lanczos(_x, x, a=2, missing=np.nan):
    """
    Returns transformation matrix for Lanczos (sinc) interpolation

    Inputs
       _x:  x-values at which the original function is sampled
        x:  x-values to which we want to interpolate
        a:  integer order of the kernel
        missing:  value to use for missing data (default:  np.nan)
    Outputs
        A:  sparse representation of the transformation matrix
    """
    if not is_evenly_sampled(_x):
        print "_A_lanczos:  warning -- _x not evenly sampled!"
        print "Lanczos interpolation may not give good results."
    # Figure out which x values are in range
    x = np.atleast_1d(x)
    ok = np.all([x >= _x[0], x < _x[-1]], axis=0)
    # Find bins and fractional positions within bins, and interpolate
    fi = np.array((len(_x) - 1) * (x - _x[0]) / (_x[-1] - _x[0]))
    i = np.array([np.int(f) for f in fi])
    # Write down the matrix for Lanczos interpolation
    EPSILON = np.finfo(np.double).eps
    # The following line of code results in a deprecation waring
    # A sparce matrix in link list format
    A = sp.lil_matrix((len(x), len(_x)))
    for m in np.arange(len(x)):
        # If x[m] is in interpolation range...
        if ok[m]:
            # Generate a range of i within the original signal
            ik = range(max(0, i[m]-a+1), min(len(_x) - 1, i[m]+a+1))
            # Find L(x-i) for each of these
            xk = np.pi*(fi[m] - np.array(ik) + EPSILON)
            w = a*np.sin(xk)*np.sin(xk/a)/xk**2
            A[m, ik] = w/w.sum()
        elif x[m] == _x[-1]:  A[m, -1] = 1
        else:  A[m, 0] = missing
    return A


# Unclear if needed
class SingleSpec(object):
    """
    Class representing a single spectrum for analysis
    """

    def __init__(self, fitsFILE):

        self.flux,self.header=fits.getdata(fitsFILE,0,header=True)
        self.wl=(np.arange(self.header['NAXIS1']) - self.header['CRPIX1']+1)*self.header['CDELT1'] + self.header['CRVAL1']
        # Temporary
        self.fluxvar = fits.getdata(fitsFILE,1,header=False)
        self.minWL=np.min(self.wl)
        self.maxWL=np.max(self.wl)
        return

        

# ============================================================================
#                Constants (down here b/c some may be classes)
# ============================================================================


vmsg = VerboseMessager(verbose=True)

# ============================================================================
#                       Various stages of the reduction
# ============================================================================




def joinSpectra(blueSpec, redSpec, args):
    """
    Resample and join the red and blue spectrograph arms.

    """
    
    # Generate the resampling matrices
    blueCRVAL1=blueSpec.header['CRVAL1']
    blueCDELT1=blueSpec.header['CDELT1']
    blueCRPIX1=blueSpec.header['CRPIX1']
    blueNAXIS1=blueSpec.header['NAXIS1']

    redCRVAL1=redSpec.header['CRVAL1']
    redCDELT1=redSpec.header['CDELT1']
    redCRPIX1=redSpec.header['CRPIX1']
    redNAXIS1=redSpec.header['NAXIS1']

    nwl=int((redCRVAL1 + redCDELT1 * redNAXIS1 - blueCRVAL1) / blueCDELT1)
    wl=(np.arange(nwl) - blueCRPIX1+1)*blueCDELT1 + blueCRVAL1

    # One does not need to interplolate the blue spectra if the waveelength is
    # set to the blue spectrum. However the code is robust to this.
    
    AB = _A_lanczos(blueSpec.wl, wl, 3).tocsr()
    AR = _A_lanczos(redSpec.wl, wl, 3).tocsr()

    flux_B = np.array(AB*blueSpec.flux).ravel()
    flux_R = np.array(AR*redSpec.flux).ravel()

    # Two sparse diagonal matrices
    diag_B = sp.dia_matrix(([blueSpec.fluxvar], [0]), shape=[blueNAXIS1, blueNAXIS1])
    diag_R = sp.dia_matrix(([redSpec.fluxvar], [0]), shape=[redNAXIS1, redNAXIS1])

    fluxvar_B = np.array((AB*diag_B*AB.T).sum(axis=1)).ravel()
    fluxvar_R = np.array((AR*diag_R*AR.T).sum(axis=1)).ravel()

    buffer=10.

    # Should check for wavelngth overlap
    
    blueOnly=np.where(wl <= redSpec.minWL+buffer)
    overlap=np.where((wl < blueSpec.maxWL-buffer) & (wl > redSpec.minWL+buffer))
    redOnly=np.where(wl >= blueSpec.maxWL-buffer)

    if redSpec.minWL > blueSpec.maxWL:
        print("WARNING: No spectral overlap")

    # Average the two taking into account the buffer region and weighting

    flux=np.zeros(len(flux_B),float)
    fluxVar=np.zeros(len(flux_B),float)
    
    flux[blueOnly]=flux_B[blueOnly]
    fluxVar[blueOnly]=fluxvar_B[blueOnly]

    fluxVar[overlap]=1.0 / (1.0/fluxvar_B[overlap] + 1.0/fluxvar_R[overlap])
    flux[overlap]=(flux_B[overlap]/fluxvar_B[overlap]+flux_R[overlap]/fluxvar_R[overlap]) * fluxVar[overlap]
    
    flux[redOnly]=flux_R[redOnly]
    fluxVar[redOnly]=fluxvar_R[redOnly]

    return flux,fluxVar
    
def get_full_path(path):
    """If required, return to the full path"""

    if '$' in path:
        rootDir=os.environ[path[path.index('$')+1:path.index('/')]]
        return rootDir+path[path.index('/'):]
    else:
        return path

def main(args):
    """
    The main routine
    """

    # Create to instances of SingleSpec

    blueSpec=SingleSpec(args.blueArm)
    redSpec=SingleSpec(args.redArm)

    # Join the spectra
    flux, fluxVar = joinSpectra(blueSpec, redSpec, args)
    
    # Write out the results
    # Use the header in red arm to start with 
    # Add additional blue CCD keywords as required - pending
    hdulist=fits.HDUList(fits.PrimaryHDU())
    hdulist[0].data=flux
    hdulist[0].header=redSpec.header
    hdulist[0].header['CRPIX1']=blueSpec.header['CRPIX1']
    hdulist[0].header['CRVAL1']=blueSpec.header['CRVAL1']
    hdulist[0].header['CDELT1']=blueSpec.header['CDELT1']
    hdulist[0].header['CTYPE1']='wavelength'
    hdulist[0].header['CUNIT1']='angstrom'

    hdr_fluxvar=fits.Header()
    hdr_fluxvar['EXTNAME']='VARIANCE'
    hdr_fluxvar['CRPIX1']=blueSpec.header['CRPIX1']
    hdr_fluxvar['CRVAL1']=blueSpec.header['CRVAL1']
    hdr_fluxvar['CDELT1']=blueSpec.header['CDELT1']
    hdr_fluxvar['CTYPE1']='wavelength'
    hdr_fluxvar['CUNIT1']='angstrom'
    hdr_fluxvar['BUNIT']="(count / Angstrom)^2"

    hdu_fluxvar=fits.ImageHDU(data=fluxVar,header=hdr_fluxvar)
    hdulist.append(hdu_fluxvar)

    # Create the directory where the splice data is saved
    # The 's' stands for spliced
    DEbass.makeDir('reduc_s')

    output=args.blueArm.replace('reduc_b/','reduc_s/').replace('Blue','Splice')
    
    hdulist.writeto(output,overwrite=True)
    hdulist.close()


    
    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Coadd single-object spectra')


    parser.add_argument('--redArm', dest='redArm',
                        default=None,
                        help='Red arm of WiFeS')

    parser.add_argument('--blueArm', dest='blueArm',
                        default=None,
                        help='Red arm of WiFeS')

    parser.add_argument('--noWeighting', dest='noWeighting',
                        action='store_true', default=False,
                        help='Weight spectra')

    parser.add_argument('--scale', dest='scale',
                        action='store_true', default=False,
                        help='Scale spectra')

    args = parser.parse_args()

    # Need to add some error checking

    if args.redArm is None:
        args.redArm="reduc_r/%s" % (args.blueArm.replace('T2m3wb','T2m3wr'))
    else:
        args.redArm="reduc_r/%s" % (args.redArm)

    args.blueArm="reduc_b/%s" % (args.blueArm)

    main(args)

