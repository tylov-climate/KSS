#!/usr/bin/env python
#
# Developed by Tyge Lovset, September 2020

import os
import sys
import platform
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
'''
overlaps_models = {
    #'CNRM-CM5': ['ALADIN_r1i1p1', 'ALARO_r1i1p1', 'RACMO_r1i1p1'],
    'CNRM-CM5': ['ALADIN63_r1i1p1', 'RACMO_r1i1p1'],
    'EC-EARTH': ['CCLM_r12i1p1', 'HIRHAM5_r3i1p1', 'RACMO_r12i1p1', 'RCA_r12i1p1', 'REMO_r12i1p1'],
    'HadGEM2-ES': ['HIRHAM5_r1i1p1', 'RACMO_r1i1p1', 'RCA_r1i1p1', 'REMO_r1i1p1'],
    'MPI-ESM-LR': ['CCLM_r1i1p1', 'RCA_r1i1p1', 'REMO_r1i1p1', 'REMO_r2i1p1'],
    'NorESM1-M': ['RCA_r1i1p1', 'REMO_r1i1p1']
}
'''
selected_models = {
    'CNRM-CM5': ['ALADIN63_r1i1p1'],
    'EC-EARTH': ['CCLM_r12i1p1', 'HIRHAM5_r3i1p1', 'RCA_r12i1p1'],
    'HadGEM2-ES': ['RCA_r1i1p1', 'REMO_r1i1p1'],
    'MPI-ESM-LR': ['CCLM_r1i1p1', 'REMO_r2i1p1'],
    'NorESM1-M': ['RCA_r1i1p1', 'REMO_r1i1p1']
}


def load_mask():
    img = mpimg.imread('norway_mask.png')
    img = img[:,:,0] > 0.5
    return img


# Save load mean of the statistical data over periods and seasons. (avg, variance, ...)

def average_data(inroot, output):
    seasons, exps, stat_ops, variables, models = ('ANN', 'MAM', 'JJA', 'SON', 'DJF'), [], [], [], []
    dirpattern = '/*'
    #print(inroot, output)

    for sub_path in sorted(glob.glob(inroot + dirpattern)):
        for path in sorted(glob.glob(sub_path + '/*.nc')):
            f = os.path.basename(path)
            var_id, domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, stat_op, create_ver_id, period = f[:-3].split('_')
            season = 'all'

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
        'names': ('seasons', 'exps', 'stat_ops', 'variables', 'models'),
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
    mask_img = np.flip(mask_img, axis=0)
    for sub_path in sorted(glob.glob(inroot + dirpattern)):
        for path in sorted(glob.glob(sub_path + '/*.nc')):
            f = os.path.basename(path)
            var_id, domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, stat_op, create_ver_id, period = f[:-3].split('_')
            season = 'all'
            #print(var_id, domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, stat_op, create_ver_id, period)
            model_name = '_'.join([institute_id, model_id, ensemble_id, source_id, rcm_version])
            exp_name = experiment_id + '_' + period

            season_all = ('DJF', 'MAM', 'JJA', 'SON', 'ANN')

            with nc4.Dataset(path) as src:
                for ncvname, ncvar in src.variables.items():
                    if ncvname == var_id:
                        data_all = ncvar[:]
                        season_n = 0
                        for season in season_all:
                            data = np.swapaxes(data_all, 0, 1).mean(axis=1) if season == 'ANN' else data_all[season_n]
                            season_n += 1

                            #value_unmasked = np.mean(data)
                            data = np.ma.masked_array(data, mask=mask_img) # Mask is with Norway shape file.
                            value = np.mean(data)
                            if var_id == 'tas' and value < 200.0: # Fix some data with C degrees instead of K.
                                value += 273.15
                            stats[d[0][season]][d[1][exp_name]][d[2][stat_op]][d[3][var_id]][d[4][model_name]] = value
                            if var_id == 'pr':
                                value *= 365.25 * 24 * 60 * 60
                            #print(n, period, season, exp_name, stat_op, var_id, model_name, ':', value) # , value_unmasked)
                            n += 1
    return stats, dims


