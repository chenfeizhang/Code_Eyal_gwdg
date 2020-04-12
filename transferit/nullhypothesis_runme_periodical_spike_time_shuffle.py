'''

This file reproduces stimuli, loads spike times and calculates STA with shuffled spike times.

'''

import sys, os, random
import numpy as np

# Load parameters and spike time list.
foldername = sys.argv[-1]
os.environ.keys()
ii = int(os.environ['SLURM_ARRAY_TASK_ID'])
print('ii = %d'%(ii)) # series number in runjobs
data = np.load('%s/Series%s/spiketimelist.npy'%(foldername, ii), allow_pickle=True)
dic = data.item()
spiketimelist = dic['spiketimelist']
data = np.load(foldername + '/param.npy', allow_pickle=True)
param = data.item()
for key, val in param.items():
  exec(key + '=val')

T_all = T + T_relax
T_s = T/1000.0 # T in unit of second

# Load function for reproducing stimuli
sys.path.append(codedirectory+'/Parameters')
from model_simulation_all import stimulate

for run in range(1,1+100): # null hypothesis test run number
  nspikes = 0
  STA_tmp = np.zeros(L)
  for k in range(len(spiketimelist)):
    seednumber = ii*100+k # random seed number for reproducing stimuli
    stim = stimulate([mean, std, tau, dt, T_all, seednumber,'OU', [0], [0]])
    stim = stim[int(T_relax/dt):]
    random.seed(ii*1000+run) # random seed number for shuffling spike times
    sp2 = np.sort((spiketimelist[k]+random.uniform(1,T_s-1))%T_s) # Add a random number to all spike times and mod them by T_s.
    sp_STA = np.array([sp for sp in sp2 if sp>(STA_L/2.0+dt_s) and sp<(T/1000.0-STA_L/2.0)]) # spike time in interval (STA_L/2, T-STA_L/2) for STA
    for sp in sp_STA:
      STA_tmp_add =  stim[(int(sp/dt_s)-maxtau-1):(int(sp/dt_s)+maxtau-1)] # spike triggered stimulus
      STA_tmp = STA_tmp + np.array(STA_tmp_add)

    nspikes = nspikes + len(sp_STA)

  STA = STA_tmp/float(nspikes) - mean
  np.save(foldername + '/Series%s'%(ii) +'/STA_null_run%d'%(run), {'STA':STA})

