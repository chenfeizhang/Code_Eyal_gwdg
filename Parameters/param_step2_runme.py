'''

For a given mean of the stimulus, search for the std of the stimulus that generates expected firing rate.

'''

import sys, os
from neuron import h
import numpy as np

# Parameters loading
foldername = sys.argv[-1]
data = np.load(foldername + '/mean.npy', allow_pickle=True)
dic = data.item()
# stim_0 = dic['stim_0']  
# stim_start = dic['stim_start'] 
stim_saturate = dic['stim_saturate'] 
# You can define parameters by hand:
stim_0 = stim_saturate - 0.2
stim_start = stim_saturate - 0.1
# stim_saturate = -0.102
data = np.load(foldername + '/param.npy', allow_pickle=True)
param = data.item()
for key, val in param.items():
  exec(key + '=val')

# Assign mean of stimulus.
os.environ.keys()
i = int(os.environ['SLURM_ARRAY_TASK_ID']) # i is the job number in the range of 1 to runs.
print('i = %d'%(i))
if i<(runs/2+1):
  stim_mean = (stim_start - stim_0)/(runs/2.0)*(i-1) + stim_0 # assign data points between stim_0 and stim_start
else:
  stim_mean = (stim_saturate - stim_start)/(runs/2.0)*(i-runs/2-1) + stim_start # assign data points between stim_start and stim_saturate

# Import model simulation function and std searching function.
sys.path.append('%s/scripts'%(codedirectory))
# Import the function for model simulation.
from model_simulation_all import simulation
# Import the function for std searching.
from Determinestd import DetermineStdI

# Search for std, estimate CV.
[stim_std, cv] = DetermineStdI(simulation, param, leftStd, rightStd, precision_std, stim_mean, fr, electrode_place=electrode_place) 
np.save('%s/mean%d/std_mean_cv'%(foldername, i),{'mean':stim_mean, 'std':stim_std, 'cv':cv})





