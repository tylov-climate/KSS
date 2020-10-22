#!/usr/bin/env python
import os
import numpy as np
import pandas as pd
import netCDF4 as nc4

import matplotlib.pyplot as plt
import seaborn as sns
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cpf


markers = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']

def facetgrid_all(df):
    #df = df[df.Season != 'ANN']
    sns.set(style='ticks')
    g = sns.FacetGrid(df, col='Season', col_order= ('ANN', 'JJA', 'SON'),
                          row='Period', row_order=('2071-2100', '2031-2060', '1951-2000'),
                          hue='Experiment', hue_order=('historical', 'rcp85'), palette='bright', height=3.3, aspect=1.35)
    #g.map_dataframe(sns.scatterplot, x='TAS celsius', y='PR mm.year') # , markers=markers, style='Experiment')
    g.map(scatterplot_func, 'TAS celsius', 'PR mm.year', 'Full Model') # , markers=markers, style='Previous Study')
    #g.map(scatterplot_func, 'TAS diff', 'PR diff', 'Full Model') # , markers=markers, style='Previous Study')
    g.fig.subplots_adjust(top=0.92, left=0.04, bottom=0.07)
    g.fig.suptitle('Nedbør og temperatur for fastlands-norge (absoluttverdier)', fontsize=16, y=0.98)
    g.set_axis_labels('Temperatur [°C]', 'Nedbør [mm/år]')
    g.add_legend()
    #g.set(ylim=(570, 1620), xlim=(-11, 18)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.savefig('facet_plot.png')


def facetgrid_abs(df):
    #df = df[df.Season != 'ANN']
    df = df[df.Experiment != 'rcp26']
    df = df[df.Experiment != 'rcp85']
    sns.set(style='ticks')
    g = sns.FacetGrid(df, col='Season', col_order= ('ANN',), # 'JJA', 'SON'),
                          row='Period', row_order=('2071-2100', '2031-2060', '1951-2000'),
                          hue='Previous Study', palette='bright', height=3.3, aspect=1.35)
    #g.map_dataframe(sns.scatterplot, x='TAS celsius', y='PR mm.year') # , markers=markers, style='Experiment')
    g.map(scatterplot_func, 'TAS celsius', 'PR mm.year', 'Full Model') # , markers=markers, style='Previous Study')
    #g.map(scatterplot_func, 'TAS diff', 'PR diff', 'Full Model') # , markers=markers, style='Previous Study')
    g.fig.subplots_adjust(top=0.92, left=0.04, bottom=0.07)
    g.fig.suptitle('Nedbør og temperatur for fastlands-norge (absoluttverdier)', fontsize=16, y=0.98)
    g.set_axis_labels('Temperatur [°C]', 'Nedbør [mm/år]')
    g.add_legend()
    #g.set(ylim=(570, 1620), xlim=(-11, 18)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.savefig('facet_plot.png')


def scatterplot_func(x, y, style, **kwargs):
    xm, ym = np.mean(x), np.mean(y)
    # Average, big diamond:
    c = kwargs.get('color', 'k')
    plt.scatter(x=xm, y=ym, color=c, marker='D', s=60)
    ax = sns.scatterplot(x, y, s=25, marker='o', **kwargs)
    ax.axhline(ym, alpha=0.1, color='black')
    ax.axvline(xm, alpha=0.1, color='black')
    x = x.to_numpy()
    y = y.to_numpy()
    if c[2] == 1.0:
        list = np.unique((np.where(x == max(x)), np.where(y == max(y)), np.where(x == min(x)), np.where(y == min(y))))
    else:
        list = np.unique(np.where(y == max(y))) # Old models: print high precipitation only
    for i in list:
        p = style.iloc[i].split('_', 2)
        s = '-'.join(p[0].split('-')[:2] + p[1:])
        ax.text(x[i], y[i], s, size='small') # , horizontalalignment='center', size='medium', color='black', weight='semibold')


def facetgrid_differences(df, season='ANN'):
    markers = ['v', 'o']
    #sns.set_style('whitegrid')
    sns.set(style='ticks')
    df = df[df.Season == season]
    df = df[df.Experiment != 'historical']
    g = sns.FacetGrid(df, col='Experiment', row='Period', row_order=('2071-2100', '2031-2060'),
                          hue='Previous Study', palette='bright', height=5, aspect=1.0,
                          legend_out=True, despine=False, sharex=False, sharey=False) #
    g.fig.suptitle('Nedbør- og temperatur-endring: %s' % season, fontsize=16, y=0.98)
    g.map(scatterplot_func, 'TAS diff', 'PR diff', 'Full Model') # , markers=markers, style='Previous Study')
    g.fig.subplots_adjust(top=0.90, wspace=0.2)
    g.set_axis_labels('Temperaturendring [°C]', 'Nedbørsendring [%]')
    g.add_legend()
    g.savefig('facet_plot_%s.png' % season)


