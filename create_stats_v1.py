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

MERGED = 'merged'

def make_season_indices(src, y1, y2, month):
    sub = []
    time = src.variables['time']
    for y in range(y1, y2 + 1):
        start_time = dt.datetime(y, month, 1, 12, 0)
        stop_time = start_time + relativedelta(months=3)
        istart = nc4.date2index(start_time, time, select='nearest')
        istop = nc4.date2index(stop_time, time, select='nearest')
        for i in range(istart, istop):
            sub.append(i)
    return sub


def write_nc4_season(src1, src, dst, y1, y2, month):

    # compute array of indices to match season
    sub = make_season_indices(src, y1, y2, month)
    
    # copy global attributes
    dst.setncatts({k: src1.getncattr(k) for k in src1.ncattrs()})

    # copy dimensions
    for name, dimension in src.dimensions.items():
        dst.createDimension(name, None if dimension.isunlimited() else len(dimension))

    # copy all file data for variables
    for name, variable in src.variables.items():
        ndims = len(variable.dimensions)
        has_time = ndims > 0 and variable.dimensions[0] == 'time'
        #print(name, ndims)

        datatype = variable[:].dtype
        x = dst.createVariable(name, datatype, variable.dimensions)
        #print('Created:', name, datatype, variable.dimensions)
        # copy variable attributes from src1: src does not have attribs because it is MF.
        try:
            v = src1.variables[name]
            x.setncatts({k: v.getncattr(k) for k in v.ncattrs()})
        except:
            pass

        if ndims == 0:
            x = variable
        elif has_time:
            x[:] = variable[sub]
        else:
            x[:] = variable[:]
        

def extract_season(inroot, infiles, outroot, outfile, month, y_min, y_max):
    season = {0: 'full', 3: 's1', 6: 's2', 9: 's3', 12: 's4'}
    opr = MERGED
    basefile = outfile + '_%s_%s.nc' % (season[month], opr)
    outfile_full = os.path.join(outroot, season[month], opr, basefile)
    print('Output:')
    print(os.path.dirname(outfile_full))
    print('   ', os.path.basename(outfile_full))
    if os.path.isfile(outfile_full):
        print('    ...exists')
        return outfile_full

    tmp = os.path.join(outroot, str(uuid.uuid4()) + '.nc')
    infiles_full = [os.path.join(inroot, f) for f in infiles]

    with nc4.Dataset(infiles_full[0]) as src1, nc4.MFDataset(infiles_full) as src, nc4.Dataset(tmp, "w") as dst:
        write_nc4_season(src1, src, dst, y_min, y_max, month)
        
    odir = os.path.dirname(outfile_full)
    if not os.path.isdir(odir):
        os.makedirs(odir)
        print('Created dir:', odir)
    os.rename(tmp, outfile_full)
    return outfile_full


def create_statistics(inroot, infiles, outroot, outfile, month, stat_op):
    season = {0: 'full', 3: 's1', 6: 's2', 9: 's3', 12: 's4'}
    basefile = outfile + '_%s_%s.nc' % (season[month], stat_op)
    outfile_full = os.path.join(outroot, season[month], stat_op, basefile)
    print('Output:')
    print(os.path.dirname(outfile_full))
    print('   ', os.path.basename(outfile_full))
    if os.path.isfile(outfile_full):
        print('    ...exists')
        return outfile_full

    tmp = os.path.join(outroot, str(uuid.uuid4()) + '.nc')
    infiles_full = os.path.join(inroot, infiles[0])
    for f in infiles[1:]:
        infiles_full += ' ' + os.path.join(inroot, f)

    # diff between timmean and timavg:
    # https://code.mpimet.mpg.de/projects/cdo/embedded/index.html#x1-3490002.8
    #cmd = "cdo %s -cat '%s' %s" % (stat_op, infiles_full, tmp)
    cmd = "cdo %s,DJF -cat '%s' %s" % (stat_op, infiles_full, tmp)
    ret = os.system(cmd)
    
    print('Return status:', ret)
    if ret == 0:
        odir = os.path.dirname(outfile_full)
        if not os.path.isdir(odir):
            os.makedirs(odir)
            print('Created dir:', odir)
        os.rename(tmp, outfile_full)
        return outfile_full
    return None


