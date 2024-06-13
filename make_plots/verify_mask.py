import numpy as np
#import pandas as pd
import netCDF4 as nc4
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def load_mask_senorge2018():
    mask = mpimg.imread('norway_mask.png')
    mask = mask[:,:,0] > 0.5
    return np.flip(mask, axis=0)


def load_mask():
    with nc4.Dataset('NorwayMask_EUR11.nc') as src:
        mask = src.variables['Norway'][:]
    return np.logical_not(mask) # invert!


def main():
    mask_img = load_mask()

    name = 'tas_test.nc'

    with nc4.Dataset(name, 'r+') as dset:
        data = dset.variables['tas'][:] # season 0
        #print(data[0,50])
        #print(mask_img[50])
        #print('')
        #... your changes ...
        data2 = np.ma.masked_array(data[0], mask=mask_img) # .filled(np.nan) # Mask is with Norway shape file.
        data[0, :] = data2
        #print(data2[0,50])
        #print(data[0, 51, :])
        dset.variables['tas'][:] = data


main()
