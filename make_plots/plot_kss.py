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


def cat1plot(df):
    df = df[df.Årstid == args.season]
    if args.period != None:
        df = df[df.Periode == periods_str[period]]
    df = df[df.Eksperiment == experiment]
    df = df.sort_values('FullModel')
    print(df)
    sns.set(style='whitegrid')
    g = sns.catplot(data=df, orient='h', x=variable, y='Modell', col='Modell Id', kind='bar', col_wrap=4,
                    sharex=False, aspect=1.6, height=2.4)
    for ax in g.axes.flatten():
        #ax.set_yticklabels(ax.get_yticklabels(), fontsize=8)
        ax.set_xticklabels(ax.get_xticks(), fontsize=10)
    g.add_legend()
    if variable.startswith('TAS'):
        tit = 'Temperaturendring [°C]' if variable != 'TAS celsius' else 'Temperatur [°C]'
    else:
        tit = 'Nedbørsendring [%]' if variable != 'PR mm.år' else 'Nedbør [mm/år]'
    g.fig.suptitle('Euro-CORDEX 11: %s, %s, %s, %s' % (tit, season_map2[args.season], periods_str[period], experiment), fontsize=16, y=0.98)
    plt.tight_layout()
    if args.save:
        save_plot(g, 'cat1plot', variable)


def cat2plot(df):
    df = df[df.Årstid == args.season]
    if args.period != None:
        df = df[df.Periode == periods_str[period]]
    df = df[df.Eksperiment == experiment]
    df = df.sort_values('FullModel')
    print(df)
    sns.set(style='whitegrid')
    g = sns.catplot(data=df, orient='h', x=variable, y='Modell Id', col='Modell', kind='bar', col_wrap=4,
                    sharex=False, aspect=0.8, height=4.8)
    for ax in g.axes.flatten():
        #ax.set_yticklabels(ax.get_yticklabels(), fontsize=8)
        ax.set_xticklabels(ax.get_xticks(), fontsize=10)
    g.add_legend()
    if variable.startswith('TAS'):
        tit = 'Temperaturendring [°C]' if variable != 'TAS celsius' else 'Temperatur [°C]'
    else:
        tit = 'Nedbørsendring [%]' if variable != 'PR mm.år' else 'Nedbør [mm/år]'
    g.fig.suptitle('Euro-CORDEX 11: %s, %s, %s, %s' % (tit, season_map2[args.season], periods_str[period], experiment), fontsize=16, y=0.98)
    plt.tight_layout()
    if args.save:
        save_plot(g, 'cat2plot', variable)


def barplot(df):
    df = df[df.Årstid == args.season]
    if args.period != None:
        df = df[df.Periode == periods_str[period]]
    df = df[df.Eksperiment == experiment]
    df = df.sort_values('FullModel')
    print(df)
    sns.set_theme(style='whitegrid')
    sns.set(rc={'figure.figsize':(11, 9.6)})
    ax = sns.barplot(data=df, x=variable, y='FullModel') # orient='h'
    if args.period != None:
        ax.set_xlabel('Periode: ' + periods_str[period] + ', ' + experiment + ', ' +
                      season_map2[args.season] + ', ' + variable) #, fontsize=12)
    else:
        ax.set_xlabel('All periods, ' + experiment + ', ' +
                      season_map2[args.season] + ', ' + variable) #, fontsize=12)

    if args.all:
        ax.set_ylabel('Euro-CORDEX 11: Alle klimamodeller')
        ax.set_yticklabels(ax.get_yticklabels(), fontsize=6)
    else:
        ax.set_ylabel('Euro-CORDEX 11: Utvalgte klimamodeller med 3 scenarioer')
        ax.set_yticklabels(ax.get_yticklabels(), fontsize=8)
    ax.set_xticklabels(ax.get_xticks(), fontsize=10)
    plt.tight_layout()
    if args.save:
        save_plot(ax.get_figure(), 'barplot', variable)


