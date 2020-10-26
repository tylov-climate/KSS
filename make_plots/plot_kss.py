# ------------------------------------------------------------------------
# kss_plots.py
# ------------------------------------------------------------------------
# Copyright (c) 2020
#   Tyge Løvset, tylo@norceresearch.no
#
# NORCE Climate
# https://www.norceresearch.no/en/research-area/klima
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------------------


#!/usr/bin/env python
import os
import numpy as np
import pandas as pd
import netCDF4 as nc4
import platform
import matplotlib.pyplot as plt
import seaborn as sns
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cpf


markers = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']

def facetgrid_diff(df, season='ANN'):
    markers = ['v', 'o']
    #sns.set_style('whitegrid')
    sns.set(style='ticks')
    df = df[df.Season == season]
    df = df[df.Experiment != 'historical']
    g = sns.FacetGrid(df, col='Experiment',
                          row='Period', row_order=('2071-2100', '2031-2060'),
                          hue='Previous Study', palette='bright', height=5, aspect=1.0,
                          legend_out=True, despine=False, sharex=False, sharey=False) #
    g.fig.suptitle('Nedbør- og temperatur-endring: %s' % season, fontsize=16, y=0.98)
    g.map(scatterplot_func, 'TAS diff', 'PR diff', 'Full Model') # , markers=markers, style='Previous Study')
    g.fig.subplots_adjust(top=0.90, wspace=0.2)
    g.set_axis_labels('Temperaturendring [°C]', 'Nedbørsendring [%]')
    g.add_legend()
    if not os.path.isdir('../plots'):
        os.makedirs('../plots')
    g.savefig('../plots/facet_plot_diff_%s.png' % season)


def facetgrid_abs(df, season='ANN'):
    df = df[df.Season == season]
    df = df[df.Experiment != 'historical']
    g = sns.FacetGrid(df, col='Experiment',
                          row='Period', row_order=('2071-2100', '2031-2060'),
                          hue='Previous Study', palette='bright', height=4.8, aspect=1.2,
                          legend_out=True, despine=False, sharex=False, sharey=False) #
    #g.map_dataframe(sns.scatterplot, x='TAS celsius', y='PR mm.year') # , markers=markers, style='Experiment')
    g.map(scatterplot_func, 'TAS celsius', 'PR mm.year', 'Full Model') # , markers=markers, style='Previous Study')
    #g.map(scatterplot_func, 'TAS diff', 'PR diff', 'Full Model') # , markers=markers, style='Previous Study')
    g.fig.subplots_adjust(top=0.92, left=0.04, bottom=0.07)
    g.fig.suptitle('Nedbør og temperatur for fastlands-norge %s (absoluttverdier)' % season, fontsize=16, y=0.98)
    g.set_axis_labels('Temperatur [°C]', 'Nedbør [mm/år]')
    sns.set_style('whitegrid')
    #sns.set(style='ticks')
    g.add_legend()
    #g.set(ylim=(570, 1620), xlim=(-11, 18)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    if not os.path.isdir('../plots'):
        os.makedirs('../plots')
    g.savefig('../plots/facet_plot_abs_%s.png' % season)

'''
def facetgrid_abs2(df, season='ANN'):
    df = df[df.Season != 'ANN']
    #df = df[df.Experiment != 'rcp26']
    #df = df[df.Experiment != 'rcp85']
    sns.set(style='ticks')
    g = sns.FacetGrid(df, col='Season', col_order= ('ANN',), # 'JJA', 'SON'),
                          row='Period', row_order=('2071-2100', '2031-2060', '1951-2000'),
                          hue='Previous Study', palette='bright', height=3.2, aspect=2.5) # 1.35)
    #g.map_dataframe(sns.scatterplot, x='TAS celsius', y='PR mm.year') # , markers=markers, style='Experiment')
    g.map(scatterplot_func, 'TAS celsius', 'PR mm.year', 'Full Model') # , markers=markers, style='Previous Study')
    #g.map(scatterplot_func, 'TAS diff', 'PR diff', 'Full Model') # , markers=markers, style='Previous Study')
    g.fig.subplots_adjust(top=0.92, left=0.04, bottom=0.07)
    g.fig.suptitle('Nedbør og temperatur for fastlands-norge (absoluttverdier)', fontsize=16, y=0.98)
    g.set_axis_labels('Temperatur [°C]', 'Nedbør [mm/år]')
    g.add_legend()
    #g.set(ylim=(570, 1620), xlim=(-11, 18)) # , xticks=[10, 30, 50], yticks=[2, 6, 10])
    g.savefig('../plots/facet_plot_abs2.png')
'''

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


def test():
    sns.set(style='ticks')
    exercise = sns.load_dataset('exercise')
    print(exercise)
    df1 = exercise.groupby(['time','kind'])['pulse'].agg(['mean', 'std']).reset_index()
    print (df1)
    #g = sns.factorplot(x='time', y='pulse', hue='kind', data=exercise)
    df2 = None
    df['TAS diff'] = df1['TAS celsius'] - df1['A'].map(df2.set_index('A')['B'])




