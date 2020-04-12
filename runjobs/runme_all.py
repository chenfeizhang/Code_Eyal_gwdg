'''

Run neuron model simulation. Calculate STA for 'OU', spike times for 'sinusoidal', population firing rate for 'step'. 

'''

import os, sys
from neuron import h
import numpy as np

# Load parameters
foldername = sys.argv[-1]
os.environ.keys()
i = int(os.environ['SLURM_ARRAY_TASK_ID']) # index of the job number
print('i = %d'%(i))
data = np.load(foldername + '/param.npy', allow_pickle=True)
param = data.item()
for key, val in param.items():
  exec(key + '=val')

# Import model simulation function and stimulus generation function.
sys.path.append('%s/Parameters'%(codedirectory))
from model_simulation_all import simulation, stimulate

# Parameters for STA and dynamic gain function
N = int(T/dt) # number of time bins    
dt_s = dt*10**-3 # time step in unit of second
sf = 1/dt_s # sampling frequency
maxtau = int(STA_L/2*sf) # The length of half of a STA
L = maxtau*2 # length of the whole STA
param['N'] = N
param['dt_s'] = dt_s
param['sf'] = sf
param['maxtau'] = maxtau
param['L'] = L
if i==1:
  np.save(foldername + '/param.npy', param, allow_pickle=True)

spiketimelist = [] # list of spike times for calculating STA
nspikes = 0 # number of spikes for calculating STA
STA_tmp = np.zeros(L) # the sum of all spike triggered stimuli
T_all = T + T_relax # simulation time and randomization of initial condition time
firing_rate = np.zeros(N)

for k in range(rep): 
  print('Loop at %d\n' %(k))
  seednumber = i*10000+k # i is Series number. k is repitition number. Repetition number is assumed to be smaller than 100.
  va = simulation(model, tau, posNa, T_all, mean, std, dt=dt, seednumber=seednumber, stim_type=stim_type, amplitude=amplitude, frequency=frequency, electrode_place = electrode_place)
  a = np.diff((np.array(va)>spthr)*1.0)
  itemindex = np.where(a==1) 
  sp1 = np.array(itemindex[0]*dt) # spike times in T_relax+T
  if stim_type == 'OU':
    sp2 = (sp1[sp1>T_relax] - T_relax)/1000.0 # Rule out spikes in T_relax. Deduct T_relax for later spike times. Change unit to second.
    spiketimelist.append(sp2)  
    sp_STA = np.array([sp for sp in sp2 if sp>(STA_L/2.0) and sp<(T/1000.0-STA_L/2.0)]) # spike time in interval (STA_L/2, T-STA_L/2) for STA
    if len(sp_STA) != 0:
      stim = stimulate([mean, std, tau, dt, T_all, seednumber, stim_type, frequency, amplitude]) # the stimulus that generates spikes
      stim = stim[int(T_relax/dt):] # deduct the stimulus in T_relax
      for sp in sp_STA:
        STA_tmp_add =  stim[(int(sp/dt_s)-maxtau-1):(int(sp/dt_s)+maxtau-1)] # spike triggered stimulus
        STA_tmp = STA_tmp + np.array(STA_tmp_add)  

    nspikes = nspikes + len(sp_STA)

  if stim_type == 'sinusoidal':
    sp2 = (sp1[sp1>T_relax] - T_relax)/1000.0
    spiketimelist.append(sp2)  

  if stim_type == 'step':
    sp3 = (sp1[sp1>T_relax] - T_relax)/dt
    sp3 = sp3.astype(int)
    for sp_time in sp3:
      firing_rate[sp_time] += 1.0

  sys.stdout.flush()

if stim_type == 'OU':
  if nspikes != 0:
    STA = STA_tmp/float(nspikes) - mean
    np.save(foldername + '/Series' + str(i) + '/STA', {'STA':STA, 'stim':stim})
    np.save(foldername + '/Series' + str(i) + '/spiketimelist', {'spiketimelist':spiketimelist})

if stim_type == 'sinusoidal':
  np.save(foldername + '/Series' + str(i) + '/spiketimelist', {'spiketimelist':spiketimelist})

if stim_type == 'step':
  firing_rate = firing_rate/float(rep)
  np.save(foldername + '/Series' + str(i) + '/firing_rate', firing_rate)

