#!/usr/bin/env python
#
# Developed by Tyge Lovset, August 2020

import os
import sys
import glob
import datetime as dt
from dateutil.relativedelta import relativedelta
import netCDF4 as nc4
import uuid

'''
 :institution = "Helmholtz-Zentrum Geesthacht, Climate Service Center, Max Planck Institute for Meteorology" ;
                :institute_id = "MPI-CSC" ;
                :experiment_id = "rcp26" ;
                :source = "MPI-CSC-REMO2009" ;
                :model_id = "MPI-CSC-REMO2009" ;
                :contact = "gerics-cordex@hzg.de" ;
                :comment = "CORDEX Europe RCM REMO 0.11 deg EUR-11" ;
                :references = "http://www.remo-rcm.de/" ;
                :initialization_method = 1 ;
                :physics_version = 1 ;
                :tracking_id = "956c3850-95bf-4434-8363-ef8f6f01bcf5" ;
                :CORDEX_domain = "EUR-11" ;
                :driving_experiment = "MPI-M-MPI-ESM-LR, rcp26, r1i1p1" ;
                :driving_model_id = "MPI-M-MPI-ESM-LR" ;
                :driving_model_ensemble_member = "r1i1p1" ;
                :driving_experiment_name = "rcp26" ;
                :rcm_version_id = "v1" ;
                :product = "output" ;
                :experiment = "RCP2.6" ;
                :frequency = "day" ;
                :creation_date = "2016-02-02T14:39:34Z" ;
                :history = "Thu Aug 20 12:29:55 2020: ncks -d rlon,196,303 -d rlat,279,402 /tos-project4/NS9076K/data/cordex/output/EUR-11/MPI-CSC/MPI-M-MPI-ESM-LR/rcp26/r1i1p1/REMO2009/v1/day/tas/v20160525/tas_EUR-11_MPI-M-MPI-ESM-LR_rcp26_r1i1p1_MPI-CSC-REMO2009_v1_day_20660101-20701231.nc -O tmp.nc\n",
                        "2016-02-02T14:39:34Z CMOR rewrote data to comply with CF standards and CORDEX requirements." ;
                :Conventions = "CF-1.4" ;
                :project_id = "CORDEX" ;
                :table_id = "Table day (March 2015) 6f55fe4ad23cded422652f83a747ce32" ;
                :title = "MPI-CSC-REMO2009 model output prepared for CORDEX RCP2.6" ;
                :modeling_realm = "atmos" ;
                :realization = 1 ;
                :cmor_version = "2.9.1" ;
                :NCO = "4.6.9" ;

MPI-CSC/MPI-M-MPI-ESM-LR/rcp26/r1i1p1/REMO2009/v1/day/pr/v20160525
         pr_EUR-11_MPI-M-MPI-ESM-LR_rcp26_r1i1p1_MPI-CSC-REMO2009_v1_day_20310101-20351231.nc

'''

def find_period(d1, d2, periods):
    i = 0
    for p in periods:
        if p[0] <= d1.year <= d2.year <= p[1]: return i
        elif (p[0] <= d1.year <= p[1]) or (p[0] <= d2.year <= p[1]): return -2
        i += 1
    return -1


def make_stats(inroot, outroot, seasons, season, stat_op, periods=((1951, 2000), (2031, 2060), (2071, 2100))):
    if inroot[-1] != '/':
        inroot += '/'
    if not os.path.isdir(outroot):
        os.makedirs(outroot)

    for dd in glob.glob(os.path.join(inroot, '*/*/*/*/*/*/day/*/*')):
        subpath = dd.replace(inroot, '')
        institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version_id, freq_id, var_id, create_ver_id = subpath.split('/')
        #print(institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version_id, freq_id, var_id, create_ver_id)

        period_map = {}
        for file in glob.glob(os.path.join(dd, '*.nc')):
            base = os.path.basename(file)
            dt1 = dt.datetime.strptime(base[-20:-12], '%Y%m%d')
            dt2 = dt.datetime.strptime(base[-11:-3], '%Y%m%d')
            p = find_period(dt1, dt2, periods)
            if p == -2:
                print('Warning: skipping file partially in period:', base)
                continue
            if p == -1:
                continue
            if p in period_map:
                period_map[p].append(file)
            else:
                period_map[p] = [file]

        for p, period_files in period_map.items():
            #base = os.path.basename(period_files[0])
            for op in ('timmean', 'timvar'):
                if stat_op == 'all' or stat_op == op:
                    for s, m in seasons.items():
                        if s != 'all' and (season == 'all' or season == s):
                            period_id = '%d-%d' % (periods[p][0], periods[p][1])
                            experiment = '%s_%s_%s_%s_%s_%s_%s_%s_%s_%s' % ('EUR-11', institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version_id, freq_id, var_id, create_ver_id)
                            outfile = os.path.join(outroot, '%s/%s_%s_%s_%s' % (s, var_id, op, period_id, experiment_id[:5]),
                                                   experiment + '_%s_%s_%s.nc' % (op, s, period_id))

                            if os.path.isfile(outfile):
                                print('    ...exists')
                                continue
                            tmpfile = os.path.join(outroot, str(uuid.uuid4()) + '.nc')
                            infiles = os.path.join(inroot, period_files[0])
                            for f in period_files[1:]:
                                infiles += ' ' + os.path.join(inroot, f)
                            if s == 'FULL':
                                cmd = "cdo %s -cat '%s' %s" % (op, infiles, tmpfile)
                            else:
                                cmd = "cdo %s -selseason,%s -cat '%s' %s" % (op, s, infiles, tmpfile)
                            ret = os.system(cmd)

                            if ret == 0:
                                odir = os.path.dirname(outfile)
                                if not os.path.isdir(odir):
                                    os.makedirs(odir)
                                    print('Created dir:', odir)
                                os.rename(tmpfile, outfile)
                                print('Created:', outfile)
                            else:
                                print('Return status:', ret)


# Create mean and variance average data over all the periods, seasons (full = all seasons)

if __name__ == '__main__':
    periods = ((1951, 2000), (2031, 2060), (2071, 2100))
    seasons = {'all': -1, 'FULL': 0, 'MAM': 3, 'JJA': 6, 'SON': 9, 'DJF': 12}
    stat_ops = {'all': 0, 'timmean': 1, 'timavg': 2, 'timvar': 3, 'timstd': 4, 'timmin': 5, 'timmax': 6, 'timrange': 7}
    try:
        season = sys.argv[1]
        stat_op = sys.argv[2]
        n = seasons[season]
        n = stat_ops[stat_op]
        if len(sys.argv) > 4:
            periods = [(int(sys.argv[i]), int(sys.argv[i+1])) for i in range(3, len(sys.argv), 2)]
    except:
        print('Usage: make_stats {all|FULL|MAM|JJA|SON|DJF} {all|timmean|timavg|timvar|timstd|timmin|timmax|timrange} [intervals]')
        exit()

    make_stats(
        inroot='/tos-project4/NS9076K/data/cordex-norway/EUR-11',
        outroot='/tos-project4/NS9076K/data/cordex-norway/stats_v2',
        seasons=seasons,
        season=season,
        stat_op=stat_op,
        periods=periods
    )