def create_dataframe(stats, dims, stat_op, use_rcp_selected=False):
    d = dims['inv']
    '''
    m = {'Season': [], 'Experiment': [], 'Period': [],
         'Institute': [], 'Model': [], 'Model Id': [], 'Ensemble': [], 'RCM Ver': [],
         'TAS celsius': [], 'PR mm.year': [],
         'TAS diff': [], 'PR diff': [],
    }
    '''
    m = {'Årstid': [], 'Eksperiment': [], 'Periode': [],
         'Institutt': [], 'Modell': [], 'Modell Id': [], 'Ensemble': [], 'RCM Ver': [],
         'TAS celsius': [], 'PR mm.år': [],
        'TAS-historical_1971-2000': [], 'TAS-historical_1985-2014': [], 'TAS-historical_1991-2020': [],
        'TAS-rcp26_2041-2070': [], 'TAS-rcp26_2071-2100': [],
        'TAS-rcp45_2041-2070': [], 'TAS-rcp45_2071-2100': [],
        'TAS-rcp85_2041-2070': [], 'TAS-rcp85_2071-2100': [],
        'PR-historical_1971-2000': [], 'PR-historical_1985-2014': [], 'PR-historical_1991-2020': [],
        'PR-rcp26_2041-2070': [], 'PR-rcp26_2071-2100': [],
        'PR-rcp45_2041-2070': [], 'PR-rcp45_2071-2100': [],
        'PR-rcp85_2041-2070': [], 'PR-rcp85_2071-2100': [],
    }

    pr_fac = 365.25 * 24 * 60 * 60

    for season in dims['seasons']:
        #season_disp = season_ren[season]
        for exp_name in dims['exps']:
            exp_disp = exp_name.split('_')
            for model_name in dims['models']: # institute_id, model_sign, ensemble_id, source_id, rcm_version
                model = model_name.split('_')
                source = model[1].split('-')

                if use_rcp_selected:
                    match = False
                    for key, val in selected_models.items():
                        if match: break
                        if model[1].endswith(key):           # 'Model' in csv
                            for mod in val:
                                mid, ens = mod.split('_')
                                if model[3].startswith(mid) and model[2] == ens: # 'Model Id' and 'Ensemble' in csv
                                    match = True
                                    #print('MATCH: ', key, ':', mid, ens, ':', model[3], model[2])
                                    if ens != model[2]:
                                        print('Wrong ensemble match:', model[1], model[3], model[2], '!=', ens)
                                    break
                    if not match:
                        continue

                s = d[0][season]
                x = d[1][exp_name]
                o = d[2][stat_op]
                n = d[4][model_name]
                tas_mean = stats[s][x][o][d[3]['tas']][n]
                pr_mean = stats[s][x][o][d[3]['pr']][n]
                #tas_variance = stats[s][x][d[2]['timvar']][d[3]['tas']][n]
                #pr_variance = stats[s][x][d[2]['timvar']][d[3]['pr']][n]
                if not (math.isnan(tas_mean) and math.isnan(pr_mean)):
                    #print(season, exp_disp[0], exp_disp[1], model_name, tas_mean, pr_mean)
                    m['Årstid'].append(season)
                    m['Eksperiment'].append(exp_disp[0])
                    m['Periode'].append(exp_disp[1])
                    m['Institutt'].append(model[0])
                    m['Modell'].append(model[1])
                    m['Modell Id'].append(model[3])
                    m['Ensemble'].append(model[2])
                    m['RCM Ver'].append(model[4])
                    m['TAS celsius'].append(tas_mean - 273.15)
                    m['PR mm.år'].append(pr_mean * pr_fac)

                    for x1 in range(len(dims['exps'])):
                        name = dims['exps'][x1]
                        if x1 != x:
                            m['TAS-%s' % name].append(stats[s][x1][o][d[3]['tas']][n] - tas_mean)
                            m['PR-%s' % name].append(100 * (stats[s][x1][o][d[3]['pr']][n] - pr_mean) / pr_mean)
                        else:
                            m['TAS-%s' % name].append(0.0)
                            m['PR-%s' % name].append(0.0)

    df = pd.DataFrame(m)
    # Merge models to match last_study_models[] signature.
    models = df[df.columns[4:7]].apply(
        lambda x: '_'.join(x.dropna().astype(str)),
        axis=1
    )
    last_study = models == last_study_models[0]
    for i in range(1, len(last_study_models)):
        last_study |= models == last_study_models[i]
    df['Referansemodell'] = last_study
    return df



def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    print('make_csv - make csv input files for KSS Klima 2100')
    print('')

    parser.add_argument(
        '-s', '--stat', required=True,
        help='Statistics (mean, min, max)'
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
    parser.add_argument(
        '--selected', action='store_true',
        help='Use a selection of models only'
    )
    return parser.parse_args()


### MAIN ###

if __name__ == '__main__':
    uname = platform.uname()[1]

    args = parse_args()

    stat_op = 'yseas%s' % args.stat
    sub_path = stat_op

    if args.indir:
        inroot = args.indir
    elif '-tos' in uname: # NIRD or similar
        inroot = '/tos-project4/NS9076K/data/cordex-norway/stats_v3.NEW5/%s' % sub_path
    elif 'norceresearch.no' in uname:
        inbase = os.path.expanduser('~') + '/proj/KSS/cordex-norway'
        inroot = inbase + '/stats_v3/%s' % sub_path
    elif 'ppi-ext' in uname: # met.no
        inroot = '/lustre/storeC-ext/users/kin2100/NORCE/NIRD_bkp/cordex-norway/stats_v3'
    else: # home
        inroot = 'C:/Dev/DATA/cordex-norway/stats_v3.NEW5/%s' % sub_path

    file = '%s_kss' % stat_op
    if args.selected:
        file += '_selected'

    print('Inroot:', inroot)
    print('Output:', file + '.csv')

    if False: # os.path.exists(file + '.pkl'):
        print("Load", file + '.pkl')
        df = pd.read_pickle(file + '.pkl')
        df = pd.read_csv(file + '.csv', sep=';')
    else:
        stats, dims = average_data(inroot, file)
        print(stats.shape)
        print(dims['seasons'])
        print(dims['exps'])
        print(dims['stat_ops'])
        print(dims['variables'])
        df = create_dataframe(stats, dims, stat_op, args.selected)

    print(df)
    #df.to_pickle(file + '.pkl')
    df.to_csv(file + '.csv', sep=';')
    print("File written:", file + '.csv')
