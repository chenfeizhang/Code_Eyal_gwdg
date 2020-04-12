'''

Run neuron model simulation. Calculate STA for 'OU', spike times for 'sinusoidal', population firing rate for 'step'. 

'''

import os, sys
from neuron import h
import numpy as np

# Load parameters
foldername = sys.argv[-1]
k_id = int(sys.argv[-2])
os.environ.keys()
i = int(os.environ['SLURM_ARRAY_TASK_ID']) # index of the job number
print('i = %d'%(i))
data = np.load(foldername + '/Series%s'%(k_id) + '/param.npy', allow_pickle=True)
param = data.item()
for key, val in param.items():
  exec(key + '=val')

# Import model simulation function and stimulus generation function.
sys.path.append('%s/Parameters'%(codedirectory))
from model_simulation_all import simulation, stimulate

T_all = T + T_relax # simulation time and randomization of initial condition 
spike_time_duration = []
for k in range(rep): 
  print('Loop at %d\n' %(k))
  seednumber = i*100+k # i is Series number. k is repitition number.
  va = simulation(model, tau, posNa, T_all, mean, std, dt=dt, seednumber=seednumber, stim_type=stim_type, amplitude=amplitude, frequency=frequency)
  a = np.diff((np.array(va)>spthr)*1.0)
  sp_id = np.where(a==1)[0] # spike time index
  b = np.diff((np.array(va)>v_loc)*1.0)
  v_loc_id_all = np.where(b==1)[0] # index of passing v_loc from below 
  v_loc_pair = [] # the last time to pass v_loc from below before each spike time
  for sp in sp_id:
    if sum(np.diff((v_loc_id_all<sp)*1.0)) == 0: # if sp is larger than all the v_loc_id, then the last one is paired.
      v_loc_pair.append(v_loc_id_all[-1])
    else:
      c = np.diff((v_loc_id_all<sp)*1.0) 
      v_loc_last_id = np.where(c==-1)[0][-1]
      v_loc_pair.append(v_loc_id_all[v_loc_last_id])
  spike_time_duration += list((np.array(list(sp_id)) - np.array(v_loc_pair))*dt)
  sys.stdout.flush()

np.save(foldername + '/Series' + str(k_id) + '/spike_detection_duration_%s'%(i), spike_time_duration)
