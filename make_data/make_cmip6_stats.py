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

MPI-CSC/MPI-M-MPI-ESM-LR/rcp26/r1i1p1/REMO2009/v1/day/pr/v20160525/
pr_EUR-11_MPI-M-MPI-ESM-LR_rcp26_r1i1p1_MPI-CSC-REMO2009_v1_day_20310101-20351231.nc

cmip6:
  /projects/NS9001K/tylo/DATA/cordex-norway/EUR-11-CMIP6/  # root
  KNMI/NorESM2-MM/ssp370/r1i1p1f1/RACMO23E/v1-r1/day/tas/  # subpath
  tas_Norway-EUR-12_NorESM2-MM_ssp370_r1i1p1f1_KNMI_RACMO23E_v1-r1_day_20150101-20151231.nc
'''

def find_period(d1, d2, periods):
    i = 0
    for p in periods:
        if p[0] <= d1.year <= d2.year <= p[1]:
            return i, 0
        elif (p[0] <= d1.year <= p[1]) or (p[0] <= d2.year <= p[1]):
            return i, -2
        i += 1
    return 0, -1


def create_diff_file(var, infile, reffile, outfile):
    outdir = os.path.dirname(outfile)
    os.makedirs(outdir, exist_ok=True)
    shutil.copyfile(infile, outfile)
    with nc4.Dataset(reffile) as nc_ref:
        with nc4.Dataset(outfile, 'r+') as nc:
            if var == 'tas':
                data = nc.variables[var][:] - nc_ref.variables[var][:]
            if var == 'pr':
                data = 100 * (nc.variables[var][:] - nc_ref.variables[var][:]) / nc_ref.variables[var][:]
            nc[var][:] = data


def make_ensemble_stats(inroot, outroot, interval, stat_op, ens_op, periods):
    # loop files
    op = interval + stat_op
    #if False:
    for dd in glob.glob(os.path.join(inroot, '%s/*' % op)):
        base = os.path.basename(dd)
        outdir = os.path.join(outroot, 'ens%s_%s' % (ens_op, op))
        if not args.dry and not os.path.isdir(outdir):
            os.makedirs(outdir)
        outfile = os.path.join(outdir, base + '_ens%s.nc' % ens_op)
        print('input:', dd)
        print('output:', outfile)

        if base.startswith('pr_'):
            cmd1 = cdo + ' -L -O ens%s %s/*.nc %s' % (ens_op, dd, 'tmp1.nc')
            cmd2 = cdo + ' -L -O setattribute,pr@units="mm year-1" %s %s' % ('tmp1.nc', 'tmp2.nc')
            cmd3 = 'ncap2 -O -s "pr=31557600*pr" %s %s' % ('tmp2.nc', outfile)
            if not args.dry:
                ret = os.system(cmd1)
                ret = os.system(cmd2)
                ret = os.system(cmd3)
        elif base.startswith('tas_'):
            cmd1 = cdo + ' -L -O ens%s %s/*.nc %s' % (ens_op, dd, 'tmp1.nc')
            cmd2 = cdo + ' -L -O setattribute,tas@units="Celsius" %s %s' % ('tmp1.nc', 'tmp2.nc')
            cmd3 = 'ncap2 -O -s "tas=tas-273.15f" %s %s' % ('tmp2.nc', outfile)
            if not args.dry:
                ret = os.system(cmd1)
                ret = os.system(cmd2)
                ret = os.system(cmd3)
        else:
            print('skipping %s folder...' % dd)

    if os.path.isfile('tmp1.nc'):
        os.remove('tmp1.nc')
    if os.path.isfile('tmp2.nc'):
        os.remove('tmp2.nc')

    create_ensdiff_files(outroot, interval, stat_op, ens_op)


def create_ensdiff_files(outroot, interval, stat_op, ens_op):
    #
    # Compute differences for all periods against all ref-periods
    #
    m = {
        '1971-2020':0, '1971-2000':1, '1991-2020':2, '2041-2070':3, '2071-2100':4,
        'histo':0, 'ssp370':3,
    }
    op = interval + stat_op
    outdir = os.path.join(outroot, 'ensdiff_%s%s' % (interval, ens_op))

    for ref in glob.glob(os.path.join(outroot, 'ens%s_%s/*.nc' % (ens_op, op))):
        rbase = os.path.basename(ref)
        rpart = rbase.split('_')
        rvar = rpart[0]
        for f in glob.glob(os.path.join(outroot, 'ens%s_%s/*.nc' % (ens_op, op))):
            base = os.path.basename(f)
            part = base.split('_')
            var = part[0]
            period = part[2]
            if f == ref or var != rvar or m[rpart[2]] > m[period]:
                continue
            if part[2] == rpart[2]:
                outfile = os.path.join(outdir, base.replace('.nc', '_diff_%s.nc' % rpart[3]))
            else:
                outfile = os.path.join(outdir, base.replace('.nc', '_diff_%s.nc' % rpart[2]))

            print('diff:', outfile)
            if not args.dry:
                create_diff_file(var, f, ref, outfile)


def create_modeldiff_files(outroot, interval, stat_op, ens_op):
    #
    # Compute differences for all periods against all ref-periods
    #
    m = {
        '1971-2020':0, '1971-2000':1, '1991-2020':2, '2041-2070':3, '2071-2100':4,
        'histo':0, 'ssp370':3,
    }
    op = interval + stat_op
    outdir = os.path.join(outroot, 'modeldiff_%s%s' % (interval, ens_op))

    for ref in glob.glob(os.path.join(outroot, 'ens%s_%s/*.nc' % (ens_op, op))):
        rbase = os.path.basename(ref)
        rpart = rbase.split('_')
        rvar = rpart[0]
        for f in glob.glob(os.path.join(outroot, 'ens%s_%s/*.nc' % (ens_op, op))):
            base = os.path.basename(f)
            part = base.split('_')
            var = part[0]
            period = part[2]
            if f == ref or var != rvar or m[rpart[2]] > m[period]:
                continue
            if part[2] == rpart[2]:
                outfile = os.path.join(outdir, base.replace('.nc', '_diff_%s.nc' % rpart[3]))
            else:
                outfile = os.path.join(outdir, base.replace('.nc', '_diff_%s.nc' % rpart[2]))

            print('diff:', outfile)
            if not args.dry:
                create_diff_file(var, f, ref, outfile)

# hist => 2005
# rcp4.5 start 2006
# ssp370 start 2015

def make_stats(inroot, outroot, interval, stat_op, periods, institute):
    print(inroot)
    if inroot[-1] != '/':
        inroot += '/'
    op = interval + stat_op
    outroot_op = os.path.join(outroot, op)
    if not os.path.isdir(outroot_op):
        os.makedirs(outroot_op)

    for per in [periods[int(i)] for i in args.periods.split(',')]:
        filemap = {}
        period_id = '%d-%d' % (per[0], per[1])
        tmpdir = os.path.join(outroot, 'temp_%s_%s_%s' % (institute, op, period_id))
        has_create_ver = args.institute in ('CLMcom-BTU', 'CLMcom-KIT')

        if has_create_ver:
            subdirs = '/*/*/*/*/*/day/*/*'
        else:
            subdirs = '/*/*/*/*/*/day/*'

        for dd in glob.glob(os.path.join(inroot, institute + subdirs)):
            print(dd)
            subpath = dd.replace(inroot, '')
            if has_create_ver:
                institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version_id, freq_id, var_id, create_ver_id = subpath.split('/')
            else:
                institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version_id, freq_id, var_id = subpath.split('/')
                create_ver_id = 'v00000000'
            #print(institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version_id, freq_id, var_id, create_ver_id)
            if args.windhouse:
                if var_id != 'sfcWind':
                    continue
            else:
                if var_id != 'pr' and var_id != 'tas':
                    continue

            # Re-categorize 'rcp45' for years <= 2020 to 'historical',
            # and skip rcp26 and rcp85 for years <= 2020
            expid = experiment_id
            if per[1] <= 2020:
                if experiment_id == 'ssp370':
                    expid = 'historical'
                elif experiment_id != 'historical':
                    continue

            experiment = '%s_%s_%s_%s_%s_%s_%s_%s_%s_%s' % (var_id, 'EUR-11', institute_id, model_id, expid, ensemble_id, source_id, rcm_version_id, op, create_ver_id)
            outfile = os.path.join(outroot_op, '%s_%s_%s_%s' % (var_id, op, period_id, expid[:5]), experiment + '_%s.nc' % period_id)
            input_files = []

            if not args.dry and os.path.isfile(outfile):
                print('  ', outfile, '...exists')
                continue

            for file in glob.glob(os.path.join(dd, '*.nc')):
                base = os.path.basename(file)

                dt0 = dt.datetime.strptime(base[-20:-12], '%Y%m%d')
                dt1 = dt.datetime.strptime(base[-11:-3], '%Y%m%d')
                if dt1.year < per[0] or dt0.year > per[1]:
                    continue
                if dt0.year >= per[0] and dt1.year <= per[1]:
                    mfile = file
                else:
                    # Create tmpfiles with data inside the selected date range only.
                    tmpfile = os.path.join(tmpdir, base + '-TRUNC-%s.nc' % period_id)
                    mfile = tmpfile
                    cmd = cdo + " -L copy -seldate,%d-01-01,%d-12-31 '%s' %s" % (per[0], per[1], file, tmpfile)
                    if not args.dry:
                        if not os.path.isdir(tmpdir):
                            os.makedirs(tmpdir)
                        ret = os.system(cmd)

                input_files.append(mfile)

            if len(input_files) == 0:
                continue
            try:
                filemap[outfile] += input_files
            except:
                filemap[outfile] = input_files

        for outfile, input_files in filemap.items():
            odir = os.path.dirname(outfile)
            oname = os.path.basename(outfile)
            print("CDO", op, period_id)
            #print('  =>', oname)
            print('  =>', outfile)
            # Temp outfile in root output, to be moved
            tmpfile = os.path.join(outroot, oname)
            infiles_str = ''
            for f in sorted(input_files):
                print('    f:', os.path.basename(f))
                infiles_str += ' ' + f
            # Concatenate all files
            cmd = cdo + " -L %s -cat '%s' %s" % (op, infiles_str, tmpfile)
            if args.dry:
                continue
            ret = os.system(cmd)

            # modify experiment attribute to 'historical' for rcp45 years < 2021
            if expid != experiment_id:
                os.system('ncatted -a experiment_id,global,m,c,historical -O %s %s.nc' % (tmpfile, tmpfile))
                os.remove(tmpfile)
                os.rename(tmpfile + '.nc', tmpfile)

            '''
            # change to mm/year
            if var_id == 'pr' and ret == 0:
                if 0 == os.system('ncap2 -s "pr=31557600*pr" %s %s.nc' % (tmpfile, tmpfile)):
                    if 0 == os.system('ncatted -O -a units,pr,m,c,"mm/year" %s.nc %s' % (tmpfile, tmpfile)):
                        os.remove(tmpfile + '.nc')
            '''

            if ret == 0:
                if not os.path.isdir(odir):
                    os.makedirs(odir)
                os.rename(tmpfile, outfile)

        if not args.dry and os.path.isdir(tmpdir):
            shutil.rmtree(tmpdir)

# cdo timmean ...

def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    print('make_stats.py - make statistics data for KSS Klima 2100')
    print('')

    parser.add_argument(
        '-w', '--windhouse', action='store_true',
        help='Wind house data'
    )
    parser.add_argument(
        '--dry',  action='store_true',
        help='Only print the operations'
    )
    parser.add_argument(
        '-e', '--ensemble', action='store_true',
        help='Create ensemble statistic files over all models'
    )
    parser.add_argument(
        '-p', '--periods', default='1,2,3,4',
        help='Periods comma-separated num: (' + ', '.join(['%d:%d-%d' % (i, periods[i][0], periods[i][1]) for i in range(len(periods))]) + ')'
    )
    parser.add_argument(
        '-r', '--ref-period', default=2,
        help='Ref. period (use with -e): 2=default (' + ', '.join(['%d:%d-%d' % (i, periods[i][0], periods[i][1]) for i in range(len(periods))]) + ')'
    )
    parser.add_argument(
        '-s', '--stat', required=True,
        help='stat operation: (' + ', '.join([k for k in stat_ops.keys()]) + ')'
    )
    parser.add_argument(
        '--interval', default='yseas',
        help='statstics interval: (yseas[=default], ymon)'
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
        '-t', '--institute', default=None,
        help='Input institute name: default "*"'
    )
    return parser.parse_args()

# Create mean, min, max or std data over all the periods, seasons (full = all seasons)

if __name__ == '__main__':
    #periods = ((1951, 2000), (2031, 2060), (2071, 2100)) # OLD MIPS5
    #periods = ((1971, 2000),                            (2041, 2070), (2071, 2100)) # CMIP5
    #periods = ((1985, 2014), (1991, 2020),              (2041, 2070), (2071, 2100)) # CMIP6
    periods = ((1971, 2020), (1971, 2000), (1991, 2020), (2041, 2070), (2071, 2100)) # 5+6
    stat_ops = {'mean': 1, 'min': 2, 'max': 3, 'std': 4}
    cdo = 'cdo'

    uname = platform.uname()
    #print(uname)

    args = parse_args()
    stat_op = args.stat
    n = stat_ops[stat_op]
    institute = args.institute

    if uname.system != 'Linux':
        print('Exit. Must be run under Linux because it needs CDO and NCO')
        exit()
    if '-nird' in uname.node: # NIRD
        if args.windhouse:
            inbase = '/projects/NS9001K/tylo/DATA/cordex'
            inroot = inbase + '/EUR-11-CMIP6'
            outroot = inbase + '/stats_windhouse'
        else:
            #inroot = '/projects/NS9001K/tylo/DATA/cordex-norway/EUR-11-CMIP6'
            #outroot = '/datalake/NS9001K/tylo/kin2100/stats_cmip6'
            inroot='/datalake/NS9001K/tylo/kin2100/NOR-11-CMIP6'
            outroot = '/datalake/NS9001K/tylo/kin2100/stats_cmip6'
    elif 'norceresearch' in uname.node: # NORCE HPC
        inbase = os.path.expanduser('~') + '/proj/kss/cordex-norway'
        inroot = inbase + '/EUR-11-CMIP6'
        outroot = inbase + '/stats_cmip6'
    elif 'ppi-ext' in uname.node: # met.no
        inbase = '/lustre/storeC-ext/users/kin2100/NORCE/cordex-norway'
        inroot = inbase + '/EUR-11-CMIP6'
        outroot = inbase + '/stats_cmip6'
    else: # work PC
        inroot = 'C:/Dev/DATA/EUR-11-CMIP6'
        outroot = 'C:/Dev/DATA/cordex-norway/stats_cmip6'

    if args.ensemble:
        #print('Reference period:', periods[int(args.ref_period)])
        make_ensemble_stats(outroot, outroot, args.interval, stat_op, 'mean', periods)
    else:
        if institute is None:
            print("missing argument: -t institute")
            exit()
        print(inroot)
        print(outroot)
        make_stats(inroot, outroot, args.interval, stat_op, periods, institute)