def kde1plot(df):
    # Kernel density estimation
    # https://seaborn.pydata.org/tutorial/distributions.html#kernel-density-estimation
    df = df[df.Årstid == args.season]
    if args.experiment != None:
        df = df[df.Eksperiment == experiment]
    if args.gcm:
        df = df[df.Modell == args.gcm]
    if args.rcm:
        df = df[df['Modell Id'] == args.rcm]
    if args.period != None:
        df = df[df.Periode == periods_str[period]]
    print(df)
    sns.set(rc={'figure.figsize':(30, 25)})
    ax = sns.displot(data=df, x=variable, hue='Periode', kind='kde', fill=True,
                     height=10, aspect=1.5)
    sel = 'utvalgte modeller' if not args.all else 'alle modeller'
    if args.gcm: sel = 'GCM:' + args.gcm
    if args.rcm: sel += '-RCM:' + args.rcm
    if args.period is None:
        tit =  'Alle perioder, ' + experiment + ', ' + sel + ', ' + season_map2[args.season] + '.'
    else:
        tit =  periods_str[period] + ', ' + experiment + ', ' + sel + ', ' + season_map2[args.season] + '.'
    ax.fig.suptitle('Euro-CORDEX 11: ' + tit, fontsize=16, y=0.98)

    #ax.fig.set_dpi(100)
    #wm = plt.get_current_fig_manager()
    #wm.window.state('zoomed')
    #wm.full_screen_toggle()
    #plt.tight_layout()
    if args.save:
        save_plot(ax.fig, 'kde1plot', variable)


def kde2plot(df):
    # Kernel density estimation
    # https://seaborn.pydata.org/tutorial/distributions.html#kernel-density-estimation
    df = df[df.Årstid == args.season]
    if args.experiment != None:
        df = df[df.Eksperiment == experiment]
    if args.period != None:
        df = df[df.Periode == periods_str[period]]
    if args.gcm:
        df = df[df.Modell == args.gcm]
    if args.rcm:
        df = df[df["Modell Id"] == args.rcm]
    print(df.to_string())
    sns.set(rc={'figure.figsize':(30, 25)})
    ax = sns.displot(data=df, x=variable, hue='FullModel', kind='kde', fill=True,
                     height=10, aspect=1.5)
    sel = 'utvalgte modeller' if not args.all else 'alle modeller'
    if args.gcm: sel = 'GCM:' + args.gcm
    if args.rcm: sel += '-RCM:' + args.rcm
    if args.period is None:
        tit =  'Alle perioder, ' + experiment + ', ' + sel + ', ' + season_map2[args.season] + '.'
    else:
        tit =  periods_str[period] + ', ' + experiment + ', ' + sel + ', ' + season_map2[args.season] + '.'

    ax.fig.suptitle('Euro-CORDEX 11: ' + tit, fontsize=16, y=0.98)

    #ax.fig.set_dpi(100)
    #wm = plt.get_current_fig_manager()
    #wm.window.state('zoomed')
    #wm.full_screen_toggle()
    #plt.tight_layout()
    if args.save:
        save_plot(ax.fig, 'kde2plot', variable)


def grid_scatterplot_diff(df):
    #global periods_str
    sns.set_style('whitegrid')
    sns.set(style='ticks')

    df = df[df.Årstid == args.season]
    if args.period != None:
        df = df[df.Periode == periods_str[period]]
    #df = df[df.Eksperiment != 'historical']
    if args.experiment != None:
        df = df[df.Eksperiment == experiment]
    print(df)

    g = sns.FacetGrid(df, col='Eksperiment',
                          row='Periode',
                          hue='Modell', palette='bright', height=9.6, aspect=0.6,
                          legend_out=False, sharex=False, sharey=True) # despine=False
    g.fig.suptitle('Nedbør- og temperatur-endring, fastlands-norge, %s, %s' % (season_map2[args.season], exp_names[args.diff]), fontsize=16, y=0.98)
    g.map(scatterplot_func, 'TAS diff-%s' % exp_names[args.diff], 'PR diff-%s' % exp_names[args.diff], 'Modell Id') # , markers=markers) #, style='Modell Id')
    g.fig.subplots_adjust(top=0.91, left=0.04, bottom=0.07, wspace=0.1, hspace=1.5)
    g.set_axis_labels('Temperaturendring [°C]   ▾ = median, ✕ = gjennomsnitt', 'Nedbørsendring [%]')
    g.add_legend()
    if args.save:
        save_plot(g, 'scatterplot_diff')