def plot2(df):
    df = df[df.Season == 'ANN']
    g = sns.FacetGrid(df, row='Previous Study', col='Period', hue='Experiment', palette='bright') # height=6, aspect=.8
    g.map_dataframe(sns.scatterplot, x='PR mm.year', y='TAS celsius', style='Institute', markers=markers, legend='full')
    g.set_axis_labels('Precipitation mm.', 'Surface temp. C.')
    g.add_legend()
    g.set(xlim=(2, 3.8), ylim=(-3, 9)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    #g.savefig('facet_plot.png')


def test():
    sns.set(style='ticks')
    exercise = sns.load_dataset('exercise')
    print(exercise)
    df1 = exercise.groupby(['time','kind'])['pulse'].agg(['mean', 'std']).reset_index()
    print (df1)
    #g = sns.factorplot(x='time', y='pulse', hue='kind', data=exercise)
    df2 = None
    df['TAS diff'] = df1['TAS celsius'] - df1['A'].map(df2.set_index('A')['B'])




norway_rotated_pole = (-6.595, 4.735, 7.535, 20.625) # lon - lat

data_source = '/tos-project4/NS9076K/data/cordex/output/EUR-11'
#data_root = '/tos-project4/NS9076K/data/cordex-norway/EUR-11'
data_root = 'C:/Dev/DATA/cordex-norway/yseasmean'


def test_sample():
    data_file_tas = '%s_yseasmean_%s_%s/%s_EUR-11_CNRM_CNRM-CERFACS-CNRM-CM5_%s_r1i1p1_ALADIN63_v2_yseasmean_v20190828_%s.nc' % \
                ('tas', '2031-2060', 'rcp45', 'tas', 'rcp45', '2031-2060')
    data_file_pr = '%s_yseasmean_%s_%s/%s_EUR-11_CNRM_CNRM-CERFACS-CNRM-CM5_%s_r1i1p1_ALADIN63_v2_yseasmean_v20190828_%s.nc' % \
                ('pr', '2031-2060', 'rcp45', 'pr', 'rcp45', '2031-2060')

    # load NetCDF file into variable
    nc_tas = nc4.Dataset(os.path.join(data_root, data_file_tas))
    nc_pr = nc4.Dataset(os.path.join(data_root, data_file_pr))
    print('loaded')
    return nc_tas, nc_pr

def plot_var(rlat, rlon, var, fig, pos, type=1, res=30):
    rotated_pole = ccrs.RotatedPole(pole_longitude=-162.0, pole_latitude=39.25)
    ax = fig.add_subplot(*pos, projection=rotated_pole)
    #ax.set_extent(norway_rotated_pole, crs=rotated_pole)
    ax.add_feature(cpf.OCEAN)
    ax.add_feature(cpf.COASTLINE)
    ax.add_feature(cpf.BORDERS, linestyle=':')
    if type == 1:
        plt.contourf(rlon, rlat, var, res, transform=rotated_pole)
    if type == 2:
        plt.pcolormesh(rlon, rlat, var, transform=rotated_pole)
    return ax


def region_plot(step):
    nc_tas, nc_pr = test_sample()
    tas = nc_tas.variables['tas']
    pr = nc_pr.variables['pr']
    rlat = nc_tas.variables['rlat'][:]
    rlon = nc_tas.variables['rlon'][:]

    fig = plt.figure(figsize=(14, 9))

    plot_var(rlat, rlon, tas[step, :, :], fig, (1, 2, 1), type=1)
    plot_var(rlat, rlon, pr[step, :, :], fig, (1, 2, 2), type=1)
    plt.show()



if __name__ == '__main__':
    # Read dataset
    df = pd.read_csv('kss_yseasmean.csv', index_col=0, sep=';')

    # Add full model column:
    models = df[df.columns[4:7]].apply(
        lambda x: '_'.join(x.dropna().astype(str)),
        axis=1
    )
    df['Full Model'] = models

    #region_plot(1)

    #sns.set_style('whitegrid')
    #sns.set_style('whitegrid', {'axes.grid' : True,'axes.edgecolor':'none'})
    #sns.set(style='ticks')
    #facetgrid_all(df)
    #facetgrid_abs(df)

    facetgrid_differences(df, 'ANN')
    '''
    facetgrid_differences(df, 'MAM')
    facetgrid_differences(df, 'JJA')
    facetgrid_differences(df, 'SON')
    facetgrid_differences(df, 'DJF')
    '''
    plt.show()

