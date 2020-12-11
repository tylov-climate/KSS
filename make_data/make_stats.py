#!/usr/bin/env python
#
# Developed by Tyge Lovset, August 2020

import os
import platform
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


def make_ensemble_stats(inroot):
    for dd in glob.glob(os.path.join(inroot, 'yseasmean/*')):
        base = os.path.basename(dd)
        for op in ('mean'):
            outdir = os.path.join(inroot, 'ens%s' % op)
            if not os.path.isdir(outdir):
                os.makedirs(outdir)
            outfile = os.path.join(outdir, base + '_ens%s.nc' % op)
            if os.path.isfile(outfile):
                print(outfile, '    ...exists')
                #return
            if base[:3] == 'pr_':
                ret = os.system('cdo -O ens%s -chunit,"kg m-2 s-1","mm year-1" %s/*.nc %s' % (op, dd, 'tmp.nc'))
                ret = os.system('ncap2 -O -s "pr=31557600*pr" %s %s' % ('tmp.nc', outfile))
            else:
                ret = os.system("cdo -O ens%s %s/*.nc %s" % (op, dd, outfile))

    if True:
        for ff in glob.glob(os.path.join(inroot, 'ensmean/*.nc')):
            base = os.path.basename(ff)
            arr = base.split('_')
            if arr[3] == 'histo':
                continue
            print('computing diff:', ff)
            fhist = os.path.join(os.path.dirname(ff), '_'.join((arr[0], arr[1], '1951-2000_histo', arr[4])))
            outfile = os.path.join(inroot, 'ensdiff', '_'.join((arr[0], 'ensdiff', arr[2], arr[3])) + '.nc')

            nc = nc4.Dataset(ff, 'r+')
            nc_hist = nc4.Dataset(fhist)
            var = 100 * (nc.variables[arr[0]][:] - nc_hist.variables[arr[0]][:])
            if arr[0] == 'pr':
                var /= nc_hist.variables[arr[0]][:]
            nc[arr[0]][:] = var
            nc.close()



def make_stats(inroot, outroot, stat_op, periods=((1951, 2000), (2031, 2060), (2071, 2100))):
    print(inroot)
    if inroot[-1] != '/':
        inroot += '/'
    outroot = os.path.join(outroot, 'yseas%s' % stat_op)
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
            op = 'yseas' + stat_op
            period_id = '%d-%d' % (periods[p][0], periods[p][1])
            experiment = '%s_%s_%s_%s_%s_%s_%s_%s_%s_%s' % (var_id, 'EUR-11', institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version_id, op, create_ver_id)
            outfile = os.path.join(outroot, '%s_%s_%s_%s' % (var_id, op, period_id, experiment_id[:5]), experiment + '_%s.nc' % period_id)

            if os.path.isfile(outfile):
                print('    ...exists')
                continue
            tmpfile = os.path.join(outroot, str(uuid.uuid4()) + '.nc')
            infiles = os.path.join(inroot, period_files[0])
            for f in period_files[1:]:
                infiles += ' ' + os.path.join(inroot, f)

            cmd = "cdo %s -cat '%s' %s" % (op, infiles, tmpfile)
            ret = os.system(cmd)
            '''
            if var_id == 'pr' and ret == 0:
                if 0 == os.system('ncap2 -s "pr=31557600*pr" %s %s.nc' % (tmpfile, tmpfile)):
                    if 0 == os.system('ncatted -O -a units,pr,m,c,"mm/year" %s.nc %s' % (tmpfile, tmpfile)):
                        os.remove(tmpfile + '.nc')
            '''
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
    stat_ops = {'mean': 1, 'avg': 2, 'var': 3, 'std': 4, 'min': 5, 'max': 6, 'range': 7, 'ensemble': 8}
    try:
        stat_op = sys.argv[1]
        n = stat_ops[stat_op]
        if len(sys.argv) > 3:
            periods = [(int(sys.argv[i]), int(sys.argv[i+1])) for i in range(2, len(sys.argv), 2)]
    except:
        print('Usage: make_stats {mean|avg|var|std|min|max|range} [intervals]')
        exit()

    uname = platform.uname()
    if uname[0] != 'Linux':
        print('Exit. Must be run under Linux because it needs CDO and NCO')
        exit()
    if '-tos' in uname[1]: # NIRD or similar
        inroot = '/tos-project4/NS9076K/data/cordex-norway/EUR-11'
        outroot = '/tos-project4/NS9076K/data/cordex-norway/stats_v3'
    elif uname[1] == 'DESKTOP-H8NNHQA': # Home PC.
        inroot = '/mnt/j/DATA/EUR-11'
        outroot = '/mnt/c/Dev/DATA/cordex-norway/stats_v3'

    #if stat_op == 'ensemble':
    #    make_ensemble_stats(outroot)
    #else:
    make_stats(inroot, outroot, stat_op, periods)
