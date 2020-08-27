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



def save_json_statistics(inroot, output):
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
    
    
def get_statistics(inroot, json_file):
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            stats = json.load(f)
    else:
        stats = save_json_statistics(inroot, json_file)
    return stats
    

def make_plots(stats):
    tas_n, pr_n = 0, 0
    for exp in ('historical', 'rcp26', 'rcp45', 'rcp85'):
        for stat_op in ('timmean', 'timvar'):
            tas_data = [e for e in stats if e['var_id'] == 'tas' and e['stat_op'] == stat_op and e['experiment_id'] == exp]
            pr_data = [e for e in stats if e['var_id'] == 'pr' and e['stat_op'] == stat_op and e['experiment_id'] == exp]
            tas_n += len(tas_data)
            pr_n += len(pr_data)
            print(exp, stat_op, ':', len(tas_data), len(pr_data))
            #for e in data:
            #    print(e['institute_id'], e['model_id'], e['ensemble_id'], e['rcm_version'],':', e['value'], e['experiment_id'])
    print('tas, pr, sum:', tas_n, pr_n, tas_n + pr_n)



# MAIN

if __name__ == '__main__':
    inroot='/tos-project4/NS9076K/data/cordex-norway'
    json_file = 'kss_analysis.json'
    
    stats = get_statistics(inroot, json_file)
    print('Items in', json_file, ':', len(stats))
    
    make_plots(stats)
    
            
