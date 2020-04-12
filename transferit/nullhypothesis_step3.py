'''

Take the 95 percent bound of these dynamic gain curves as the final null hypothesis test curve. 

'''

import numpy as np
import scipy.io as sio

hostname = 'chenfei'
model = 'GE_diam_0'
runs = 100 # null hypothesis runs
codedirectory = '..'
datafolder = '/scratch/%s/%s/'%(hostname, model)

for tau in (5, ): 
  for posNa in (47,): 
    fr = 519
    appendix = 'tau%sfr%sposNa%s'%(tau, fr, posNa)
    foldername = datafolder + appendix
    gain = []
    for i in range(1,runs+1):
      data = np.load(datafolder+appendix+'/nullhypothesis/transferdata_nullhypothesis_run%d.npy'%(i), allow_pickle=True)
      dic = data.item()
      gain.append(dic['gain'])
    
    gain = np.array(gain)
    gain = np.sort(gain, axis=0)
    nullgain = gain[int(runs*0.95)]
    data = np.load(datafolder+'dynamic_gain_Hz_per_nA_%s.npy'%(appendix), allow_pickle=True)
    dic = data.item()
    dic['nullgain_%s'%(appendix)] = nullgain
    np.save(datafolder+'dynamic_gain_Hz_per_nA_%s.npy'%(appendix), dic)
