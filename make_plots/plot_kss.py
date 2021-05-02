# ------------------------------------------------------------------------
# kss_plots.py
# ------------------------------------------------------------------------
# Copyright (c) 2021
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
periods = ('1951-2000', '2031-2060', '2071-2100')
season_map = {'ANN': 0, 'MAM': 1, 'JJA': 2, 'SON': 3, 'DJF': 4}
#norway_rotated_pole = (-6.595, 4.735, 7.535, 20.625) # lon - lat


def catplot1(df):
    df = df[df.Season == args.season]
    df = df[df.Period == periods[period]]
    df = df[df.Experiment == experiment]
    df = df[df.FullModel != 'MIROC-MIROC5_WRF361H_r1i1p1']
    df = df.sort_values('FullModel')
    sns.set(style='whitegrid')
    g = sns.catplot(data=df, orient='h', x=args.var, y='Model', col='Model Id', kind='bar', col_wrap=4,
                    sharex=False, aspect=1.6, height=2.3)
    for ax in g.axes.flatten():
        #ax.set_yticklabels(ax.get_yticklabels(), fontsize=8)
        ax.set_xticklabels(ax.get_xticks(), fontsize=10)
    g.add_legend()
    plt.tight_layout()
       

def catplot2(df):
    df = df[df.Season == args.season]
    df = df[df.Period == periods[period]]
    df = df[df.Experiment == experiment]
    df = df[df.FullModel != 'MIROC-MIROC5_WRF361H_r1i1p1']
    df = df.sort_values('FullModel')
    sns.set(style='whitegrid')
    g = sns.catplot(data=df, orient='h', x=args.var, y='Model Id', col='Model', kind='bar', col_wrap=4,
                    sharex=False, aspect=0.8, height=4.8)
    for ax in g.axes.flatten():
        #ax.set_yticklabels(ax.get_yticklabels(), fontsize=8)
        ax.set_xticklabels(ax.get_xticks(), fontsize=10)
    g.add_legend()
    plt.tight_layout()


def barplot(df):
    df = df[df.Season == args.season]
    df = df[df.Period == periods[period]]
    df = df[df.Experiment == experiment]
    df = df[df.FullModel != 'MIROC-MIROC5_WRF361H_r1i1p1']
    df = df.sort_values('FullModel')
    sns.set(style='whitegrid')
    sns.set(rc={'figure.figsize':(11, 9.6)})
    ax = sns.barplot(data=df, x=args.var, y='FullModel') # orient='h'
    ax.set_xlabel(args.var + ': ' + args.season + ', ' + periods[period]) #, fontsize=12)
    if args.overlaps:
        ax.set_ylabel('Models with all 3 scenarios. %s' % experiment)
    else:
        ax.set_ylabel('Models, scenario %s' % experiment)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=6)
    ax.set_xticklabels(ax.get_xticks(), fontsize=10)
    plt.tight_layout()


def grid_scatterplot_diff(df):
    global periods
    markers = ['v', 'o']
    #sns.set_style('whitegrid')
    sns.set(style='ticks')
    df = df[df.Season == args.season]
    df = df[df.Period == periods[period]]
    df = df[df.Experiment != 'historical']
    g = sns.FacetGrid(df, col='Experiment',
                          row='Period',
                          hue='Previous Study', palette='bright', height=9.6, aspect=0.6,
                          legend_out=False, sharex=False, sharey=True) # despine=False 
    g.fig.suptitle('Nedbør- og temperatur-endring, sesong: %s' % args.season, fontsize=16, y=0.98)
    g.map(scatterplot_func, 'TAS diff', 'PR diff', 'FullModel') # , markers=markers, style='Previous Study')
    g.fig.subplots_adjust(top=0.91, left=0.04, bottom=0.07, wspace=0.8, hspace=1.5)
    g.set_axis_labels('Temperaturendring [°C]', 'Nedbørsendring [%]')
    g.add_legend()
    if args.save:
        if not os.path.isdir(args.outdir):
            os.makedirs(args.outdir)
        overlaps = '_overlaps' if args.overlaps else ''
        g.savefig('%s/facet_plot_diff_%s%s.png' % (args.outdir, args.season, overlaps))


def grid_scatterplot_abs(df):
    df = df[df.Season == args.season]
    df = df[df.Period == periods[period]]
    sns.set(style='ticks')
    g = sns.FacetGrid(df, col='Experiment',
                          row='Period',
                          hue='Previous Study', palette='bright', height=9.6, aspect=0.6,
                          legend_out=False, despine=True, sharex=False, sharey=True)
    #g.map_dataframe(sns.scatterplot, x='TAS celsius', y='PR mm.year')
    g.map(scatterplot_func, 'TAS celsius', 'PR mm.year', 'FullModel') # , markers=markers, style='Previous Study')
    g.fig.subplots_adjust(top=0.91, left=0.05, bottom=0.07, wspace=0.8, hspace=1.5)
    g.fig.suptitle('Absolutt nedbør og temperatur for fastlands-norge, sesong: %s' % args.season, fontsize=16, y=0.98)
    g.set_axis_labels('Temperatur [°C]', 'Nedbør [mm/år]')
    g.add_legend()
    if args.save:
        if not os.path.isdir(args.outdir):
            os.makedirs(args.outdir)
        overlaps = '_overlaps' if args.overlaps else ''
        g.savefig('%s/facet_plot_abs_%s%s.png' % (args.outdir, args.season, overlaps))