def find_period(d1, d2, periods):
    i = 0
    for p in periods:
        if p[0] <= d1.year <= d2.year <= p[1]: return i
        elif (p[0] <= d1.year <= p[1]) or (p[0] <= d2.year <= p[1]): return -2
        i += 1
    return -1
    

def map_input_output(inroot, institute=None, periods=((1951, 2000), (2031, 2060), (2071, 2100))):
    path_map = {}
    if inroot[-1] != '/':
        inroot += '/'
    for root, dirs, files in os.walk(inroot):
        for f in files:
            if f.endswith('.nc'):
                subpath = root.replace(inroot, '')
                institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version_id, freq_id, var_id, create_ver_id = subpath.split('/')
                if institute is not None and institute != institute_id:
                    continue
                d1 = dt.datetime.strptime(f[-20:-12], '%Y%m%d')
                d2 = dt.datetime.strptime(f[-11:-3], '%Y%m%d')
                p = find_period(d1, d2, periods)
                if p == -2:
                    print('Warning: skipping file partially in period:', f)
                    continue
                if p == -1:
                    continue

                inpath = os.path.join(subpath, f)
                period_id = '%d-%d' % (periods[p][0], periods[p][1])
                experiment_name = '%s_%s_%s_%s_%s_%s_%s_%s_%s_%s_%s' % ('EUR-11', institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version_id, freq_id, var_id, create_ver_id, period_id)
                #experiment_name = '%s_%s' % (f[:-21], period_id)
                outpath = '%s_%s_%s/%s' % (var_id, experiment_id, period_id, experiment_name)
                try:
                    path_map[outpath].append(inpath)
                except:
                    path_map[outpath] = [inpath]
    return path_map


def create_stats(inroot, outroot, month, stat_op, institute=None, periods=((1951, 2000), (2031, 2060), (2071, 2100))):
    path_map = map_input_output(inroot, institute, periods)

    if not os.path.isdir(outroot):
        os.makedirs(outroot)
    for outfile, infiles in path_map.items():
        infiles.sort()
        y_min, y_max = 100000, 0
        print('Input:')
        for f in infiles:
            y_min = min(y_min, int(f[-20:-16]))
            y_max = max(y_max, int(f[-11:-7]))   
            print('   ', f) 
        if True: # month == 0:
            if stat_op != MERGED:
                create_statistics(inroot, infiles, outroot, outfile, month, stat_op)
        else:
            outpath = extract_season(inroot, infiles, outroot, outfile, month, y_min, y_max)
            if outpath and stat_op != MERGED:
                create_statistics(os.path.dirname(outpath), [os.path.basename(outpath)], outroot, outfile, month, stat_op)

# MAIN

if __name__ == '__main__':
    season = {'s1': 3, 's2': 6, 's3': 9, 's4': 12, 'full': 0}
    stat_ops = {MERGED: 0, 'timmean': 1, 'timavg': 2, 'timvar': 3, 'timstd': 4, 'timmin': 5, 'timmax': 6, 'timrange': 7}
    try:
        month = season[sys.argv[1]]
        stat_op = sys.argv[2]
        #n = stat_ops[stat_op]
    except:
        print('Usage: create_stats {full|s1|s2|s3|s4} {merged|timmean|timavg|timvar|timstd|timmin|timmax|timrange} [{institute|all} [period]]')
        exit()

    institute = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "all" else None  # e.g. DMI
    if len(sys.argv) > 5:
        periods = [(int(sys.argv[i]), int(sys.argv[i+1])) for i in range(4, len(sys.argv), 2)]
    else:
        periods = ((1951, 2000), (2031, 2060), (2071, 2100))
    print('Using all instutes' if institute == None else institute)
    print('Using periods:', periods)
    
    create_stats(
        inroot='/tos-project4/NS9076K/data/cordex-norway/EUR-11',
        outroot='/tos-project4/NS9076K/data/cordex-norway', 
        month=month,
        stat_op=stat_op,
        institute=institute, 
        periods=periods
    )
