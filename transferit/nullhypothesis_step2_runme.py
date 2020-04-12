'''

This file loads STAs generated from shuffled spike times across different series folders, and calculates linear response curves.

'''

import os, sys, math
datafolder = sys.argv[-1]
appendix = sys.argv[-2]
os.environ.keys()
ii = int(os.environ['SLURM_ARRAY_TASK_ID'])
print('ii = %d'%(ii)) # null hypothesis run index

import numpy as np
data = np.load(datafolder + appendix + '/param.npy', allow_pickle=True)
param = data.item()
for key, val in param.items():
  exec(key + '=val')

runs = 400 # runjob series number
STA = np.zeros(L)
for kk in range(1,runs+1):
  datafile = datafolder + appendix + '/Series' + str(kk) + '/STA_null_run%d.npy'%(ii)
  data = np.load(datafile, allow_pickle=True)
  dic = data.item()       
  STA_tmp = dic['STA']
  STA = STA + STA_tmp

STA = STA/float(runs)   
from transferit import gain, firing_rate_estimate
fr_estimated = firing_rate_estimate(range(1, runs+1), datafolder, appendix)
[f, gain_filt] = gain(fr_estimated, STA, datafolder, appendix)
transferdata = {'f':f, 'gain':gain_filt}
np.save(datafolder + appendix + '/nullhypothesis/transferdata_nullhypothesis_run%d'%(ii), transferdata)