def get_extreme_values(xa, ya):
    k = 2
    sorted = []
    for i in range(len(xa)):
        sorted.append((i, xa[i], ya[i]))

    sorted.sort(key=lambda p: p[1])
    all = [e[0] for e in sorted]
    extremes = all[:k] + all[-k:] # The k most extremes in x-dir
    xmd = sorted[len(all) // 2]   # Median x

    sorted.sort(key=lambda p: p[2])
    all = [e[0] for e in sorted]
    ymd = sorted[len(all) // 2]   # Median y
    extremes = extremes + all[:k] + all[-k:] # Add the k most extremes in y-dir
    return extremes, xmd, ymd, all


def scatterplot_func(x, y, style, **kwargs):
    global args
    xa, ya = x.to_numpy(), y.to_numpy()
    xm, ym = np.mean(xa), np.mean(ya)
    extremes, xmd, ymd, all = get_extreme_values(xa, ya)

    c = kwargs.get('color', 'k')
    if args.overlaps:
        list = all  # plot all names
    elif c[2] != 1.0:
        list = np.unique(np.where(ya == max(ya))) # plot highest precipitation name only
    else:
        #sn = [i for i, s in enumerate(style.iloc) if 'seNorge' in s] # Add seNorge modellen to printed list
        #list = np.concatenate((extremes, sn))
        list = extremes # plot extreme names only

    #print(list, xmd, ymd)
    plt.scatter(x=xmd[1], y=ymd[2], color=c, marker='s', s=60) # Plot median as 's'quare
    plt.scatter(x=xm, y=ym, color=c, marker='D', s=60)         # Plot average as big 'D'iamond
    ax = sns.scatterplot(x=x, y=y, s=25, marker='o', **kwargs)     # Plot average as r'o'und
    ax.axhline(ym, alpha=0.1, color='black')
    ax.axvline(xm, alpha=0.1, color='black')

    # Print the model names
    for i in list:
        p = style.iloc[i].split('_', 2)
        s = '-'.join(p[0].split('-')[:2] + p[1:])
        ax.text(xa[i], ya[i], s, size='small') # , horizontalalignment='center', size='medium', color='black', weight='semibold')


def test_groupby():
    sns.set(style='ticks')
    exercise = sns.load_dataset('exercise')
    print(exercise)
    df1 = exercise.groupby(['time','kind'])['pulse'].agg(['mean', 'std']).reset_index()
    print (df1)
    #g = sns.factorplot(x='time', y='pulse', hue='kind', data=exercise)
    df2 = None
    df['TAS diff'] = df1['TAS celsius'] - df1['A'].map(df2.set_index('A')['B'])


def test_sample():
    data_file_tas = '%s_yseasmean_%s_%s/%s_EUR-11_CNRM_CNRM-CERFACS-CNRM-CM5_%s_r1i1p1_ALADIN63_v2_yseasmean_v20190828_%s.nc' % \
                ('tas', '2031-2060', 'rcp45', 'tas', 'rcp45', '2031-2060')
    data_file_pr = '%s_yseasmean_%s_%s/%s_EUR-11_CNRM_CNRM-CERFACS-CNRM-CM5_%s_r1i1p1_ALADIN63_v2_yseasmean_v20190828_%s.nc' % \
                ('pr', '2031-2060', 'rcp45', 'pr', 'rcp45', '2031-2060')

    # load NetCDF file into variable
    fpath = 'yseas%s_%s_%s_ens%s' % (args.stat, periods[period], 'rcp45', args.stat)
    tas_file = args.indir + '/ens%s/tas_%s.nc' % (args.stat, fpath)
    pr_file = args.indir + '/ens%s/pr_%s.nc' % (args.stat, fpath)
    nc_tas = nc4.Dataset(tas_file)
    nc_pr = nc4.Dataset(pr_file)
    print('loaded')
    return nc_tas, nc_pr


def test_sample():
    data_file_tas = '%s_yseasmean_%s_%s/%s_EUR-11_CNRM_CNRM-CERFACS-CNRM-CM5_%s_r1i1p1_ALADIN63_v2_yseasmean_v20190828_%s.nc' % \
                ('tas', '2031-2060', 'rcp45', 'tas', 'rcp45', '2031-2060')
    data_file_pr = '%s_yseasmean_%s_%s/%s_EUR-11_CNRM_CNRM-CERFACS-CNRM-CM5_%s_r1i1p1_ALADIN63_v2_yseasmean_v20190828_%s.nc' % \
                ('pr', '2031-2060', 'rcp45', 'pr', 'rcp45', '2031-2060')

    # load NetCDF file into variable
    fpath = 'yseas%s_%s_%s_ens%s' % (args.stat, periods[period], 'rcp45', args.stat)
    tas_file = args.indir + '/ens%s/tas_%s.nc' % (args.stat, fpath)
    pr_file = args.indir + '/ens%s/pr_%s.nc' % (args.stat, fpath)
    nc_tas = nc4.Dataset(tas_file)
    nc_pr = nc4.Dataset(pr_file)
    print('loaded')
    return nc_tas, nc_pr


def plot_geo_var(rlat, rlon, var, fig, pos, type=1, res=30):
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


def geoplot():
    global periods, season_map
    nc_tas, nc_pr = test_sample()
    tas = nc_tas.variables['tas']
    pr = nc_pr.variables['pr']
    rlat = nc_tas.variables['rlat'][:]
    rlon = nc_tas.variables['rlon'][:]

    fig = plt.figure(figsize=(14, 9))

    s = season_map[args.season]
    tas_data = np.swapaxes(tas, 0, 1).mean(axis=1) if s == 0 else tas[s, :, :]
    pr_data = np.swapaxes(pr, 0, 1).mean(axis=1) if s == 0 else pr[s, :, :]

    plot_geo_var(rlat, rlon, tas_data, fig, (1, 2, 1), type=1)
    plot_geo_var(rlat, rlon, pr_data, fig, (1, 2, 2), type=1)
    plt.show()


uname = platform.uname()[1]
if '-tos' in uname: # NIRD or similar
    inroot = '/tos-project4/NS9076K/data/cordex-norway/stats_v3'
elif uname == 'CMR-PC-158': # Work
    inroot = 'D:/Data/EUR-11_norway/stats_v3'
else: # home
    inroot = 'C:/Dev/DATA/cordex-norway/stats_v3'
outroot = '../plots'

args = None

def get_args():
    import argparse
    global args

    parser = argparse.ArgumentParser()
    print('kss_plot - make plots for KSS Klima 2100')
    print('')

    parser.add_argument(
        '-p', '--plot', default='bar',
        help='Plot (bar, cat1, cat2, diff, abs, geo)'
    )
    parser.add_argument(
        '-t', '--period', default=1,
        help='Time period (0: 1951-2000, 1: 2031-2060=default, 2: 2071-2100)'
    )

    parser.add_argument(
        '-f', '--csvfile',
        help='Input csv file'
    )
    parser.add_argument(
        '-i', '--indir', default=inroot,
        help='Input file directory'
    )
    parser.add_argument(
        '-o', '--outdir', default=outroot,
        help='Output file directory'
    )

    parser.add_argument(
        '-s', '--season', default='ANN',
        help='Season to be plotted (ANN=default, MAM, JJA, SON, DJF)'
    )
    parser.add_argument(
        '-e', '--experiment', default='rcp85',
        help='Experiment (historical, rcp26, rcp45, rcp85=default)'
    )
    parser.add_argument(
        '-v', '--var', default='TAS diff',
        help='Variable (...)'
    )
    parser.add_argument(
        '-m', '--model', default='',
        help='Model ()'
    )
    parser.add_argument(
        '--stat', default='mean',
        help='Statistics (mean=default, std)'
    )
    parser.add_argument(
        '--save', action='store_true',
        help='Save plot image'
    )
    parser.add_argument(
        '--overlaps', action='store_true',
        help='Input file directory'
    )
    args = parser.parse_args()


### MAIN ###

if __name__ == '__main__':
    get_args()
    overlaps = '_overlaps' if args.overlaps else ''
    period = int(args.period)
    experiment = args.experiment
    if int(args.period) == 0:
        experiment = 'historical'
    elif args.experiment == 'historical':
        period = 0

    csvfile = args.csvfile if args.csvfile else 'yseas%s_kss%s.csv' % (args.stat, overlaps)

    # Read dataset
    df = pd.read_csv(csvfile, index_col=0, sep=';')

    # Add full model column: join 
    models = df[df.columns[4:7]].apply(
        lambda x: '_'.join(x.dropna().astype(str)),
        axis=1
    )
    df['FullModel'] = models

    if args.plot == 'bar':
        barplot(df)
    elif args.plot == 'cat1':
        catplot1(df)
    elif args.plot == 'cat2':
        catplot2(df)
    elif args.plot == 'geo':
        geoplot()
    elif args.plot == 'abs':
        #sns.set_style('whitegrid')
        #sns.set_style('whitegrid', {'axes.grid' : True,'axes.edgecolor':'none'})
        #sns.set(style='ticks')
        grid_scatterplot_abs(df)
    elif args.plot == 'diff':
        grid_scatterplot_diff(df)
    plt.show()
