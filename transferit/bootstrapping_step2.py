'''

Determine bootstrapping boundaries from 1000 bootstrapping linear response curves.

Linear response curves should be calculated with transferit.py before running this file.

'''

import numpy as np
import os
import scipy.io as sio
import matplotlib.pyplot as plt
hostname = 'chenfei'
model = 'GE_diam_0'
stim_type = 'OU'
runs = 1000
codedirectory = '..'
datafolder = '/scratch/%s/%s/'%(hostname, model)

for tau in (50,): 
  for posNa in (47, ):
    for fr in (5192, ): 
      if stim_type == 'OU':
        appendix = 'tau%sfr%sposNa%s_spikedistance50_v2'%(tau, fr, posNa)
      if stim_type == 'step':
        amplitude = 0.1
        appendix = 'tau%sfr%sposNa%samplitude%s'%(tau, fr, posNa, amplitude)
      foldername = datafolder + appendix
      gain = []
      # Load linear response curves
      filenumber = 0
      for i in range(1,runs+1):
        datafile = datafolder+appendix+'/bootstrapping/transferdata_bootstrapping_%d.npy'%(i)
        if os.path.isfile(datafile) == True:
          filenumber += 1
          data = np.load(datafile, allow_pickle=True)
          dic = data.item()
          gain.append(dic['gain'])
      
      # Sort all curves to determine the 95 percent boundary.
      gain_all = np.array(gain)
      gain = np.sort(gain_all, axis=0)
      bootstrapping_gain_lower = gain[int(filenumber*0.025)] # take the 95 percent in the middle as the confidence interval
      bootstrapping_gain_upper = gain[int(filenumber*0.975)]
      if stim_type == 'OU':
        data = np.load(datafolder+'dynamic_gain_Hz_per_nA_%s.npy'%(appendix), allow_pickle=True)
        dic = data.item()
        dic['bootstrapping_gain_lower_%s'%(appendix)] = bootstrapping_gain_lower
        dic['bootstrapping_gain_upper_%s'%(appendix)] = bootstrapping_gain_upper
        # Save bootstrapping boundaries in linear response curve data file.
        np.save(datafolder+'dynamic_gain_Hz_per_nA_%s.npy'%(appendix), dic)
      if stim_type == 'step':
        data_appendix = 'tau%sfr%sposNa%s'%(tau, fr, posNa)
        data = np.load(datafolder+'dynamic_gain_step_%s.npy'%(appendix), allow_pickle=True)
        dic = data.item()
        dic['bootstrapping_gain_lower_%s'%(data_appendix)] = bootstrapping_gain_lower
        dic['bootstrapping_gain_upper_%s'%(data_appendix)] = bootstrapping_gain_upper
        # Save bootstrapping boundaries in linear response curve data file.
        np.save(datafolder+'dynamic_gain_step_%s.npy'%(appendix), dic)