def kde_scatterplot_diff(df, df2):
    #global periods_str
    sns.set_style('whitegrid')
    sns.set(style='ticks')

    df = df[df.Årstid == args.season]
    if args.period != None:
        df = df[df.Periode == periods_str[period]]
    if args.experiment != None:
        df = df[df.Eksperiment == experiment]

    df2 = df2[df2.Årstid == args.season]
    if args.period != None:
        df2 = df2[df2.Periode == periods_str[period]]
    if args.experiment != None:
        df2 = df2[df2.Eksperiment == experiment]

    print(df2)


    g = sns.FacetGrid(df, col='Eksperiment',
                          row='Periode',
                          hue='Modell', palette='bright', height=9.6, aspect=0.6,
                          legend_out=False, sharex=False, sharey=True) # despine=False
    g.fig.suptitle('Nedbør- og temperatur-endring, fastlands-norge, %s, %s' % (season_map2[args.season], exp_names[args.diff]), fontsize=16, y=0.98)

    sns.kdeplot(data=df2, x='TAS diff-%s' % exp_names[args.diff], y='PR diff-%s' % exp_names[args.diff], fill=True, palette='bright')

    g.map(scatterplot_func, 'TAS diff-%s' % exp_names[args.diff], 'PR diff-%s' % exp_names[args.diff], 'Modell Id') # , markers=markers) #, style='Modell Id')
    g.fig.subplots_adjust(top=0.91, left=0.04, bottom=0.07, wspace=0.1, hspace=1.5)
    g.set_axis_labels('Temperaturendring [°C]   ▾ = median, ✕ = gjennomsnitt', 'Nedbørsendring [%]')

    g.add_legend()
    if args.save:
        save_plot(g, 'kde_scatterplot_diff')



def grid_scatterplot_abs(df):
    sns.set_style('whitegrid')
    sns.set(style='ticks')

    df = df[df.Årstid == args.season]
    if args.period != None:
        df = df[df.Periode == periods_str[period]]
    if args.experiment != None:
        df = df[df.Eksperiment == experiment]
    print(df)
    sns.set(style='ticks')
    g = sns.FacetGrid(df, col='Eksperiment',
                          row='Periode',
                          hue='Modell', palette='bright', height=9.6, aspect=0.6,
                          legend_out=False, despine=True, sharex=False, sharey=True)
    #g.map_dataframe(sns.scatterplot, x='TAS celsius', y='PR mm.år')
    g.map(scatterplot_func, 'TAS celsius', 'PR mm.år', 'Modell Id') # , markers=markers, style='Previous Study')
    g.fig.subplots_adjust(top=0.91, left=0.05, bottom=0.07, wspace=0.1, hspace=1.5)
    g.fig.suptitle('Absolutt nedbør og temperatur for fastlands-norge, %s' % season_map2[args.season], fontsize=16, y=0.98)
    g.set_axis_labels('Temperatur [°C]   ▾ = median, ✕ = gjennomsnitt', 'Nedbør [mm/år]')
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
    if not args.all:
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
    ax.axhline(ym, alpha=0.1, color='black')
    ax.axvline(xm, alpha=0.1, color='black')

    # Print the model names
    for i in list:
        p = style.iloc[i].split('_', 2)
        s = '-'.join(p[0].split('-')[:2] + p[1:])
        ax.text(xa[i], ya[i], s, size='small') # , horizontalalignment='center', size='medium', color='black', weight='semibold')


def geoplot():
    global periods_str, season_map
    varname = 'tas' if variable.startswith('TAS') else 'pr'
    nc_data = geoplot_load(varname, args.diff)
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
    points = geoplot_sub(rlat, rlon, data[0], fig, gs[0], 'Gjennomsnitt for året')
    plt.colorbar(points)
    geoplot_sub(rlat, rlon, data[1], fig, gs01[0], 'Årstid: mars-mai')
    geoplot_sub(rlat, rlon, data[2], fig, gs01[1], 'Årstid: juni-aug')
    geoplot_sub(rlat, rlon, data[3], fig, gs01[2], 'Årstid: sep-nov')
    geoplot_sub(rlat, rlon, data[4], fig, gs01[3], 'Årstid: des-feb')
    if variable.startswith('TAS'):
        tit = 'Temperaturendring [°C]' if variable != 'TAS celsius' else 'Temperatur [°C]'
    else:
        tit = 'Nedbørsendring [%]' if variable == 'PR mm.år' else 'Nedbør [mm/år]'
    fig.suptitle(f'Euro-CORDEX 11: {tit} ({variable}) i perioden %s, scenario %s' % (tit, variable, periods_str[period], experiment), fontsize=16, y=0.98)
    plt.subplots_adjust(top=0.91, left=0.04, bottom=0.07, wspace=0.08, hspace=0.08)

    #plt.tight_layout()
    if args.save:
        save_plot(fig, 'geoplot', variable)


