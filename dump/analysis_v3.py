#!/usr/bin/env python
#
# Developed by Tyge Lovset, August 2020

import os
import glob
import netCDF4 as nc4
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import pandas as pd

def load_mask():
    img = mpimg.imread('norway_mask.png')
    img = img[:,:,0] < 0.5
    return img


# Save load mean of the statistical data over periods and seasons. (avg, variance, ...)

def save_statistics_v2_data(inroot, output):
    seasons, exps, stat_ops, variables, models = [], [], [], [], []
    seasons_r, exps_r, stat_ops_r, variables_r, models_r = {}, {}, {}, {}, {}
    for sub_path in sorted(glob.glob(inroot + '/*/*')):
        for path in sorted(glob.glob(sub_path + '/*.nc')):
            f = os.path.basename(path)
            
            domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, freq_id, var_id, create_ver_id, stat_op, season, period = f[:-3].split('_')
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
    mask_img = load_mask()
    for sub_path in sorted(glob.glob(inroot + '/*/*')):
        for path in sorted(glob.glob(sub_path + '/*.nc')):
            f = os.path.basename(path)
            domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, freq_id, var_id, create_ver_id, stat_op, season, period = f[:-3].split('_')
            model_name = '_'.join([institute_id, model_id, ensemble_id]) # , rcm_version])
            exp_name = experiment_id + '-' + period

            with nc4.Dataset(path) as src:
                for ncvname, ncvar in src.variables.items():
                    if ncvname == var_id:
                        data = ncvar[:]
                        data = np.ma.masked_array(data, mask=mask_img) # Mask it
                        value = np.mean(data)
                        stats[d[0][season]][d[1][exp_name]][d[2][stat_op]][d[3][var_id]][d[4][model_name]] = value
                        print(n, period, season, exp_name, stat_op, var_id, model_name, ':', value)
                        n += 1
    return stats, dims
    '''
    print('assigned values:', n, stats.shape)
    np.save(output + '.npy', stats)
    with open(output + '.json', 'w') as f:
        json.dump(dims, f, indent=4)
    '''


def get_statistics_v2(inroot, file):
    if not os.path.exists(file + '.npy'):
        save_statistics_v2_data(inroot, file)
    print('loading results...')
    stats = np.load(file + '.npy')
    with open(file + '.json', 'r') as f:
        dims = json.load(f)
    return stats, dims


# MAIN

if __name__ == '__main__':
    #inroot='/tos-project4/NS9076K/data/cordex-norway/stats_v2'
    inroot = 'D:/DATA/EUR-11_norway/stats_v2'
    file = 'kss_analysis_v2'

    stats, dim = save_statistics_v2_data(inroot, file)
    print(stats.shape)
    exit()

    stats, dims = get_statistics_v2(inroot, file)
    for m in dims['models']:
        print(m)
    print("")
    print(stats.shape)
    print(dims['seasons'])
    print(dims['exps'])
    print(dims['stat_ops'])
    print(dims['variables'])
