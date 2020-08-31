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

## ANALYSE2

def save_json_statistics_v1(inroot, output):
    periods, seasons, stat_ops, variables, models = [], [], [], [], []
    periods_r, seasons_r, stat_ops_r, variables_r, models_r = {}, {}, {}, {}, {}
    
    for sub_path in sorted(glob.glob(inroot + '/*/*/*')):
        for path in sorted(glob.glob(sub_path + '/*.nc')):
            f = os.path.basename(path)
            domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, freq_id, var_id, create_ver_id, period, season, stat_op = f[:-3].split('_')
            model_name = '_'.join([institute_id, model_id, ensemble_id, rcm_version])

            if period not in periods:
                periods.append(period)
            if season not in seasons:
                seasons.append(season)
            if stat_op not in stat_ops:
                stat_ops.append(stat_op)
            if var_id not in variables:
                variables.append(var_id)
            if model_name not in models:
                models.append(model_name)
                #print(model_name)

    periods = sorted(periods)
    seasons = sorted(seasons)
    stat_ops = sorted(stat_ops)
    variables = sorted(variables)
    models = sorted(models)

    for i in range(len(periods)):
        periods_r[periods[i]] = i
    for i in range(len(seasons)):
        seasons_r[seasons[i]] = i
    for i in range(len(stat_ops)):
        stat_ops_r[stat_ops[i]] = i
    for i in range(len(variables)):
        variables_r[variables[i]] = i
    for i in range(len(models)):
        models_r[models[i]] = i
    
    
    print('Dimensions:')
    print(periods)
    print(seasons)
    print(stat_ops)
    print(variables)
    print(len(models), 'models')
    table = np.zeros(shape=(len(periods), len(seasons), len(stat_ops), len(variables), len(models)), dtype=np.float32)
    
    print(table.shape)
    m = 0
    for sub_path in sorted(glob.glob(inroot + '/*/*/*')):
        #m += 1
        #if m > 10:
        #    break
        for path in sorted(glob.glob(sub_path + '/*.nc')):
            f = os.path.basename(path)
            domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, freq_id, var_id, create_ver_id, period, season, stat_op = f[:-3].split('_')
            model_name = '_'.join([institute_id, model_id, ensemble_id, rcm_version])

            with nc4.Dataset(path) as src:
                for ncvname, ncvar in src.variables.items():
                    if ncvname == var_id:
                        data = ncvar[:]
                        value = np.mean(data)
                        table[periods_r[period]][seasons_r[season]][stat_ops_r[stat_op]][variables_r[var_id]][models_r[model_name]] = value
                        print(model_name, period, season, stat_op, var_id, ':', value)
                            
    np.savez(output, periods=periods, seasons=seasons, stat_ops=stat_ops, variables=variables, models=models, table=table)
    
    
def get_statistics_v1(inroot, file):
    file += '.npz'
    if not os.path.exists(file):
        save_json_statistics_v1(inroot, file)
    
    with open(file, 'r') as f:
        stats = np.load(file)
    print(stats.files)
    return stats
    

def make_plots(stats):
    pass

'''
def regression_plot(tas_data, pr_data):
    fig = plt.figure(figsize=(18, 10))
    n = 4
    pos = [2, n, 0]
    for i in range(0, n):
        # plot one week pr / tas 
        pos[2] = i + 1
        ax = fig.add_subplot(*pos)
        t = tas[t1, pix[i][0], :].flatten()
        p = pr[t1, pix[i][0], :].flatten()
        data = pd.DataFrame({'TAS'})
        sns.regplot(x=t, y=p, fit_reg=True, ax=ax)
    
        pos[2] = i + 1 + n
        ax = fig.add_subplot(*pos)
        t = tas[t1, :, pix[i][1]].flatten()
        p = pr[t1, :, pix[i][1]].flatten()
        sns.regplot(x=t, y=p, fit_reg=True, ax=ax)

    plt.show()
''' 

# MAIN

if __name__ == '__main__':
    inroot='/tos-project4/NS9076K/data/cordex-norway/stats_v1'
    json_file = 'kss_analysis'
    
    #stats = get_statistics_v1(inroot, json_file)
    #print('Items in', json_file, ':', len(stats))
    
    stats = get_statistics_v1(inroot, json_file)
    print(stats['models'])
    print(stats['seasons'])
    print(stats['table'][1][3][0][1])