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
#periods = ('1951-2000', '2031-2060', '2071-2100')
periods = ((1971, 2000), (1991, 2020), (2041, 2070), (2071, 2100)) # MIX CMIPS5, CMIPS6
season_map = {'ANN': 0, 'MAM': 1, 'JJA': 2, 'SON': 3, 'DJF': 4}
norway_rotated_pole = (-6.595, 4.735, 7.535, 20.625) # lon - lat


def catplot1(df):
    df = df[df.Season == args.season]
    df = df[df.Period == periods[period]]
    df = df[df.Experiment == experiment]
    df = df.sort_values('FullModel')
    sns.set(style='whitegrid')
    g = sns.catplot(data=df, orient='h', x=variable, y='Model', col='Model Id', kind='bar', col_wrap=4,
                    sharex=False, aspect=1.6, height=2.4)
    for ax in g.axes.flatten():
        #ax.set_yticklabels(ax.get_yticklabels(), fontsize=8)
        ax.set_xticklabels(ax.get_xticks(), fontsize=10)
    g.add_legend()
    plt.tight_layout()
    if args.save:
        save_plot(g, "catplot1", variable)
       

def catplot2(df):
    df = df[df.Season == args.season]
    df = df[df.Period == periods[period]]
    df = df[df.Experiment == experiment]
    df = df.sort_values('FullModel')
    sns.set(style='whitegrid')
    g = sns.catplot(data=df, orient='h', x=variable, y='Model Id', col='Model', kind='bar', col_wrap=4,
                    sharex=False, aspect=0.8, height=4.8)
    for ax in g.axes.flatten():
        #ax.set_yticklabels(ax.get_yticklabels(), fontsize=8)
        ax.set_xticklabels(ax.get_xticks(), fontsize=10)
    g.add_legend()
    if variable.startswith('TAS'):
        tit = "Temperaturendring [°C]" if variable == "TAS diff" else "Temperatur [°C]"
    else:
        tit = "Nedbørsendring [%]" if variable == "PR diff" else "Nedbør [mm/år]"
    g.fig.suptitle('Euro-CORDEX 11: %s, sesong: %s, %s, %s' % (tit, args.season, periods[period], experiment), fontsize=16, y=0.98)
    plt.tight_layout()
    if args.save:
        save_plot(g, "catplot2", variable)


def barplot(df):
    df = df[df.Season == args.season]
    print(df)
    print(periods[period], experiment)
    #exit()
    #df = df[df.Period == periods[period]]

    df = df[df.Experiment == experiment]
    df = df.sort_values('FullModel')


    sns.set(style='whitegrid')
    sns.set(rc={'figure.figsize':(11, 9.6)})
    ax = sns.barplot(data=df, x=variable, y='FullModel') # orient='h'
    ax.set_xlabel('Variabel ' + variable + ': Sesong ' + args.season + ', ' + periods[period] + ', scenario ' + experiment) #, fontsize=12)
    if args.overlaps:
        ax.set_ylabel('Euro-CORDEX 11: Utvalgte klimamodeller med 3 scenarioer')
    else:
        ax.set_ylabel('Euro-CORDEX 11: Alle klimamodeller')
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=6)
    ax.set_xticklabels(ax.get_xticks(), fontsize=10)
    plt.tight_layout()
    if args.save:
        save_plot(ax.get_figure(), "barplot", variable)


def grid_scatterplot_diff(df):
    global periods
    #sns.set_style('whitegrid')
    sns.set(style='ticks')
    df = df[df.Season == args.season]
    df = df[df.Period == periods[period]]
    df = df[df.Experiment != 'historical']
    g = sns.FacetGrid(df, col='Experiment',
                          row='Period',
                          hue='Model', palette='bright', height=9.6, aspect=0.6,
                          legend_out=False, sharex=False, sharey=True) # despine=False 
    g.fig.suptitle('Nedbør- og temperatur-endring, sesong: %s' % args.season, fontsize=16, y=0.98)
    g.map(scatterplot_func, 'TAS diff', 'PR diff', 'Model Id') # , markers=markers) #, style='Model Id')
    g.fig.subplots_adjust(top=0.91, left=0.04, bottom=0.07, wspace=0.1, hspace=1.5)
    g.set_axis_labels('Temperaturendring [°C]', 'Nedbørsendring [%]')
    g.add_legend()
    if args.save:
        save_plot(g, 'scatterplot_diff')


