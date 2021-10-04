#!/usr/bin/env python

"""
DEbass -- Extracting data from PyFiWeS cubes
"""

import astropy.io.fits as fits
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from matplotlib.patches import Rectangle
import DEbass_Library as DEbass

# Globals 

version_tag = "v01"
start = [None, None]
end = [None, None]

# v01 - Modified version Harry's extract.py code

def aveImage(*datacubes):
    '''
    Averages a data cube over all wavelengths to produce 2D image

    Parameters
    ----------
    *datacubes  :   (List of 3D np.array) 
                    Science spaxels to image

    Returns
    -------
    ave :   (2D np.array) 
            Image of science data
    '''

    #Set total = 0 for array in size of image
    total = np.zeros_like(datacubes[0][0])

    #For each data cube to average
    for cube in datacubes:
        #Assert dimensions are correct
        assert(cube.shape[1] == total.shape[0])
        assert(cube.shape[2] == total.shape[1])

        #Average the flux across wavelength axis
        ave = np.nanmean(cube, axis=0)

        #Add to total
        total = np.add(total, ave)

    #Make it an average instead of total count
    ave = np.divide(total, len(datacubes))

    return ave

#Get user selection from mouse positions
def line_select_callback(eclick, erelease):
	start[:] = eclick.xdata, eclick.ydata
	end[:] = erelease.xdata, erelease.ydata


#Close plot when button pressed
def toggle_selector(event):
	if event.key in ['enter', ' '] and toggle_selector.RS.active:
		# print('Selection Made')
		plt.close()


#Show plot for user selections
def select_spaxel(data, rect=None, width=1, height=1, title=''):
	#Set sensible colourmap range based off average values across image
	ave = np.mean(data)
        
	#Clip within an order of mag of average
	data = np.clip(data, ave/5, ave*5)

	#Show image
	fig, ax = plt.subplots()
	ax.imshow(data, origin='lower', extent=[0,25,0,38])
	ax.title.set_text('{}'.format(title))
        
	#Add box showing saved section if section already saved
	if rect != None:
		# print(rect)
		ax.add_patch(Rectangle(rect, width, height, alpha=0.5, color='limegreen'))
	
	# drawtype is 'box' or 'line' or 'none'
	toggle_selector.RS = RectangleSelector(ax, line_select_callback,
					       drawtype='box', useblit=True,
					       button=[1, 1],  # don't use middle button
					       minspanx=5, minspany=5,
					       spancoords='pixels',
					       interactive=True)
        
	plt.connect('key_press_event', toggle_selector)

	plt.show()

	#Save coordinates of selection
	x = {'start':int(np.rint(start[0])), 'end':int(np.rint(end[0]))}
	y = {'start':int(np.rint(start[1])), 'end':int(np.rint(end[1]))}

	plt.close()

	return x,y


def calcFlux(sci, var, obj_x, obj_y, sub_x, sub_y, skySub):
    '''
    Takes in user selected range of spaxels and averages flux for each spaxel per wavelength.
    Subtracts spaxels in another user selected region for sky/host subtraction
    Weights flux values by variance of spaxel (i.e. higher variance = less weight)

    Parameters
    ----------
    sci     :   (3D np.array) 
                Science data cube

    var     :   (3D np.array)
                Variance data cube

    obj_x, :   (dict){'start':(int), 'end':(int)}
    obj_y      Coordinates to average saved spaxels across

    sub_x,  :   (dict){'start':(int), 'end':(int)}
    sub_y       Coordinates to average subtracted spaxels across

    Returns
    -------
    fl :    (2D np.array) 
            Spectrum of selected range
    '''

    #Extracts average spectrum in section to save
    obj_sci = sci[:, obj_y['start']:obj_y['end'], obj_x['start']:obj_x['end']]
    obj_var = var[:, obj_y['start']:obj_y['end'], obj_x['start']:obj_x['end']]

    #Extracts average spectrum in section to subtract
    if skySub:
        sub_sci  = sci[:, sub_y['start']:sub_y['end'], sub_x['start']:sub_x['end']]
        sub_var  = var[:, sub_y['start']:sub_y['end'], sub_x['start']:sub_x['end']]

    #Calculates the weighted average spectrum across selection range
        
        fl = [
            np.average(obj_sci[i], weights=np.reciprocal(obj_var[i])) - 
            np.average(sub_sci[i], weights=np.reciprocal(sub_var[i])) 
            for i in range(obj_sci.shape[0])
            ]

    else:

        fl = [
            np.average(obj_sci[i], weights=np.reciprocal(obj_var[i]))
            for i in range(obj_sci.shape[0])
            ]


    area=(obj_y['end']-obj_y['start'])*(obj_x['end']-obj_x['start'])
    
    return np.array(fl) * area

def calcVar(var, obj_x, obj_y, sub_x, sub_y, skySub):
    '''
    Calculates variance in flux values across selected region

    Parameters
    ----------
    var     :   (3D np.array)
                Variance data cube

    obj_x, :   (dict){'start':(int), 'end':(int)}
    obj_y      Coordinates to average saved spaxels across

    sub_x,  :   (dict){'start':(int), 'end':(int)}
    sub_y       Coordinates to average subtracted spaxels across

    Returns
    -------
    err :   (2D np.array) 
            Added error of spaxels in selected ranges.
    '''
    #Cut out relevant regions
    obj_var = var[:, obj_y['start']:obj_y['end'], obj_x['start']:obj_x['end']]
    obj_err = np.reciprocal(np.sum(np.reciprocal(obj_var), axis=(1,2)))

    if skySub:
        sub_var  = var[:, sub_y['start']:sub_y['end'], sub_x['start']:sub_x['end']]
        sub_err = np.reciprocal(np.sum(np.reciprocal(sub_var), axis=(1,2)))

    #Add errors of two sections and multiply by the area

    area=(obj_y['end']-obj_y['start'])*(obj_x['end']-obj_x['start'])

    if skySub:
        return (obj_err + sub_err) * area
    else:
        return obj_err * area

