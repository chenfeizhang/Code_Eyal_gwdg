'''

Run neuron model simulation. Calculate STA for 'OU', spike times for 'sinusoidal', population firing rate for 'step'. 

'''

import os, sys
from neuron import h
import numpy as np

# Load parameters
foldername = sys.argv[-1]
k_id = int(sys.argv[-2])
print('k is %s'%(k_id))
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
  np.save(foldername + '/param.npy', param)

spiketimelist = [] # list of spike times for calculating STA
nspikes = 0 # number of spikes for calculating STA
T_all = T + T_relax # simulation time and randomization of initial condition time

for k in range(rep): 
  print('Loop at %d\n' %(k))
  seednumber = i*10000+k # i is Series number. k is repitition number.
  va = simulation(model, tau, posNa, T_all, mean, std, dt=dt, seednumber=seednumber, stim_type=stim_type, amplitude=amplitude, frequency=frequency, electrode_place = electrode_place)
  a = np.diff((np.array(va)>spthr)*1.0)
  itemindex = np.where(a==1) 
  sp1 = np.array(itemindex[0]*dt) # spike times in T_relax+T
  if stim_type == 'OU':
    sp2 = (sp1[sp1>T_relax] - T_relax)/1000.0 # Rule out spikes in T_relax. Deduct T_relax for later spike times. Change unit to second.
    spiketimelist.append(sp2)  
    nspikes = nspikes + len(sp2)

  sys.stdout.flush()

if stim_type == 'OU':
  if nspikes != 0:
    np.save(foldername + '/Series' + str(k_id) + '/spiketimelist%s'%(i), {'spiketimelist':spiketimelist})
