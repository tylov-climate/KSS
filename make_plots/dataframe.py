#!/usr/bin/env python
#
# Developed by Tyge Lovset, September 2020

import os
import glob
import netCDF4 as nc4
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import pandas as pd
import math


def load_mask():
    img = mpimg.imread('norway_mask.png')
    img = img[:,:,0] < 0.5
    return img


# Save load mean of the statistical data over periods and seasons. (avg, variance, ...)

def average_v1data(inroot, output):
    seasons, exps, stat_ops, variables, models = [], [], [], [], []
    seasons_r, exps_r, stat_ops_r, variables_r, models_r = {}, {}, {}, {}, {}

    for sub_path in sorted(glob.glob(inroot + '/*/*/*')):
        for path in sorted(glob.glob(sub_path + '/*.nc')):
            f = os.path.basename(path)
            domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, freq_id, var_id, create_ver_id, period, season, stat_op = f[:-3].split('_')
            model_name = '_'.join([institute_id, model_id, ensemble_id, source_id, rcm_version])
            exp_name = experiment_id + '_' + period
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
    #print('Dimensions:')
    #print(seasons)
    #print(exps)
    #print(stat_ops)
    #print(variables)
    #print(len(models), 'models')
    stats = np.empty(shape=(len(seasons), len(exps), len(stat_ops), len(variables), len(models)), dtype=float)
    stats.fill(np.nan)

    print(stats.shape)
    d = dims['inv']
    n = 0
    mask_img = load_mask()
    for sub_path in sorted(glob.glob(inroot + '/*/*/*')):
        for path in sorted(glob.glob(sub_path + '/*.nc')):
            f = os.path.basename(path)
            domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, freq_id, var_id, create_ver_id, period, season, stat_op = f[:-3].split('_')
            model_name = '_'.join([institute_id, model_id, ensemble_id, source_id, rcm_version])
            exp_name = experiment_id + '_' + period

            with nc4.Dataset(path) as src:
                for ncvname, ncvar in src.variables.items():
                    if ncvname == var_id:
                        data = ncvar[:]
                        value_unmasked = np.mean(data)
                        data = np.ma.masked_array(data, mask=mask_img) # Mask is with Norway shape file.
                        value = np.mean(data)
                        stats[d[0][season]][d[1][exp_name]][d[2][stat_op]][d[3][var_id]][d[4][model_name]] = value
                        print(n, period, season, exp_name, stat_op, var_id, model_name, ':', value, value_unmasked)
                        n += 1
    return stats, dims


def create_dataframe(stats, dims, file):
    d = dims['inv']
    season_ren = {'full': 'annual', 's1': 'spring', 's2': 'summer', 's3': 'autumn', 's4': 'winter',
                  'FULL': 'annual', 'MAM': 'spring', 'JJA': 'summer', 'SON': 'autumn', 'DJF': 'winter'}

    m = {'Season': [], 'Experiment': [], 'Period': [],
         'Institute': [], 'Model': [], 'Model Id': [], 'Ensemble': [], 'RCM Ver': [],
         'TAS celsius': [], 'PR mm.day': [],
         'TAS': [], 'PR': [],
         'TAS variance': [], 'PR variance': []}
    for season in dims['seasons']:
        season_disp = season_ren[season]
        for exp_name in dims['exps']:
            exp_disp = exp_name.split('_')
            for model_name in dims['models']: # institute_id, model_id, ensemble_id, source_id, rcm_version
                model = model_name.split('_')
                source = model[1].split('-')
                tas_mean = stats[d[0][season]][d[1][exp_name]][d[2]['timmean']][d[3]['tas']][d[4][model_name]]
                pr_mean = stats[d[0][season]][d[1][exp_name]][d[2]['timmean']][d[3]['pr']][d[4][model_name]]
                tas_variance = stats[d[0][season]][d[1][exp_name]][d[2]['timvar']][d[3]['tas']][d[4][model_name]]
                pr_variance = stats[d[0][season]][d[1][exp_name]][d[2]['timvar']][d[3]['pr']][d[4][model_name]]
                if not (math.isnan(tas_mean) and math.isnan(pr_mean)):
                    #print(season_disp, exp_disp[0], exp_disp[1], model_name, tas_mean, pr_mean)
                    m['Season'].append(season_disp)
                    m['Experiment'].append(exp_disp[0])
                    m['Period'].append(exp_disp[1])
                    m['Institute'].append(model[0])
                    m['Model'].append(model[1])
                    m['Model Id'].append(model[3])
                    m['Ensemble'].append(model[2])
                    m['RCM Ver'].append(model[4])
                    m['TAS celsius'].append(tas_mean - 273.15)
                    m['PR mm.day'].append(pr_mean * (24*60*60))
                    m['TAS'].append(tas_mean)
                    m['PR'].append(pr_mean)
                    m['TAS variance'].append(tas_variance)
                    m['PR variance'].append(pr_variance)

    df = pd.DataFrame(m)
    df.to_pickle(file + '.pkl')
    df.to_csv(file + '.csv')
    return df


# MAIN


if __name__ == '__main__':
    #inroot='/tos-project4/NS9076K/data/cordex-norway/stats_v1'
    inroot='C:/Dev/DATA/stats_v1'
    file = 'kss_analysis'

    if os.path.exists(file + '.pkl'):
        df = pd.read_pickle(file + '.pkl')
    else:
        stats, dims = average_v1data(inroot, file)
        print(stats.shape)
        print(stats.shape)
        print(dims['seasons'])
        print(dims['exps'])
        print(dims['stat_ops'])
        print(dims['variables'])
        df = create_dataframe(stats, dims, file)

    print(df)