def geoplot_load(varname, diff):
    # load NetCDF file into variable

    fpath = 'yseas%s_%s_%s_ens%s' % (args.stat, periods_str[period], experiment[:5], args.stat)
    if diff:
        file = inroot + '/ensdiff/%s_%s_diff.nc' % (varname, fpath)
    else:
        file = inroot + '/ens%s/%s_%s.nc' % (args.stat, varname, fpath)
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
    global period, experiment, outfile, figure
    os.makedirs(outroot, exist_ok=True)
    var = args.var if args.var else ''
    #var = varname.replace(' ', '-')
    per = periods_str[period] if args.period else 'allper'
    exp = experiment if args.experiment or args.period else 'allexp'
    gcm = args.gcm if args.gcm else 'allgcm'
    rcm = args.rcm if args.rcm else 'allrcm'
    sel = '_allmod' if args.all else ''
    outfile = f'{plotname}_{var}_{gcm}_{rcm}_{per}_{args.season}_{exp}{sel}.png'
    figure = g
    #full = outroot + '/' + outfile
    #print('save to:', full)
    #print('plots_cmip%s/%s' % (args.cmip, name))
    #g.savefig(full)
    #g.savefig(name)


#def test_groupby():
#    sns.set(style='ticks')
#    exercise = sns.load_dataset('exercise')
#    print(exercise)
#    df1 = exercise.groupby(['time','kind'])['pulse'].agg(['mean', 'std']).reset_index()
#    print (df1)
#    #g = sns.factorplot(x='time', y='pulse', hue='kind', data=exercise)
#    df2 = None
#    df['TAS endring'] = df1['TAS celsius'] - df1['A'].map(df2.set_index('A')['B'])

exp_names = {
    #'histo-0': 'historical_1971-2020',
    'histo-1': 'historical_1971-2000',
    'histo-2': 'historical_1991-2020',
    'rcp45-3': 'rcp45_2041-2070',
    'rcp85-3': 'rcp85_2041-2070',
    'ssp370-3': 'ssp370_2041-2070',
    'rcp45-4': 'rcp45_2071-2100',
    'rcp85-4': 'rcp85_2071-2100',
    'ssp370-4': 'ssp370_2071-2100',
}

def get_args():
    import argparse
    parser = argparse.ArgumentParser()
    print('kss_plot - make plots for KSS Klima 2100')
    print('')

    parser.add_argument(
        '-c', '--cmip', default='6',
        help='CMIP (5, 6=default)'
    )
    parser.add_argument(
        '-P', '--plot', required=False, default='bar',
        help='Plot type (bar=default, scatter, kdediff, kde1, kde2, cat1, cat2, geo)'
    )
    parser.add_argument(
        '-p', '--period', default=None,
        help='Period (%s)' % ', '.join(['%d:%s' % (i+1, periods_str[i]) for i in range(len(periods))])
    )
    parser.add_argument(
        '-e', '--experiment', default=None,
        help='Experiment (historical=default, rcp45, rcp85, ssp370)'
    )
    parser.add_argument(
        '-s', '--season', default='ANN',
        help='Season to be plotted (ANN=default, MAM, JJA, SON, DJF)'
    )
    parser.add_argument(
        '-v', '--var', default='TAS',
        help='Variable (TAS, PR)'
    )
    parser.add_argument(
        '-g', '--gcm', default=None,
        help='GCM name'
    )
    parser.add_argument(
        '-r', '--rcm', default=None,
        help='RCM name'
    )
    parser.add_argument(
        '-a', '--stat', default='mean',
        help='Statistics (mean=default, min, max)'
    )
    parser.add_argument(
        '-d', '--diff', default=None,
        help='Difference to experiment (histo-1, histo-2, '
             'rcp45-3, rcp85-3, ssp370-3, '
             'rcp45-4, rcp85-4, ssp370-4)'
    )
    parser.add_argument(
        '--all', action='store_true',
        help='Plot all, not only a selection of models (cmip5)'
    )

    parser.add_argument(
        '--save', action='store_true',
        help='Save plot image'
    )
    parser.add_argument(
        '-f', '--csvfile',
        help='Input csv file'
    )
    parser.add_argument(
        '-i', '--indir', default=None,
        help='Input file directory'
    )
    parser.add_argument(
        '-o', '--outdir', default=None,
        help='Output file directory'
    )
    return parser.parse_args()