#norway_rotated_pole = (-6.595, 4.735, 7.535, 20.625) # lon - lat

period = ('1951-2000', '2031-2060', '2071-2100')
season_map = {'ANN': 0, 'MAM': 1, 'JJA': 2, 'SON': 3, 'DJF': 4}

def test_sample():
    data_file_tas = '%s_yseasmean_%s_%s/%s_EUR-11_CNRM_CNRM-CERFACS-CNRM-CM5_%s_r1i1p1_ALADIN63_v2_yseasmean_v20190828_%s.nc' % \
                ('tas', '2031-2060', 'rcp45', 'tas', 'rcp45', '2031-2060')
    data_file_pr = '%s_yseasmean_%s_%s/%s_EUR-11_CNRM_CNRM-CERFACS-CNRM-CM5_%s_r1i1p1_ALADIN63_v2_yseasmean_v20190828_%s.nc' % \
                ('pr', '2031-2060', 'rcp45', 'pr', 'rcp45', '2031-2060')

    # load NetCDF file into variable
    fpath = 'yseas%s_%s_%s_ens%s' % (args.type, period[args.years], args.rcp, args.type)
    tas_file = args.indir + '/ens%s/tas_%s.nc' % (args.type, fpath)
    pr_file = args.indir + '/ens%s/pr_%s.nc' % (args.type, fpath)
    nc_tas = nc4.Dataset(tas_file)
    nc_pr = nc4.Dataset(pr_file)
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


def geo_plot(season):
    nc_tas, nc_pr = test_sample()
    tas = nc_tas.variables['tas']
    pr = nc_pr.variables['pr']
    rlat = nc_tas.variables['rlat'][:]
    rlon = nc_tas.variables['rlon'][:]

    fig = plt.figure(figsize=(14, 9))

    s = season_map[season]
    tas_data = np.swapaxes(tas, 0, 1).mean(axis=1) if s == 0 else tas[s, :, :]
    pr_data = np.swapaxes(pr, 0, 1).mean(axis=1) if s == 0 else pr[s, :, :]

    plot_var(rlat, rlon, tas_data, fig, (1, 2, 1), type=1)
    plot_var(rlat, rlon, pr_data, fig, (1, 2, 2), type=1)
    plt.show()


uname = platform.uname()[1]
if '-tos' in uname: # NIRD or similar
    inroot = '/tos-project4/NS9076K/data/cordex-norway/stats_v3'
elif uname == 'CMR-PC-158': # Work
    inroot = 'D:/Data/EUR-11_norway/stats_v3'
else: # home
    inroot = 'C:/Dev/DATA/cordex-norway/stats_v3'

def get_args():
    import argparse

    parser = argparse.ArgumentParser()
    print('kss_plot - make plots for KSS Klima 2100')
    print('')

    parser.add_argument(
        '-i', '--indir', default=inroot,
        help='Input file directory'
    )
    parser.add_argument(
        '-o', '--outdir', default='../plots',
        help='Output file directory'
    )
    parser.add_argument(
        '-s', '--season', default='ANN',
        help='Season to be plotted (ANN=default, MAM, JJA, SON, DJF)'
    )
    parser.add_argument(
        '-y', '--years', default=0,
        help='Year period (0=default: 1951-200, 1: 2031-2060, 2: 2071-2100)'
    )
    parser.add_argument(
        '-v', '--var', default='tas',
        help='Variable (tas=default, pr)'
    )
    parser.add_argument(
        '-m', '--model', default='',
        help='Model ()'
    )
    parser.add_argument(
        '--rcp', default='histo',
        help='RCP (histo=default, rcp26, rpc45, rpc85)'
    )
    parser.add_argument(
        '-t', '--type', default='mean',
        help='Type of statistics (mean=default, std)'
    )
    parser.add_argument(
        '-p', '--plot', required=True,
        help='Plot type: (diff, abs, geo)'
    )
    args = parser.parse_args()
    return args


### MAIN ###

if __name__ == '__main__':
    args = get_args()

    # Read dataset
    df = pd.read_csv('yseas%s_kss.csv' % args.type, index_col=0, sep=';')

    # Add full model column:
    models = df[df.columns[4:7]].apply(
        lambda x: '_'.join(x.dropna().astype(str)),
        axis=1
    )
    df['Full Model'] = models

    if args.plot == 'geo':
        geo_plot(args.season)
    elif args.plot == 'abs':
        #sns.set_style('whitegrid')
        #sns.set_style('whitegrid', {'axes.grid' : True,'axes.edgecolor':'none'})
        #sns.set(style='ticks')
        facetgrid_abs(df, args.season)
    elif args.plot == 'diff':
        facetgrid_diff(df, args.season)
    plt.show()