def grid_scatterplot_abs(df):
    df = df[df.Season == args.season]
    df = df[df.Period == periods[period]]
    sns.set(style='ticks')
    g = sns.FacetGrid(df, col='Experiment',
                          row='Period',
                          hue='Model', palette='bright', height=9.6, aspect=0.6,
                          legend_out=False, despine=True, sharex=False, sharey=True)
    #g.map_dataframe(sns.scatterplot, x='TAS celsius', y='PR mm.year')
    g.map(scatterplot_func, 'TAS celsius', 'PR mm.year', 'Model Id') # , markers=markers, style='Previous Study')
    g.fig.subplots_adjust(top=0.91, left=0.05, bottom=0.07, wspace=0.1, hspace=1.5)
    g.fig.suptitle('Absolutt nedbør og temperatur for fastlands-norge, sesong: %s' % args.season, fontsize=16, y=0.98)
    g.set_axis_labels('Temperatur [°C]', 'Nedbør [mm/år]')
    g.add_legend()
    if args.save:
        save_plot(g, 'scatterplot_abs')


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
    plt.scatter(x=xmd[1], y=ymd[2], color=c, marker='v', s=60) # Plot median
    plt.scatter(x=xm, y=ym, color=c, marker='X', s=60)         # Plot average
    ax = sns.scatterplot(x=x, y=y, s=30, marker='o', **kwargs)     # Plot as r'o'und
    #ax.axhline(ym, alpha=0.1, color='black')
    #ax.axvline(xm, alpha=0.1, color='black')

    # Print the model names
    for i in list:
        p = style.iloc[i].split('_', 2)
        s = '-'.join(p[0].split('-')[:2] + p[1:])
        ax.text(xa[i], ya[i], s, size='small') # , horizontalalignment='center', size='medium', color='black', weight='semibold')



def geoplot():
    global periods, season_map
    varname = 'tas' if variable == 'TAS diff' or variable == 'TAS celsius' else 'pr'
    nc_data = geoplot_load(varname, not args.abs)
    nc_var = nc_data.variables[varname]
    rlat = nc_data.variables['rlat'][:]
    rlon = nc_data.variables['rlon'][:]

    fig = plt.figure(figsize=(16, 9.6), constrained_layout=False)

    # ANN: 0, 'MAM': 1, 'JJA': 2, 'SON': 3, 'DJF': 4
    data = [np.swapaxes(nc_var, 0, 1).mean(axis=1), nc_var[0, :, :], nc_var[1, :, :], nc_var[2, :, :], nc_var[3, :, :]]

    #fig.text(0.5, 0.04, 'common xlabel', ha='center', va='center')
    #fig.text(0.06, 0.5, 'common ylabel', ha='center', va='center', rotation='vertical')

    gs = fig.add_gridspec(1, 2)
    gs01 = gs[1].subgridspec(2, 2)
    points = geoplot_sub(rlat, rlon, data[0], fig, gs[0], "Gjennomsnitt for året")
    plt.colorbar(points)
    geoplot_sub(rlat, rlon, data[1], fig, gs01[0], "Sesong: MAM")
    geoplot_sub(rlat, rlon, data[2], fig, gs01[1], "Sesong: JJA")
    geoplot_sub(rlat, rlon, data[3], fig, gs01[2], "Sesong: SON")
    geoplot_sub(rlat, rlon, data[4], fig, gs01[3], "Sesong: DJF")
    if variable.startswith('TAS'):
        tit = "Temperaturendring [°C]" if variable == "TAS diff" else "Temperatur [°C]"
    else:
        tit = "Nedbørsendring [%]" if variable == "PR diff" else "Nedbør [mm/år]"
    fig.suptitle('Euro-CORDEX 11: %s (%s) i perioden %s, scenario %s' % (tit, variable, periods[period], experiment), fontsize=16, y=0.98)
    plt.subplots_adjust(top=0.91, left=0.04, bottom=0.07, wspace=0.08, hspace=0.08)
    
    #plt.tight_layout()
    if args.save:
        save_plot(fig, 'geoplot', variable)


