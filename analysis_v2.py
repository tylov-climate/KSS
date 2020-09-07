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

## ANALYSE2

def save_statistics_v1(inroot, output):
    seasons, exps, stat_ops, variables, models = [], [], [], [], []
    seasons_r, exps_r, stat_ops_r, variables_r, models_r = {}, {}, {}, {}, {}
    
    for sub_path in sorted(glob.glob(inroot + '/*/*/*')):
        for path in sorted(glob.glob(sub_path + '/*.nc')):
            f = os.path.basename(path)
            domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, freq_id, var_id, create_ver_id, period, season, stat_op = f[:-3].split('_')
            model_name = '_'.join([institute_id, model_id, ensemble_id]) # , rcm_version])
            exp_name = experiment_id + '-' + period
            if season not in seasons:
                seasons.append(season)
            if exp_name not in exps:
                exps.append(exp_name)
            if stat_op not in stat_ops:
                stat_ops.append(stat_op)
            if var_id not in variables:
                variables.append(var_id)
            if model_name not in models:
                models.append(model_name)

    seasons = sorted(seasons)
    exps = sorted(exps)
    stat_ops = sorted(stat_ops)
    variables = sorted(variables)
    models = sorted(models)

    dims = {
        'names': ['seasons', 'exps', 'stat_ops', 'variables', 'models'],
        'seasons': seasons,
        'exps': exps,
        'stat_ops': stat_ops,
        'variables': variables,
        'models': models,
        'inv': [{seasons[i]: i for i in range(len(seasons))},
                {exps[i]: i for i in range(len(exps))},
                {stat_ops[i]: i for i in range(len(stat_ops))},
                {variables[i]: i for i in range(len(variables))},
                {models[i]: i for i in range(len(models))}]
    }

    print('Dimensions:')
    print(seasons)
    print(exps)
    print(stat_ops)
    print(variables)
    print(len(models), 'models')
    stats = np.empty(shape=(len(seasons), len(exps), len(stat_ops), len(variables), len(models)), dtype=float)
    stats.fill(np.nan)
    
    print(stats.shape)
    d = dims['inv']
    n = 0
    for sub_path in sorted(glob.glob(inroot + '/*/*/*')):
        for path in sorted(glob.glob(sub_path + '/*.nc')):
            f = os.path.basename(path)
            domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, freq_id, var_id, create_ver_id, period, season, stat_op = f[:-3].split('_')
            model_name = '_'.join([institute_id, model_id, ensemble_id]) # , rcm_version])
            exp_name = experiment_id + '-' + period

            with nc4.Dataset(path) as src:
                for ncvname, ncvar in src.variables.items():
                    if ncvname == var_id:
                        data = ncvar[:]
                        value = np.mean(data)
                        stats[d[0][season]][d[1][exp_name]][d[2][stat_op]][d[3][var_id]][d[4][model_name]] = value
                        #print(d[0][season], d[1][exp_name], d[2][stat_op], d[3][var_id])
                        print(n, period, season, exp_name, stat_op, var_id, model_name, ':', value)
                        n += 1
    print('assigned values:', n, stats.shape)
    np.save(output + '.npy', stats)
    with open(output + '.json', 'w') as f:
        json.dump(dims, f, indent=4)    
    
def get_statistics_v1(inroot, file):
    if not os.path.exists(file + '.npy'):
        save_statistics_v1(inroot, file)
    print('loading results...')
    stats = np.load(file + '.npy')
    with open(file + '.json', 'r') as f:
        dims = json.load(f)    
    return stats, dims
    

def make_plots(stats, dims):
    fig = plt.figure(figsize=(18, 10))
    pos = [2, n, 0]
    pass


def pairgrid_plots(stats, dims, statop, season='full', exp=None, period=None):
    season_ren = {'full': 'annual', 's1': 'spring', 's2': 'summer', 's3': 'autumn', 's4': 'winter'}
    stat_ren = {'timmean': 'mean', 'timvar': 'variance'}

    d = dims['inv']
    s = d[0][season]
    op = d[2][statop]
    m = {}
    for s in range(len(dims['seasons'])):
        if season is None or season == dims['seasons'][s]:
            for e in range(len(dims['exps'])):
                period_label = dims['exps'][e]
                if (exp is None or exp in period_label) and (period is None or period in period_label):
                    print(period_label)
                    tas = stats[s][e][op][d[3]['tas']]
                    pr = stats[s][e][op][d[3]['pr']]
                    season_label = season_ren[season]
                    stat_label = stat_ren[statop]
                    name = '%s_%s_%s' % ('tas', season_label, period_label)
                    m[name] = tas
                    name = '%s_%s_%s' % ('pr', season_label, period_label)
                    m[name] = pr

    df = pd.DataFrame(m)
    #print(df)
    #return
    g = sns.PairGrid(df)
    g.map_upper(sns.regplot)
    g.map_lower(sns.kdeplot, cmap = "Blues_d")
    g.map_diag(sns.kdeplot, lw = 3, legend = True);
    plt.show()
    

# MAIN

if __name__ == '__main__':
    inroot='/tos-project4/NS9076K/data/cordex-norway/stats_v1'
    file = 'kss_analysis'
    '''
    import seaborn as sb
    df = sb.load_dataset('tips')
    print(df)
    g = sb.FacetGrid(df, col = "sex", hue = "time", palette='Set1', hue_order=["Dinner", "Lunch"])
    g.map(plt.scatter, "total_bill", "tip").add_legend()
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

    pairgrid_plots(stats, dims, statop='timmean', exp='rcp85') # , season='s1', period='2071-2100'