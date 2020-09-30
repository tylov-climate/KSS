#!/usr/bin/env python
#
# Developed by Tyge Lovset, August 2020

import os
import glob
import netCDF4 as nc4
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def get_statistics_v1(inroot, file):
    print('loading results...')
    stats = np.load(file + '.npy')
    with open(file + '.json', 'r') as f:
        dims = json.load(f)
    return stats, dims


def make_plots(stats, dims):
    fig = plt.figure(figsize=(18, 10))
    pos = [2, n, 0]
    pass



def pairgrid_plots(stats, dims, statop, season=None, scenario=None, period=None):
    season_ren = {'full': 'annual', 's1': 'spring', 's2': 'summer', 's3': 'autumn', 's4': 'winter',
                  'FULL': 'annual', 'MAM': 'spring', 'JJA': 'summer', 'SON': 'autumn', 'DJF': 'winter'}
    stat_ren = {'timmean': 'mean', 'timvar': 'variance'}
    exp_ren = {'timmean': 'mean', 'timvar': 'variance'}

    d = dims['inv']
    op = d[2][statop]
    m = {}
    exps = [i for i in range(len(dims['exps'])) if ((period is None) or period in dims['exps'][i]) and ((scenario is None) or scenario in dims['exps'][i])]
    seasons = [i for i in range(len(dims['seasons']))] if season is None else [d[0][season]]
    #scenarios = [i for i in range(len(dims['exps'])) if scenario in dims['exps'][i]] if scenario else []
    #periods = [i for i in range(len(dims['exps'])) if period in dims['exps'][i]] if period else []
    #print(dims['exps'])
    #print('scen', [dims['exps'][i] for i in scenarios])
    #print('peri', [dims['exps'][i] for i in periods])
    #print(seasons)
    #exit()
    '''
    print('Building DataFrame')
    for s in seasons:
        for e in exps:
            tas = stats[s][e][op][d[3]['tas']]
            pr = stats[s][e][op][d[3]['pr']]
            exp_label = dims['exps'][e]
            season_label = season_ren[dims['seasons'][s]]
            #stat_label = stat_ren[statop]
            name = '%s %s %s' % ('tas', season_label, exp_label)
            print(name)
            m[name] = tas
            name = '%s %s %s' % ('pr', season_label, exp_label)
            m[name] = pr
    print('Define DataFrame')
    #df = pd.DataFrame(m)
    #print(df)
    #return

    g = sns.PairGrid(df)
    g.map_upper(sns.regplot)
    g.map_lower(sns.kdeplot, cmap = 'Blues_d')
    g.map_diag(sns.kdeplot, lw = 3, legend = True);
    plt.show()
    '''
    fig = plt.figure(figsize=(18, 9))
    n = 0
    #cols = seasons if season is None else
    pos = [len(exps), len(seasons), n]
    print('exps', [dims['exps'][i] for i in exps], pos)

    for e in exps:
        for s in seasons:
            # plot one week pr / tas
            n += 1
            pos[2] = n
            ax = fig.add_subplot(*pos)
            tas = stats[s][e][op][d[3]['tas']]
            pr = stats[s][e][op][d[3]['pr']] * (24*60*60)
            exp_label = dims['exps'][e]
            season_label = season_ren[dims['seasons'][s]]
            tas_name = '%s %s %s' % ('tas', season_label, exp_label)
            pr_name = '%s %s %s' % ('pr', season_label, exp_label)
            print(tas_name)
            df = pd.DataFrame({tas_name: tas, pr_name: pr})
            sns.regplot(data=df, x=tas_name, y=pr_name, fit_reg=True, ax=ax)

    plt.show()



def make_dataframe(stats, dims, statop, season=None, scenario=None, period=None):
    season_ren = {'full': 'annual', 's1': 'spring', 's2': 'summer', 's3': 'autumn', 's4': 'winter',
                  'FULL': 'annual', 'MAM': 'spring', 'JJA': 'summer', 'SON': 'autumn', 'DJF': 'winter'}
    stat_ren = {'timmean': 'mean', 'timvar': 'variance'}
    exp_ren = {'timmean': 'mean', 'timvar': 'variance'}

    d = dims['inv']
    op = d[2][statop]
    m = {}
    exps = [i for i in range(len(dims['exps'])) if ((period is None) or period in dims['exps'][i]) and ((scenario is None) or scenario in dims['exps'][i])]
    seasons = [i for i in range(len(dims['seasons']))] if season is None else [d[0][season]]
    fig = plt.figure(figsize=(18, 9))
    n = 0
    #cols = seasons if season is None else
    pos = [len(exps), len(seasons), n]
    print('exps', [dims['exps'][i] for i in exps], pos)

    df = pd.DataFrame()
    for e in exps:
        for s in seasons:
            tas = stats[s][e][op][d[3]['tas']]
            pr = stats[s][e][op][d[3]['pr']] * (24*60*60) # convert to mm/day
            exp_label = dims['exps'][e]
            season_label = season_ren[dims['seasons'][s]]
            tas_name = '%s %s %s' % ('tas', season_label, exp_label)
            pr_name = '%s %s %s' % ('pr', season_label, exp_label)
            print(tas_name)
            df[tas_name] = tas
            df[pr_name]: pr
    return df


# MAIN


if __name__ == '__main__':
    inroot='/tos-project4/NS9076K/data/cordex-norway/stats_v1'
    file = 'kss_analysis'
    '''
    import seaborn as sb
    df = sb.load_dataset('tips')
    print(df)
    g = sb.FacetGrid(df, col = 'sex', hue = 'time', palette='Set1', hue_order=['Dinner', 'Lunch'])
    g.map(plt.scatter, 'total_bill', 'tip').add_legend()
    plt.show()
    exit()
    '''
    stats, dims = get_statistics_v1(inroot, file)
    d = dims['inv']
    s = dims['seasons']
    e = dims['exps']
    o = dims['stat_ops']
    v = dims['variables']
    m = dims['models']
    print(stats.shape)

    #pairgrid_plots(stats, dims, statop='timmean', period='2071-2100') # , period='2031-2060') # , period='2071-2100', season='s1'
    df = make_dataframe(stats, dims, statop='timmean', period='2071-2100')
    print(df)
