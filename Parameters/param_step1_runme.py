'''

Search for the constant input that is about to trigger spikes and the constant input that generates 5Hz firing rate.

'''

import sys, os
import numpy as np

# Load parameters.
foldername = sys.argv[-1] 
data = np.load(foldername + '/param.npy', allow_pickle=True)
param = data.item()
for key, val in param.items():
  exec(key + '=val')

# Import model simulation function and parameter searching function.
sys.path.append('%s/scripts'%(codedirectory))
# Import the function for model simulation.
from model_simulation_all import simulation
# Import the function for stimulus searching.
from firingonset import FiringOnset 

# Search for constant stimulus.
stim_0 = 0
# stim_start: stimulus just about to fire (fr=0Hz)
stim_start = FiringOnset(simulation, param, leftI, rightI, precisionFiringOnset, 0, electrode_place = electrode_place)
# stim_saturate: stimulus that generates 5Hz firing rate (fr=5Hz) 
stim_saturate = FiringOnset(simulation, param, leftI, rightI, precisionFiringOnset, fr, electrode_place = electrode_place) 

np.save(foldername+'/mean',{'stim_0':stim_0, 'stim_start':stim_start, 'stim_saturate':stim_saturate})
