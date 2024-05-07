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


def load_mask():
    img = mpimg.imread('norway_mask.png')
    img = img[:, :, 0] > 0.5
    return np.flip(img, axis=0)


# Save load mean of the statistical data over periods and seasons. (avg, variance, ...)

def average_data(inroot, output):
    exps, stat_ops, variables, models = [], [], [], []
    interval_seasons = ('ANN', 'MAM', 'JJA', 'SON', 'DJF')
    interval_months = ('ANN', 'Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Des')
    dirpattern = '/*'
    #print(inroot, output)
    seasons = interval_seasons if args.interval == 'yseas' else interval_months

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
    for sub_path in sorted(glob.glob(inroot + dirpattern)):
        for path in sorted(glob.glob(sub_path + '/*.nc')):
            f = os.path.basename(path)
            var_id, domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, stat_op, create_ver_id, period = f[:-3].split('_')
            season = 'all'
            #print(var_id, domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, stat_op, create_ver_id, period)
            model_name = '_'.join([institute_id, model_id, ensemble_id, source_id, rcm_version])
            exp_name = experiment_id + '_' + period
            if args.interval == 'yseas':
                season_all = ('DJF', 'MAM', 'JJA', 'SON', 'ANN')
            else:
                season_all = seasons[1:] + seasons[:1]

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


def create_dataframe(stats, dims, stat_op):
    d = dims['inv']
    m = {
        'Årstid': [], 'Eksperiment': [], 'Periode': [],
        'Institutt': [], 'Modell': [], 'Modell Id': [],
        'Ensemble': [], 'RCM Ver': [],
        'TAS celsius': [], 'PR mm.år': [],
        'TAS diff-historical_1971-2000': [],
        'TAS diff-historical_1991-2020': [],
        'TAS diff-ssp370_2041-2070': [],
        'TAS diff-ssp370_2071-2100': [],
        'PR diff-historical_1971-2000': [],
        'PR diff-historical_1991-2020': [],
        'PR diff-ssp370_2041-2070': [],
        'PR diff-ssp370_2071-2100': [],
    }

    pr_fac = 365.25 * 24 * 60 * 60

    for season in dims['seasons']:
        #season_disp = season_ren[season]
        for exp_name in dims['exps']:
            exp_disp = exp_name.split('_')
            for model_name in dims['models']: # institute_id, model_sign, ensemble_id, source_id, rcm_version
                model = model_name.split('_')
                source = model[1].split('-')

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
                            m['TAS diff-%s' % name].append(tas_mean - stats[s][x1][o][d[3]['tas']][n])
                            m['PR diff-%s' % name].append(100 * (pr_mean - stats[s][x1][o][d[3]['pr']][n]) / pr_mean)
                        else:
                            m['TAS diff-%s' % name].append(0.0)
                            m['PR diff-%s' % name].append(0.0)

    df = pd.DataFrame(m)
    return df



def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    print('make_csv - make csv input files for KSS Klima 2100')
    print('')

    parser.add_argument(
        '-s', '--stat', default='mean',
        help='Statistics (mean=default, min, max)'
    )
    parser.add_argument(
        '--interval', default='yseas',
        help='Interval (yseas=default, ymon)'
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

if __name__ == '__main__':
    uname = platform.uname()[1]

    args = parse_args()

    stat_op = '%s%s' % (args.interval, args.stat) # e.g. yseasmean
    sub_path = stat_op

    if args.indir:
        inbase = inroot = args.indir
    elif '-nird' in uname: # NIRD or similar
        inbase = '/datalake/NS9001K/dataset/tylo/kin2100/stats_cmip6'
        inroot = '%s/%s' % (inbase, sub_path)
    elif 'norceresearch.no' in uname:
        inbase = os.path.expanduser('~') + '/proj/KSS/cordex-norway'
        inroot = inbase + '/stats_v3/%s' % sub_path
    elif 'ppi-ext' in uname: # met.no
        inbase = '/lustre/storeC-ext/users/kin2100/NORCE/NIRD_bkp/cordex-norway/stats_v3'
        inroot = inbase
    else: # home
        inbase = '.'
        inroot = inbase

    #file = '%s/%s_cmip6' % (inbase, stat_op)
    file = stat_op + '_cmip6'

    print('Inroot:', inbase)
    print('Output:', file + '.csv')

    if False: # os.path.exists(file + '.pkl'):
        print('Load', file + '.pkl')
        df = pd.read_pickle(file + '.pkl')
        df = pd.read_csv(file + '.csv', sep=';')
    else:
        stats, dims = average_data(inroot, file)
        print(stats.shape)
        print(dims['seasons'])
        print(dims['exps'])
        print(dims['stat_ops'])
        print(dims['variables'])
        df = create_dataframe(stats, dims, stat_op)

    print(df)
    #df.to_pickle(file + '.pkl')
    df.to_csv(file + '.csv', sep=';')
    print('File written:', file + '.csv')