def geoplot_load(varname, diff=True):
    # load NetCDF file into variable
    fpath = 'yseas%s_%s_%s_ens%s' % (args.stat, periods[period], experiment, args.stat)
    if diff:
        file = args.indir + '/ensdiff/%s_%s_diff.nc' % (varname, fpath)
    else:
        file = args.indir + '/ens%s/%s_%s.nc' % (args.stat, varname, fpath)
    print(file)
    nc_data = nc4.Dataset(file)
    return nc_data

def geoplot_sub(rlat, rlon, var, fig, pos, title, type=1, res=30):
    rotated_pole = ccrs.RotatedPole(pole_longitude=-162.0, pole_latitude=39.25)
    ax = fig.add_subplot(pos, projection=rotated_pole)
    ax.add_feature(cpf.OCEAN)
    ax.add_feature(cpf.COASTLINE)
    ax.add_feature(cpf.BORDERS, linestyle=':')
    ax.set_title(title)

    if type == 1:
        res = plt.contourf(rlon, rlat, var, res, transform=rotated_pole)
    if type == 2:
        ax.set_extent(norway_rotated_pole, crs=rotated_pole)
        res = plt.pcolormesh(rlon, rlat, var, transform=rotated_pole)
    return res


def save_plot(g, plotname, varname=''):
    global period, experiment
    varname = varname.replace(' ', '-')
    os.makedirs(args.outdir, exist_ok=True)
    overlaps = '_overlaps' if args.overlaps else ''
    g.savefig('%s/eur11_%s%s_%s_period%d_%s_%s.png' % (args.outdir, plotname, overlaps, varname, period, args.season, experiment))


#def test_groupby():
#    sns.set(style='ticks')
#    exercise = sns.load_dataset('exercise')
#    print(exercise)
#    df1 = exercise.groupby(['time','kind'])['pulse'].agg(['mean', 'std']).reset_index()
#    print (df1)
#    #g = sns.factorplot(x='time', y='pulse', hue='kind', data=exercise)
#    df2 = None
#    df['TAS diff'] = df1['TAS celsius'] - df1['A'].map(df2.set_index('A')['B'])


uname = platform.uname()[1]
if '-tos' in uname: # NIRD or similar
    inroot = '/tos-project4/NS9076K/data/cordex-norway/stats_v3'
elif 'ppi-ext' in uname: # met.no
    inroot = '/lustre/storeC-ext/users/kin2100/NORCE/NIRD_bkp/cordex-norway/stats_v3'
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
        help='Plot (bar, cat1, cat2, geo, scatter)'
    )
    parser.add_argument(
        '-a', '--abs', action='store_true',
        help='Absolute values instead of differences'
    )
    parser.add_argument(
        '-t', '--period', default=1,
        help='Time period (0: 1971-2000, 1: 1991-2020, 2: 2031-2060=default, 3: 2071-2100)'
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
    variable = args.var
    if args.abs:
        if args.var == "TAS diff": variable = 'TAS celsius'
        if args.var == "PR diff": variable = 'PR mm.year'

    csvfile = args.csvfile if args.csvfile else 'yseas%s_kss%s.csv' % (args.stat, overlaps)
    print(csvfile)

    # Read dataset
    df = pd.read_csv(csvfile, index_col=0, sep=';')

    # Add full model column: join 
    models = df[df.columns[4:7]].apply(
        lambda x: '_'.join(x.dropna().astype(str)),
        axis=1
    )

    df['FullModel'] = models
    df = df[df.FullModel != 'MIROC-MIROC5_WRF361H_r1i1p1']

    if args.plot == 'bar':
        barplot(df)
    elif args.plot == 'cat1':
        catplot1(df)
    elif args.plot == 'cat2':
        catplot2(df)
    elif args.plot == 'geo':
        geoplot()
    elif args.plot == 'scatter':
        #sns.set_style('whitegrid')
        #sns.set_style('whitegrid', {'axes.grid' : True,'axes.edgecolor':'none'})
        #sns.set(style='ticks')
        if args.abs:
            grid_scatterplot_abs(df)
        else:
            grid_scatterplot_diff(df)
    
    if not args.save:
        plt.show()
