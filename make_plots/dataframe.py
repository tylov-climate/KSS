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

last_study_models = [
    'ICHEC-EC-EARTH_HIRHAM5_r3i1p1',
    'ICHEC-EC-EARTH_RCA4_r12i1p1',
    'ICHEC-EC-EARTH_CCLM4-8-17_r12i1p1',
    'ICHEC-EC-EARTH_RACMO22E_r1i1p1',
    'CNRM-CERFACS-CNRM-CM5_RCA4_r1i1p1',
    'CNRM-CERFACS-CNRM-CM5_CCLM4-8-17_r1i1p1',
    'IPSL-IPSL-CM5A-MR_RCA4_r1i1p1',
    'IPSL-IPSL-CM5A-MR_WRF331F_r1i1p1',
    'MPI-M-MPI-ESM-LR_REMO2009_r1i1p1',
    'MPI-M-MPI-ESM-LR_RCA4_r1i1p1',
    'MPI-M-MPI-ESM-LR_CCLM4-8-17_r1i1p1',
    'MOHC-HadGEM2-ES_RCA4_r1i1p1'
]


def load_mask():
    img = mpimg.imread('norway_mask.png')
    img = img[:,:,0] < 0.5
    return img


# Save load mean of the statistical data over periods and seasons. (avg, variance, ...)

def average_data(inroot, output, version=1):
    seasons, exps, stat_ops, variables, models = [], [], [], [], []
    if version == 1:
        dirpattern = '/*/*/*'
        seasons = ['full', 's1', 's2', 's3', 's4']
    else:
        dirpattern = '/*/*'
        seasons = ['FULL', 'MAM', 'JJA', 'SON', 'DJF']

    for sub_path in sorted(glob.glob(inroot + dirpattern)):
        for path in sorted(glob.glob(sub_path + '/*.nc')):
            f = os.path.basename(path)
            if version == 1:
                domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, freq_id, var_id, create_ver_id, period, season, stat_op = f[:-3].split('_')
            else:
                domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, freq_id, var_id, create_ver_id, stat_op, season, period = f[:-3].split('_')
            model_name = '_'.join([institute_id, model_id, ensemble_id, source_id, rcm_version])
            exp_name = experiment_id + '_' + period
            if exp_name not in exps:
                exps.append(exp_name)
            if stat_op not in stat_ops:
                stat_ops.append(stat_op)
            if var_id not in variables:
                variables.append(var_id)
            if model_name not in models:
                models.append(model_name)

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
    stats = np.empty(shape=(len(seasons), len(exps), len(stat_ops), len(variables), len(models)), dtype=float)
    stats.fill(np.nan)

    d = dims['inv']
    n = 0
    mask_img = load_mask()
    for sub_path in sorted(glob.glob(inroot + dirpattern)):
        for path in sorted(glob.glob(sub_path + '/*.nc')):
            f = os.path.basename(path)
            if version == 1:
                domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, freq_id, var_id, create_ver_id, period, season, stat_op = f[:-3].split('_')
            else:
                domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, freq_id, var_id, create_ver_id, stat_op, season, period = f[:-3].split('_')

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
         'TAS celsius': [], 'PR mm.year': [],
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
                    m['PR mm.year'].append(pr_mean * (365.25*24*60*60))
                    m['TAS'].append(tas_mean)
                    m['PR'].append(pr_mean)
                    m['TAS variance'].append(tas_variance)
                    m['PR variance'].append(pr_variance)

    df = pd.DataFrame(m)
    # Merge models to match last_study_models[] signature.
    models = df[df.columns[4:7]].apply(
        lambda x: '_'.join(x.dropna().astype(str)),
        axis=1
    )
    last_study = models == last_study_models[0]
    for i in range(1, len(last_study_models)):
        last_study |= models == last_study_models[i]
    df['Last Study'] = last_study
    df.to_pickle(file + '.pkl')
    df.to_csv(file + '.csv', sep=';')
    return df


# MAIN


if __name__ == '__main__':
    for version in (2,):
        if os.name == 'posix':
            inroot = '/tos-project4/NS9076K/data/cordex-norway/stats_v%d' % version
        else: # 'nt' -> windows
            inroot = 'D:/Data/EUR-11_norway/stats_v%d' % version
        file = 'kss_analysis_v%d' % version

        if os.path.exists(file + '.pkl'):
            df = pd.read_pickle(file + '.pkl')
        else:
            stats, dims = average_data(inroot, file, version)
            print(stats.shape)
            print(dims['seasons'])
            print(dims['exps'])
            print(dims['stat_ops'])
            print(dims['variables'])
            df = create_dataframe(stats, dims, file)
        print(df)

