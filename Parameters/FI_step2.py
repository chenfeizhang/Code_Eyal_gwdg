#! /usr/bin/python

'''
This file collects the data and saves them into one file. 
'''

import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt

hostname = 'chenfei'
model = 'GE_diam_0'
runs = 500
datafolder = '/scratch/%s/%s/'%(hostname,model)

for posNa in (47, ):
  fr_all = []
  stim_mean_all = []
  appendix = 'posNa%s'%(posNa)
  foldername = datafolder + 'FI_constant/' + appendix    
  for k in range(1,runs+1):
    data = np.load(foldername+'/mean_fr_%d.npy'%(k), allow_pickle=True)
    dic = data.item()
    fr_all.append(dic['fr'])
    stim_mean_all.append(dic['mean'])
  np.save(datafolder + 'FI_constant/' + appendix + '_FI', {'fr':fr_all, 'I':stim_mean_all})
  plt.plot(stim_mean_all, fr_all)
  plt.savefig('F_I.pdf')
