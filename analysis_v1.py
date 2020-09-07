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



def save_json_statistics_v1(inroot, output):
    seasons = ['s1', 's2', 's3', 's4', 'full']
    stat_ops = ['timmean', 'timvar']
    variables = ['tas', 'pr']
    
    stats = []
    for season in seasons:
        for op in stat_ops:
            for sub_path in sorted(glob.glob(inroot + '/' + season + '/' + op + '/*')):
                base = os.path.basename(sub_path)
                #_var, _exper, _period = base.split('_')
                print(base)
                for path in sorted(glob.glob(sub_path + '/*.nc')):
                    f = os.path.basename(path)
                    domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, freq_id, var_id, create_ver_id, period, season, stat_op = f[:-3].split('_')
                    #print(f)
                    with nc4.Dataset(path) as src:
                        for ncvname, ncvar in src.variables.items():
                            if ncvname in variables:
                                data = ncvar[:]
                                value = np.mean(data)
                                stats.append({'domain_id': domain_id,
                                                'institute_id': institute_id,
                                                'model_id': model_id,
                                                'experiment_id': experiment_id,
                                                'ensemble_id': ensemble_id,
                                                'source_id': source_id,
                                                'rcm_version': rcm_version,
                                                'freq_id': freq_id,
                                                'create_ver_id': create_ver_id,
                                                'period': period,
                                                'season': season,
                                                'stat_op': stat_op,
                                                'var_id': var_id,
                                                'value': str(value),
                                                })
    with open(output, 'w') as f:
        json.dump(stats, f, indent=4)
    return stats
    
    
def get_statistics_v1(inroot, json_file):
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            print('loading prestored results...')
            stats = json.load(f)
    else:
        print('creating results...')
        stats = save_json_statistics_v1(inroot, json_file)
    return stats
    

def make_plots(stats):
    data = {}
    for exp in ['rcp85']:
        data[exp] = {}
        for stat_op in ['timmean']:
            data[exp][stat_op] = {}
            for season in ['s4']:
                data[exp][stat_op][season] = {}
                for period in ['2']:
                    data[exp][stat_op][season][period] = {}
                    for var in ['pr', 'tas']:
                        arr = [e for e in stats if e['var_id'] == var and e['stat_op'] == stat_op and e['experiment_id'] == exp  ] # and e['season'] == 's2' and e['period'] == '3'
                        #data[exp][stat_op][season][period][var] = arr
                        print(exp, stat_op, season, period, var, ':')
                        for v in arr:
                            print('  ', v)
                        #regression_plot(data[exp][stat_op][season][period])
    #for e in data:
    #    print(e['institute_id'], e['model_id'], e['ensemble_id'], e['rcm_version'],':', e['value'], e['experiment_id'])

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
    json_file = 'kss_analysis.json'
    
    stats = get_statistics_v1(inroot, json_file)
    print('Items in', json_file, ':', len(stats))
    
    make_plots(stats)
    
            
