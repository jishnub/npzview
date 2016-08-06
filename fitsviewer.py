#! /usr/bin/python
from __future__ import division,print_function
import matplotlib.pyplot as plt
from matplotlib import cm as cm,colors as colors
from matplotlib.ticker import MaxNLocator
import sys,os
import pyfits
import numpy as np
import subprocess

def main():
    if len(sys.argv)>1:
        files = sys.argv[1:]
    else:
        print("Usage: python fitsviewer.py <fitsfile>")
        exit()

    max_subplots_per_fig = 6
    nfigs=len(files)//max_subplots_per_fig+1

    for figno in xrange(nfigs):
        fig=plt.figure()
        files_in_plot = files[max_subplots_per_fig*figno:max_subplots_per_fig*(figno+1)]
        invalid_files=[]
        for filename in files_in_plot:
            filetype=subprocess.check_output(['file',filename])
            if not "FITS image data" in filetype:
                invalid_files.append(filename)
        for filename in invalid_files: files_in_plot.remove(filename)

        num_subplots_in_fig = len(files_in_plot)
        for plotno,filename in enumerate(files_in_plot):
            arr = np.atleast_2d(np.squeeze(pyfits.getdata(filename)))
            amin,amax = arr.min(),arr.max()
            cmap = get_appropriate_colormap(amin,amax)
            subplot_geometry = get_subplot_geometry(num_subplots_in_fig,plotno)
            ax=plt.subplot(*subplot_geometry)
            plt.pcolormesh(arr,cmap=cmap)
            plt.xlim(0,arr.shape[1])
            plt.ylim(0,arr.shape[0])
            plt.title(os.path.basename(filename),fontsize=16)
            plt.colorbar(format="%.1E")
            ax.xaxis.set_major_locator(MaxNLocator(4))
            fig.tight_layout()

    plt.show()

def get_subplot_geometry(num_subplots_in_fig,plotno):
    if num_subplots_in_fig<=3:
        return (1,num_subplots_in_fig,plotno+1)
    elif num_subplots_in_fig==4:
        return (2,2,plotno+1)
    elif num_subplots_in_fig<=6:
        return (2,3,plotno+1)

def center_cb_range_around_zero(amin,amax):

    if amax*amin<0:
        vmax = max(abs(amax),abs(amin))
        vmin=-vmax
    else:
        vmax,vmin=amax,amin

    return vmin,vmax

def get_appropriate_colormap(vmin,vmax):

    all_positive_cmap=cm.OrRd
    positive_negative_cmap=cm.RdBu_r
    all_negative_cmap=cm.Blues_r

    if vmax>0 and (vmin*vmax>=0 or -vmin/vmax<2e-2):
        return all_positive_cmap
    elif vmin<0 and (vmin*vmax>=0 or -vmax/vmin<2e-2):
        return all_negative_cmap
    elif vmin*vmax<0:
        midpoint = 1 - vmax/(vmax + abs(vmin))
        orig_cmap=positive_negative_cmap
        return shiftedColorMap(orig_cmap, midpoint=midpoint, name='shifted')
    else:
        return positive_negative_cmap

#~ Shifted colormap from http://stackoverflow.com/questions/7404116/defining-the-midpoint-of-a-colormap-in-matplotlib
def shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
    '''
    Function to offset the "center" of a colormap. Useful for
    data with a negative min and positive max and you want the
    middle of the colormap's dynamic range to be at zero

    Input
    -----
      cmap : The matplotlib colormap to be altered
      start : Offset from lowest point in the colormap's range.
          Defaults to 0.0 (no lower ofset). Should be between
          0.0 and `midpoint`.
      midpoint : The new center of the colormap. Defaults to
          0.5 (no shift). Should be between 0.0 and 1.0. In
          general, this should be  1 - vmax/(vmax + abs(vmin))
          For example if your data range from -15.0 to +5.0 and
          you want the center of the colormap at 0.0, `midpoint`
          should be set to  1 - 5/(5 + 15)) or 0.75
      stop : Offset from highets point in the colormap's range.
          Defaults to 1.0 (no upper ofset). Should be between
          `midpoint` and 1.0.
    '''
    cdict = {
        'red': [],
        'green': [],
        'blue': [],
        'alpha': []
    }

    # regular index to compute the colors
    reg_index = np.linspace(start, stop, 257)

    # shifted index to match the data
    shift_index = np.hstack([
        np.linspace(0.0, midpoint, 128, endpoint=False),
        np.linspace(midpoint, 1.0, 129, endpoint=True)
    ])

    for ri, si in zip(reg_index, shift_index):
        r, g, b, a = cmap(ri)

        cdict['red'].append((si, r, r))
        cdict['green'].append((si, g, g))
        cdict['blue'].append((si, b, b))
        cdict['alpha'].append((si, a, a))

    newcmap = colors.LinearSegmentedColormap(name, cdict)
    plt.register_cmap(cmap=newcmap)

    return newcmap

if __name__=="__main__":
    main()
