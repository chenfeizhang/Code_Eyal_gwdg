'''

Collect data and calculate electrotonic filtering. 

'''

hostname = 'chenfei'
model = 'GE_diam_0'
runs = 400
codedirectory = '..'
datafolder = '/scratch/%s/%s/'%(hostname, model)
import numpy as np
import scipy.io as sio
import os
import math

for tau in (5,):  
  for posNa in (47,): 
    for fr in (519, ):
      appendix = 'tau%dfr%dposNa%s_subthreshold_v2'%(tau, fr, posNa)
      foldername = datafolder + appendix
      data = np.load(foldername + '/param.npy', allow_pickle=True)
      gain = []
      frequency = []
      for i in range(1, runs+1):
        datafile = foldername + '/va_stim_%d.npy'%(i)
        if os.path.isfile(datafile) == True:
          data = np.load(datafile, allow_pickle=True)
          dic = data.item()
          gain.append(dic['ftout'])
          frequency.append(i)
        else: continue
      np.save(foldername + '/electrotonic_filtering_tau%sfr%sposNa47.npy'%(tau, fr), {'g_tau%s_posNa%d'%(tau,posNa):gain, 'f':frequency}) 
