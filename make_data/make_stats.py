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
        if p[0] <= d1.year <= d2.year <= p[1]:
            return i, 0
        elif (p[0] <= d1.year <= p[1]) or (p[0] <= d2.year <= p[1]):
            return i, -2
        i += 1
    return 0, -1


def make_ensemble_stats(inroot, interval, stat_op, ref_per):
    op = interval + stat_op
    yper = '' if interval == 'yseas' else interval
    for dd in glob.glob(os.path.join(inroot, '%s/*' % op)):
        base = os.path.basename(dd)
        outdir = os.path.join(inroot, 'ens%s%s' % (yper, stat_op))
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        outfile = os.path.join(outdir, base + '_ens%s.nc' % stat_op) # stat_op not needed: could use just '_ens.nc'
        print('input:', dd)
        print('output:', outfile)

        if base.startswith('pr_'):
            cmd1 = cdo + ' -L -O ens%s%s %s/*.nc %s' % (yper, stat_op, dd, 'tmp1.nc')
            cmd2 = cdo + ' -L -O setattribute,pr@units="mm year-1" %s %s' % ('tmp1.nc', 'tmp2.nc')
            cmd3 = 'ncap2 -O -s "pr=31557600*pr" %s %s' % ('tmp2.nc', outfile)
            ret = os.system(cmd1)
            ret = os.system(cmd2)
            ret = os.system(cmd3)
        elif base.startswith('tas_'):
            cmd1 = cdo + ' -L -O ens%s%s %s/*.nc %s' % (yper, stat_op, dd, 'tmp1.nc')
            cmd2 = cdo + ' -L -O setattribute,tas@units="Celsius" %s %s' % ('tmp1.nc', 'tmp2.nc')
            cmd3 = 'ncap2 -O -s "tas=tas-273.15f" %s %s' % ('tmp2.nc', outfile)
            ret = os.system(cmd1)
            ret = os.system(cmd2)
            ret = os.system(cmd3)
        else:
            print('skipping %s folder...' % dd)
    try:
        os.remove('tmp1.nc')
        os.remove('tmp2.nc')
    except:
        pass
    
    if True:
        for ff in glob.glob(os.path.join(inroot, 'ens%s%s/*.nc' % (yper, stat_op))):
            base = os.path.basename(ff)
            part = base.split('_')
            if part[3] == 'histo':
                continue
            var = part[0]
            # fhist ref?
            fhist = os.path.join(os.path.dirname(ff), '_'.join((part[0], part[1], '%d-%d_histo' % (ref_per[0], ref_per[1]), part[4])))
            outdir = os.path.join(inroot, 'ens%sdiff' % yper)
            outfile = os.path.join(outdir, base.replace('.nc', '_diff.nc'))
            print('computing diff:', outfile)

            os.makedirs(outdir, exist_ok=True)
            shutil.copyfile(ff, outfile)
            with nc4.Dataset(outfile, 'r+') as nc:
                nc_hist = nc4.Dataset(fhist)
                if var == 'tas':
                    data = nc.variables[var][:] - nc_hist.variables[var][:]
                if var == 'pr':
                    data = 100 * (nc.variables[var][:] - nc_hist.variables[var][:]) / nc_hist.variables[var][:]
                nc[var][:] = data

# hist => 2005
# rcp4.5 start 2006