### MAIN ###

markers = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
#periods = ((1971, 2000),                             (2041, 2070), (2071, 2100)) # cmip5
#periods = (              (1985, 2014), (1991, 2020), (2041, 2070), (2071, 2100)) # cmip6
periods  = ((1971, 2000), (1991, 2020), (2041, 2070), (2071, 2100)) # cmip5+cmip6
periods_str = ['%d-%d' % (p[0], p[1]) for p in periods]
season_map = {'ANN': 0, 'MAM': 1, 'JJA': 2, 'SON': 3, 'DJF': 4}
season_map2 = {'ANN': 'årlig', 'MAM': 'mars-mai', 'JJA': 'juni-aug', 'SON': 'sep-nov', 'DJF': 'des-feb'}
norway_rotated_pole = (-6.595, 4.735, 7.535, 20.625) # lon - lat


if __name__ == '__main__':
    args = get_args()

    uname = platform.uname()[1]

    if args.indir != None:
        inroot = args.indir
    if args.outdir != None:
        outroot = args.outdir

    period = args.period
    if period is not None:
        period = int(period) - 1
    experiment = args.experiment
    if experiment is None:
        if period is not None and period >= 2:
            experiment = 'rcp85' if args.cmip == '5' else 'ssp370'
        else:
            experiment = 'historical'
    if period is None:
        if experiment == 'historical':
            period = 0 if args.cmip == '5' else 1
        else:
            period = 3

    print('period', period)

    #selected = '_all' if args.all else ''
    #csvfile = args.csvfile if args.csvfile else 'yseas%s_cmip%s%s.csv' % (args.stat, args.cmip, selected)
    csvfile = args.csvfile
    print(csvfile)

    # Read datasets
    df = pd.read_csv(csvfile, index_col=0, sep=';')
    df2 = pd.read_csv(csvfile[:-4] + '_all.csv', index_col=0, sep=';')
    if args.all:
        df, df2 = df2, df

    if args.diff:
        if args.var == 'TAS':
            variable = 'TAS diff-%s' % exp_names[args.diff]
        if args.var == 'PR':
            variable = 'PR diff-%s' % exp_names[args.diff]
    else:
        if args.var == 'TAS':
            variable = 'TAS celsius'
        if args.var == 'PR':
            variable = 'PR mm.år'

    # Add full model name column: join col 4 and 7
    models = df[df.columns[4:7]].apply(
        lambda x: '_'.join(x.dropna().astype(str)),
        axis=1
    )
    df['FullModel'] = models
    if args.cmip == '5':
        df = df[df.FullModel != 'MIROC-MIROC5_WRF361H_r1i1p1']

    outfile = None
    figure = None

    if args.plot == 'bar':
        barplot(df)
    elif args.plot == 'cat1':
        cat1plot(df)
    elif args.plot == 'cat2':
        catplot2(df)
    elif args.plot == 'kde1':
        kde1plot(df)
    elif args.plot == 'kde2':
        kde2plot(df)
    elif args.plot == 'kdediff':
        kde_scatterplot_diff(df, df2)
    elif args.plot == 'geo':
        geoplot()
    elif args.plot == 'scatter':
        #sns.set_style('whitegrid')
        #sns.set_style('whitegrid', {'axes.grid' : True,'axes.edgecolor':'none'})
        #sns.set(style='ticks')
        if args.diff:
            grid_scatterplot_diff(df)
        else:
            grid_scatterplot_abs(df)
    else:
        exit()

    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())

    if args.save:
        plt.show(block=False)
        plt.pause(1)
        savefile = outroot + '/' + outfile
        #savefile = outfile
        print('save', savefile)
        figure.savefig(savefile)
    else:
        plt.show()
