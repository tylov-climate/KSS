#!/usr/bin/env python
#
# Coded by Tyge Lovset, 2020

import os
import sys
import glob
import datetime as dt
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

def create_avg(inroot, outroot, infiles, outfile):
    infiles.sort()
    infiles_full = os.path.join(inroot, infiles[0])
    
    for f in infiles[1:]:
        infiles_full += ' ' + os.path.join(inroot, f)
    outfile_full = os.path.join(outroot, outfile) + '.nc'

    print(outfile)
    if os.path.isfile(outfile_full):
            print('Exists')
            return
 
    tmp = os.path.join(outroot, str(uuid.uuid4()) + '.nc')

    # timmean uses only non-missing values, while timavg uses all.
    # https://code.mpimet.mpg.de/projects/cdo/embedded/index.html#x1-3490002.8
    cmd = "cdo timmean -cat '%s' %s" % (infiles_full, tmp)
    for f in infiles:
        print('   ', f)
 
    ret = os.system(cmd)
    
    print('Result:', ret)    
    if ret == 0:
        odir = os.path.dirname(outfile_full)
        if not os.path.isdir(odir):
            os.makedirs(odir)
            print('Created dir:', odir)
        os.rename(tmp, outfile_full)


def find_period(d1, d2, periods):
    i = 0
    for p in periods:
        if p[0] <= d1.year <= d2.year <= p[1]: return i
        elif (p[0] <= d1.year <= p[1]) or (p[0] <= d2.year <= p[1]): return -2
        i += 1
    return -1

def create_file_groups(inroot, outroot, institute = None, periods=((1951, 2000), (2031, 2060), (2071, 2100))):
    m = {}
    if inroot[-1] != '/':
        inroot += '/'
    for root, dirs, files in os.walk(inroot):
        for f in files:
            if f.endswith('.nc'):
                infile = os.path.join(root, f)
                subpath = root.replace(inroot, '')
                institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version_id, freq_id, var_id, create_ver_id = subpath.split('/')
                d1 = dt.datetime.strptime(f[-20:-12], '%Y%m%d')
                d2 = dt.datetime.strptime(f[-11:-3], '%Y%m%d')
                p = find_period(d1, d2, periods)
                if p == -2:
                    print('PARTLY OUTSIDE:', f)
                    continuell 
                if p == -1:
                    continue
                pavg = 'a%d-%d' % (periods[p][0], periods[p][1])
                #experiment_name = '%s_%s_%s_%s_%s_%s_%s_%s_%s_%s' % (var_id, domain_id, institute_id, model_id, experiment_id, ensemble_id, source_id, rcm_version_id, freq_id, pavg)
                experiment_name = '%s_%s' % (f[:-21], pavg)
                output_name = '%s_%s/%s' % (var_id, pavg, experiment_name)
                try:
                    m[output_name].append(os.path.join(subpath, f))
                except:
                    m[output_name] = [os.path.join(subpath, f)]
    return m


def create_avg_all(inroot, outroot):
    m = create_file_groups(inroot, outroot) 
    n = 0
    if not os.path.isdir(outroot):
        os.makedirs(outroot)    
    for outfile, infiles in m.items():
        create_avg(inroot, outroot, infiles, outfile)
    return m



# MAIN

if __name__ == '__main__':
    #if len(sys.argv) == 1:
    #    print('give institute group name')
    #    exit()
    #group = sys.argv[1]
    m = create_avg_all(
        inroot='/tos-project4/NS9076K/data/cordex-norway/EUR-11',
        outroot='/tos-project4/NS9076K/data/cordex-norway/avg'
    )
