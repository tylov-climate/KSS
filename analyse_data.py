#!/usr/bin/env python
#
# Developed by Tyge Lovset, August 2020

import os
import glob
import netCDF4 as nc4
import numpy as np
import json
    

# MAIN

if __name__ == '__main__':

    inroot='/tos-project4/NS9076K/data/cordex-norway'
    seasons = ['s1', 's2', 's3', 's4', 'full']
    stat_ops = ['timmean', 'timvar']
    variables = ['tas', 'pr']
    
    summary = []
    for season in seasons:
        for op in stat_ops:
            for sub_path in glob.glob(inroot + '/' + season + '/' + op + '/*'):
                _var, _exper, _period = sub_path.split('_')
                for path in glob.glob(sub_path + '/*.nc'):
                    f = os.path.basename(path)
                    domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version, freq_id, var_id, create_ver_id, period, season, stat_op = f[:-3].split('_')
                    #print(f)
                    with nc4.Dataset(path) as src:
                        for ncvname, ncvar in src.variables.items():
                            if ncvname in variables:
                                data = ncvar[:]
                                value = np.mean(data)
                                summary.append({'domain_id': domain_id,
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
    output = 'kss_analysis.json'
    with open(output, 'w') as outfile:
        json.dump(summary, outfile, indent=4)
    
    print('Items in', output, ':', len(summary))