def make_stats(inroot, outroot, interval, stat_op, periods, modelname):
    print(inroot)
    if inroot[-1] != '/':
        inroot += '/'
    op = interval + stat_op
    outroot = os.path.join(outroot, op)
    if not os.path.isdir(outroot):
        os.makedirs(outroot)

    for dd in glob.glob(os.path.join(inroot, modelname + '/*/*/*/*/*/day/*/*')):
        subpath = dd.replace(inroot, '')
        institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version_id, freq_id, var_id, create_ver_id = subpath.split('/')
        #print(institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version_id, freq_id, var_id, create_ver_id)
        if not (var_id == 'pr' or var_id == 'tas'):
            continue
        for per in periods:
            period_files = []
            tmp_files = []

            # Re-categorize 'rcp45' for years < 2022 to 'historical',
            # and skip rcp26 and rcp85 for years < 2022
            expid = experiment_id
            if per[1] <= 2020:
                if experiment_id == 'rcp45':
                    expid = 'historical'
                elif experiment_id != 'historical':
                    continue

            period_id = '%d-%d' % (per[0], per[1])
            experiment = '%s_%s_%s_%s_%s_%s_%s_%s_%s_%s' % (var_id, 'EUR-11', institute_id, model_id, expid, ensemble_id, source_id, rcm_version_id, op, create_ver_id)
            outfile = os.path.join(outroot, '%s_%s_%s_%s' % (var_id, op, period_id, expid[:5]), experiment + '_%s.nc' % period_id)
            odir = os.path.dirname(outfile)
            oname = os.path.basename(outfile)
            
            if not dry and os.path.isfile(outfile):
                print('    ...exists')
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
                    #tmpfile = os.path.join(outroot, str(uuid.uuid4()) + '.nc')
                    tmpfile = os.path.join(outroot, base + '-TRUNCATED-%s.nc' % period_id)
                    tmp_files.append(tmpfile)
                    mfile = tmpfile
                    cmd = cdo + " -L copy -seldate,%d-01-01,%d-12-31 '%s' %s" % (per[0], per[1], file, tmpfile)
                    if not dry:
                        ret = os.system(cmd)

                period_files.append(mfile)

            if len(period_files) == 0:
                continue
            
            print("CDO", op)
            print('  =>', oname)
            # Temp outfile in root output, to be moved
            tmpfile = os.path.join(outroot, oname)
            infiles = sorted([os.path.join(inroot, f) for f in period_files])
            infiles_str = ''
            for f in infiles:
                print('    ', os.path.basename(f))
                infiles_str += ' ' + f
            '''
            infiles = os.path.join(inroot, period_files[0])
            print('    ', os.path.basename(period_files[0]))
            for f in period_files[1:]:
                infiles += ' ' + os.path.join(inroot, f)
                print('    ', os.path.basename(f))
            '''
            # Concatenate all files
            cmd = cdo + " -L %s -cat '%s' %s" % (op, infiles_str, tmpfile)
            if dry:
                continue
            ret = os.system(cmd)

            # modify experiment attribute to 'historical' for rcp45 years < 2021
            if expid != experiment_id:
                os.system('ncatted -a experiment_id,global,m,c,historical -O %s %s.nc' % (tmpfile, tmpfile))
                os.remove(tmpfile)
                os.rename(tmpfile + '.nc', tmpfile)
            
            if os.path.isfile(outfile):
                cmd = cdo + " -L cat '%s %s' %s.nc" % (outfile, tmpfile, tmpfile)
                ret = os.system(cmd)
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
                    #print('    Created dir:', odir)
                os.rename(tmpfile, outfile)
                #print('    Created file.', oname)
            #else:
            #    print('Return status:', ret)

            for file in tmp_files:
                os.remove(file)


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    print('make_stats.py - make statistics data for KSS Klima 2100')
    print('')

    parser.add_argument(
        '--dry',  action='store_true',
        help='Only print the operations'
    )
    parser.add_argument(
        '-e', '--ensemble',  action='store_true',
        help='Create ensemble statistic files over all or selected models'
    )
    parser.add_argument(
        '-r', '--ref-period',  default=1,
        help='Ref. hist period:  1=default (' + ', '.join(['%d:%d-%d' % (i, periods[i][0], periods[i][1]) for i in range(len(periods))]) + ')'

    )
    parser.add_argument(
        '-s', '--stat',  required=True,
        help='stat operation: (' + ', '.join([k for k in stat_ops.keys()]) + ')'
    )
    parser.add_argument(
        '--interval',  default='yseas',
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
        '-m', '--model', default='*',
        help='Input model name: default "*"'
    )
    return parser.parse_args()

# Create mean and variance average data over all the periods, seasons (full = all seasons)

if __name__ == '__main__':
    #periods = ((1951, 2000), (2031, 2060), (2071, 2100)) # OLD MIPS5
    #periods = ((1971, 2000),                            (2041, 2070), (2071, 2100)) # CMIP5
    #periods = ((1985, 2014), (1991, 2020),              (2041, 2070), (2071, 2100)) # CMIP6
    periods = ((1971, 2000), (1985, 2014), (1991, 2020), (2041, 2070), (2071, 2100)) # 5+6
    stat_ops = {'mean': 1, 'min': 2, 'max': 3, 'std': 4}
    cdo = 'cdo'

    uname = platform.uname()
    #print(uname)
    
    args = parse_args()    
    dry = args.dry
    stat_op = args.stat
    n = stat_ops[stat_op]
    modelname = args.model

    if uname.system != 'Linux':
        print('Exit. Must be run under Linux because it needs CDO and NCO')
        exit()
    if '-tos' in uname.node: # NIRD or similar
        inbase = '/tos-project4/NS9076K/data/cordex-norway'
        inroot = inbase + '/EUR-11'
        outroot = inbase + '/stats_v3'
        #inroot = inbase + '/EUR-11.OLD'
        #outroot = inbase + '/stats_v3.OLD'
        cdo = '/opt/cdo'
    elif 'norceresearch.no' in uname.node:
        inbase = os.path.expanduser('~') + '/proj/KSS/cordex-norway'
        inroot = inbase + '/EUR-11'
        outroot = inbase + '/stats_v3'
    elif 'ppi-ext' in uname.node: # met.no
        inbase = '/lustre/storeC-ext/users/kin2100/NORCE/cordex-norway'
        inroot = inbase + '/EUR-11'
        outroot = inbase + '/stats_v3'
    else: # home
        inroot = 'C:/Dev/DATA/EUR-11'
        outroot = 'C:/Dev/DATA/cordex-norway/stats_v3'

    if args.ensemble:
        print('Reference period:', periods[int(args.ref_period)])
        make_ensemble_stats(outroot, args.interval, stat_op, periods[int(args.ref_period)])
    else:
    	make_stats(inroot, outroot, args.interval, stat_op, periods, modelname)
