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
import shutil

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


def make_ensemble_stats(inroot, stat_op):
    op = stat_op.split('-')[1]
    for dd in glob.glob(os.path.join(inroot, 'yseas%s/*' % op)):
        base = os.path.basename(dd)
        outdir = os.path.join(inroot, 'ens%s' % op)
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        outfile = os.path.join(outdir, base + '_ens%s.nc' % op)
        print('input:', dd)
        print('output:', outfile)

        if base.startswith('pr_'):
            cmd1 = 'cdo -O ens%s %s/*.nc %s' % (op, dd, 'tmp1.nc')
            cmd2 = 'cdo -O setattribute,pr@units="mm year-1" %s %s' % ('tmp1.nc', 'tmp2.nc')
            cmd3 = 'ncap2 -O -s "pr=31557600*pr" %s %s' % ('tmp2.nc', outfile)
            ret = os.system(cmd1)
            ret = os.system(cmd2)
            ret = os.system(cmd3)
        elif base.startswith('tas_'):
            cmd1 = 'cdo -O ens%s %s/*.nc %s' % (op, dd, 'tmp1.nc')
            cmd2 = 'cdo -O setattribute,tas@units="Celsius" %s %s' % ('tmp1.nc', 'tmp2.nc')
            cmd3 = 'ncap2 -O -s "tas=tas-273.15f" %s %s' % ('tmp2.nc', outfile)
            ret = os.system(cmd1)
            ret = os.system(cmd2)
            ret = os.system(cmd3)
        else:
            print('skipping %s folder...' % dd)

    if True:
        for ff in glob.glob(os.path.join(inroot, 'ens%s/*.nc' % op)):
            base = os.path.basename(ff)
            arr = base.split('_')
            if arr[3] == 'histo':
                continue
            var = arr[0]
            fhist = os.path.join(os.path.dirname(ff), '_'.join((arr[0], arr[1], '1951-2000_histo', arr[4])))
            outdir = os.path.join(inroot, 'ensdiff')
            outfile = os.path.join(outdir, base.replace('.nc', '_diff.nc'))
            print('computing diff:', outfile)

            os.makedirs(outdir, exist_ok=True)
            shutil.copyfile(ff, outfile)
            nc = nc4.Dataset(outfile, 'r+')
            nc_hist = nc4.Dataset(fhist)
            if var == 'tas':
                data = nc.variables[var][:] - nc_hist.variables[var][:]
            if var == 'pr':
                data = 100 * (nc.variables[var][:] - nc_hist.variables[var][:]) / nc_hist.variables[var][:]
            nc[var][:] = data
            nc.close()


# hist => 2005
# rcp4.5 start 2006

def make_stats(inroot, outroot, stat_op, periods):

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
    #periods = ((1951, 2000), (2031, 2060), (2071, 2100))
    periods = ((1971, 2000), (1985, 2014), (1991, 2020), (2041, 2070), (2071, 2100))
    
    #stat_ops = {'mean': 1, 'avg': 2, 'var': 3, 'std': 4, 'min': 5, 'max': 6, 'range': 7, 
    stat_ops = {'mean': 1, 'min': 2, 'max': 3, 'ens-mean': 4, 'ens-min': 5, 'ens-max': 6}
    try:
        stat_op = sys.argv[1]
        n = stat_ops[stat_op]
        if len(sys.argv) > 3:
            periods = [(int(sys.argv[i]), int(sys.argv[i+1])) for i in range(2, len(sys.argv), 2)]
    except:
        print('Usage: make_stats {mean | min | max | ens-mean | ens-min | ens-max} [intervals]')
        exit()


    uname = platform.uname()
    print(uname)
    if uname.system != 'Linux':
        print('Exit. Must be run under Linux because it needs CDO and NCO')
        exit()
    if '-tos' in uname.node: # NIRD or similar
        inroot = '/tos-project4/NS9076K/data/cordex-norway/EUR-11'
        outroot = '/tos-project4/NS9076K/data/cordex-norway/stats_v3'
    elif 'ppi-ext' in uname.node: # met.no
        inroot = '/lustre/storeC-ext/users/kin2100/NORCE/cordex-norway/EUR-11'
        outroot = '/lustre/storeC-ext/users/kin2100/NORCE/cordex-norway/stats_v3'
    elif uname.node == 'DESKTOP-H8NNHQA': # Home PC.
        inroot = '/mnt/j/DATA/EUR-11'
        outroot = '/mnt/c/Dev/DATA/cordex-norway/stats_v3'
    else:
        print("WTF")

    if stat_op.startswith('ens-'):
        make_ensemble_stats(outroot, stat_op)
    else:
    	make_stats(inroot, outroot, stat_op, periods)
