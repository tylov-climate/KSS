import numpy as np
#import pandas as pd
import netCDF4 as nc4
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def load_mask():
    img = mpimg.imread('norway_mask.png')
    img = img[:,:,0] > 0.5
    return img

def main():
    mask_img = load_mask()
    mask_img = np.flip(mask_img, axis=0)

    dset = nc4.Dataset('tas_yseasmean_2071-2100_rcp85_ensmean.nc','r+')
    data = dset.variables['tas'][:] # season 0
    print(data[0,50])
    print(mask_img[50])
    #... your changes ...
    data2 = np.ma.masked_array(data[0], mask=mask_img).filled(np.nan) # Mask is with Norway shape file.
    data[0,:] = data2
    #print(data2[0,50])
    print(data[0, 51, :])
    dset.variables['tas'][:] = data
    #print(data[50, :])
    dset.close()
main()