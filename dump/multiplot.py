#!/usr/bin/env python
import os
import numpy as np
import netCDF4 as nc4
import pandas as pd
import datetime as dt

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cpf
import matplotlib.pyplot as plt
import seaborn as sns


norway_plate_carree = (5.684921607269574, 31.682012795900178, 57.73557430824275, 70.93623338069854)
norway_rotated_pole = (-6.595, 4.735, 7.535, 20.625) # lon - lat

data_source = '/tos-project4/NS9076K/data/cordex/output/EUR-11'
#data_root = '/tos-project4/NS9076K/data/cordex-norway/EUR-11'
data_root = 'C:/Dev/DATA/cordex-norway/yseasmean'

data_file_tas = '%s_yseasmean_%s_%s/%s_EUR-11_CNRM_CNRM-CERFACS-CNRM-CM5_%s_r1i1p1_ALADIN63_v2_yseasmean_v20190828_%s.nc' % \
            ('tas', '2031-2060', 'rcp45', 'tas', 'rcp45', '2031-2060')
data_file_pr = '%s_yseasmean_%s_%s/%s_EUR-11_CNRM_CNRM-CERFACS-CNRM-CM5_%s_r1i1p1_ALADIN63_v2_yseasmean_v20190828_%s.nc' % \
            ('pr', '2031-2060', 'rcp45', 'pr', 'rcp45', '2031-2060')


def test_sample():
    # load NetCDF file into variable
    nc_tas = nc4.Dataset(os.path.join(data_root, data_file_tas))
    nc_pr = nc4.Dataset(os.path.join(data_root, data_file_pr))
    print('loaded')
    return nc_tas, nc_pr


def normalize3(nc, name, step):
    step = 0
    var = nc.variables[name][step, :, :] # near surface temperature
    print('got var')
    # means and standard deviation.
    mean = np.mean(var)
    std = np.std(var)
    # normalize step
    var -= mean
    var /= std
    return var


def plot_var(rlat, rlon, var, fig, pos, type=1, res=30):
    rotated_pole = ccrs.RotatedPole(pole_longitude=-162.0, pole_latitude=39.25)
    ax = fig.add_subplot(*pos, projection=rotated_pole)
    ax.set_extent(norway_rotated_pole, crs=rotated_pole)
    ax.add_feature(cpf.OCEAN)
    ax.add_feature(cpf.COASTLINE)
    ax.add_feature(cpf.BORDERS, linestyle=':')
    if type == 1:
        plt.contourf(rlon, rlat, var, res, transform=rotated_pole)
    if type == 2:
        plt.pcolormesh(rlon, rlat, var, transform=rotated_pole)
    return ax


def plot4():
    nc_tas, nc_pr = test_sample()
    #time = nctas.variables['time'][:]
    #lat = nctas.variables['lat'][:]
    #lon = nctas.variables['lon'][:]
    rlat = nc_tas.variables['rlat'][:]
    rlon = nc_tas.variables['rlon'][:]

    fig = plt.figure(figsize=(10, 10))

    poslist = (221, 222, 223, 224)
    i = 0;
    for step in range(0, 365, 92):
        pos = poslist[i]
        tas = normalize3(nc_tas, 'tas', step)
        pr = normalize3(nc_pr, 'pr', step)
        plot_tas_pr(rlat, rlon, tas, pr, step, fig, pos)
        i += 1

    #plt.savefig('plot.png')
    #plot_scatter(nctas, ncpr)
    #plot_region(nctas, ncpr)
    plt.show()


def region_plot(step):
    nc_tas, nc_pr = test_sample()
    tas = nc_tas.variables['tas']
    pr = nc_pr.variables['pr']
    rlat = nc_tas.variables['rlat'][:]
    rlon = nc_tas.variables['rlon'][:]

    fig = plt.figure(figsize=(15, 10))

    plot_var(rlat, rlon, tas[step, :, :], fig, (1, 2, 1), type=1)
    plot_var(rlat, rlon, pr[step, :, :], fig, (1, 2, 2), type=1)
    plt.show()

def regression_plot(step, start_time, stop_time):
    nc_tas, nc_pr = test_sample()
    tas = nc_tas.variables['tas']
    pr = nc_pr.variables['pr']
    rlat = nc_tas.variables['rlat'][:]
    rlon = nc_tas.variables['rlon'][:]
    time = nc_tas.variables['time']

    pix = ((30, 30), (50, 50), (70, 70), (90, 90))
    n = len(pix)
    pos = [3, n, 0]

    t1 = step*7
    t2 = (step + 1)*7
    t3 = (step + 8)*7
    #istart = nc4.date2index(start_time, time, select='nearest')
    #istop = nc4.date2index(stop_time, time, select='nearest')
    #times = nc4.num2date(time[istart:istop], time.units)
    times = nc4.num2date(time[t1:t2], time.units)
    print(times[0], '-', times[-1])

    fig = plt.figure(figsize=(18, 10))
    for i in range(0, n):
        # plot one week pr / tas
        pos[2] = i + 1
        ax = fig.add_subplot(*pos)
        t = tas[t1, pix[i][0], :].flatten()
        p = pr[t1, pix[i][0], :].flatten()
        data = pd.DataFrame({'TAS'})
        sns.regplot(x=t, y=p, fit_reg=True, ax=ax)

        pos[2] = i + 1 + n
        ax = fig.add_subplot(*pos)
        t = tas[t1, :, pix[i][1]].flatten()
        p = pr[t1, :, pix[i][1]].flatten()
        sns.regplot(x=t, y=p, fit_reg=True, ax=ax)

        pos[2] = i + 1 + n*2
        ax = fig.add_subplot(*pos)
        t = tas[t1:t3, pix[i][0], pix[i][1]]
        p = pr[t1:t3, pix[i][0], pix[i][1]]
        sns.regplot(x=t, y=p, fit_reg=True, ax=ax)

    plt.show()


if __name__ == "__main__":

# Extract desired times.


    start = dt.datetime(2016,1,1,0,0,0)
    stop = dt.datetime(2016,1,3,0,0,0)
    #regression_plot(0, start, stop)
    region_plot(0)
    plt.show()
