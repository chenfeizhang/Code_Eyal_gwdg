#! /usr/bin/python

'''
Firing rate estimation 
'''

import sys, os
import numpy as np
foldername = sys.argv[-1]

# Parameters loading
data = np.load(foldername + '/param.npy', allow_pickle=True)
param = data.item()
for key, val in param.items():
  exec(key + '=val')

os.environ.keys()
i = int(os.environ['SLURM_ARRAY_TASK_ID'])
stim_mean = Iconst[i-1]

from model_simulation_all import simulation
va = simulation(model, 5, posNa, T, stim_mean, 0, dt=dt) # stim_std = 0
a = np.diff((np.array(va)>spthr)*1)
itemindex = np.where(a==1)
T_s = T/1000.0
fr = len(itemindex[0])/T_s
print("Firing rate is %s Hz"%(fr))
np.save('%s/mean_fr_%i'%(foldername, i),{'mean':stim_mean, 'fr':fr})