def writeFITS(sci,var,output,sci_header,var_header):

    hdulist=fits.HDUList(fits.PrimaryHDU())
    hdulist[0].data=sci
    hdulist[0].header=sci_header
    hdulist[0].header['CRPIX1']=1.0
    hdulist[0].header['CRVAL1']=hdulist[0].header['CRVAL3']
    hdulist[0].header['CDELT1']=hdulist[0].header['CDELT3']
    
    hdr_fluxvar=fits.Header()
    hdr_fluxvar=var_header
    hdr_fluxvar['CRPIX1']=1.0
    hdr_fluxvar['CRVAL1']=hdr_fluxvar['CRVAL3']
    hdr_fluxvar['CDELT1']=hdr_fluxvar['CDELT3']
    
    hdu_fluxvar=fits.ImageHDU(data=var,header=var_header)
    hdulist.append(hdu_fluxvar)
    
    hdulist.writeto(output,overwrite=True)
    hdulist.close()
    
    return

def updateHeader(args):

    version=DEbass.getPipelineVersion()
    metaData=DEbass.getMetadataVersion()

    if args.reducedBy is None:
        reducedBy=DEbass.setName()
    else:
        reducedBy=args.reducedBy

    redDate=DEbass.getUTC()
        
    # Update red arm
    red=fits.open(args.redArm,mode='update')
    red[0].header['REDUCBY']=reducedBy
    red[0].header['REDDATE']=redDate
    red[0].header['PIPELINE']=version
    red[0].header['METADATA']=metaData
    red.close()

    # Update blue arm
    blue=fits.open(args.blueArm,mode='update')
    blue[0].header['REDUCBY']=reducedBy
    blue[0].header['REDDATE']=redDate
    blue[0].header['PIPELINE']=version
    blue[0].header['METADATA']=metaData
    blue.close()
    
    return

def main(args):
    # Update the FITS header with inofmrationon who processed the data an with which version
    updateHeader(args)
    
    # Load in the data

    b_sci,b_sci_hdr=fits.getdata(args.blueArm,0,header=True)
    b_var,b_var_hdr=fits.getdata(args.blueArm,1,header=True)
    b_dq,b_dq_hdr=fits.getdata(args.blueArm,1,header=True)

    r_sci,r_sci_hdr=fits.getdata(args.redArm,0,header=True)
    r_var,r_var_hdr=fits.getdata(args.redArm,1,header=True)
    r_dq,r_dq_hdr=fits.getdata(args.redArm,2,header=True)

    # Generate an images for the user to see. We use the red arm
    #ave_image = aveImage(r_sci, b_sci)
    ave_image = aveImage(r_sci)

    obj_x, obj_y = select_spaxel(ave_image, title='Select Object spaxels to coadd',)


    if args.skySub:
        sub_x, sub_y = select_spaxel(ave_image, title='Select sky spaxels to subtract',
                                     rect  = (obj_x['start'], obj_y['start']),
                                     width =  obj_x['end']-obj_x['start'],
                                     height=  obj_y['end']-obj_y['start'],
                                     )
    else:
        sub_x=None
        sub_y=None

    # Calculate spectrum for selected values
    b_fl = calcFlux(b_sci, b_var, obj_x, obj_y, sub_x, sub_y, args.skySub)
    b_var= calcVar(b_var, obj_x, obj_y, sub_x, sub_y, args.skySub)

    r_fl = calcFlux(r_sci, r_var, obj_x, obj_y, sub_x, sub_y, args.skySub)
    r_var= calcVar(r_var, obj_x, obj_y, sub_x, sub_y, args.skySub)


    # Write out the results

    blueOutput=args.blueArm.replace('p11.fits','p12_%s.fits' % (args.suffix))
    redOutput=args.redArm.replace('p11.fits','p12_%s.fits' % (args.suffix))

    writeFITS(b_fl,b_var,blueOutput,b_sci_hdr,b_var_hdr)
    writeFITS(r_fl,r_var,redOutput,r_sci_hdr,r_var_hdr)
    
    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Coadd single-object spectra')


    parser.add_argument('--redArm', dest='redArm',
                        default=None,
                        help='Red arm of WiFeS')

    parser.add_argument('--blueArm', dest='blueArm',
                        default=None,
                        help='Red arm of WiFeS')

    parser.add_argument('--suffix', dest='suffix',
                        default='SN',
                        help='Suffix')

    parser.add_argument('--reducedBy', dest='reducedBy',
                        default=None,
                        help='Person who processed the data')

    parser.add_argument('--aperture', dest='aperture',
                        default=None,
                        help='Pre-defined aperture')

    parser.add_argument('--skySub', dest='skySub',
                        default=False, action='store_true',
                        help='Subtract Sky')
    
    args = parser.parse_args()

    # Need to add some error checking
    # Note that the filenames for the red and blue arms can differ by a second

    if args.redArm is None:
        args.redArm="reduc_r/%s" % (args.blueArm.replace('T2m3wb','T2m3wr'))
    else:
        args.redArm="reduc_r/%s" % (args.redArm)


    args.blueArm="reduc_b/%s" % (args.blueArm)


    main(args)
