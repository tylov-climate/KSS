import numpy as np
#import pandas as pd
import netCDF4 as nc4
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def load_mask():
    img = mpimg.imread('norway_mask.png')
    img = img[:,:,0] > 0.5
    return np.flip(img, axis=0)


def main():
    mask_img = load_mask()

    name = 'tas_EUR-11_KNMI_MPI-ESM1-2-HR_historical_r1i1p1f1_RACMO23E_v1-r1_yseasmean_v00000000_1985-2014.nc'
    with nc4.Dataset(name, 'r+') as dset:
        data = dset.variables['tas'][:] # season 0
        print(data[0,50])
        print(mask_img[50])
        print('')
        #... your changes ...
        data2 = np.ma.masked_array(data[0], mask=mask_img).filled(np.nan) # Mask is with Norway shape file.
        data[0, :] = data2
        #print(data2[0,50])
        print(data[0, 51, :])
        dset.variables['tas'][:] = data


main()
