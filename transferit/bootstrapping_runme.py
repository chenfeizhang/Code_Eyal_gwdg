'''

This file defines neuron models for bootstrapping and the range of series folders for random selection of STA.

'''

import os, sys, math
import numpy as np
from random import randint

runs = 400 # number of series folders
datafolder = sys.argv[-1]
stim_type = sys.argv[-2]
os.environ.keys()
ii = int(os.environ['SLURM_ARRAY_TASK_ID'])
print('ii = %d'%(ii))

for tau in (50, ):  
  for posNa in (47,): 
    for fr in (5192,):
      if stim_type == 'OU':
        from transferit import STA_average, gain, firing_rate_estimate
        appendix = 'tau%sfr%sposNa%s_spikedistance50_v3'%(tau, fr, posNa)
        # Randomly select STA with replacement.
        List = [randint(1,runs) for i in range(runs)]
        fr_estimated = firing_rate_estimate(List, datafolder, appendix)
        print('Firing rate is estimated to be %sHz.'%(fr_estimated))
        STA = STA_average(List, datafolder, appendix) # averaged STA
        [f, gain_filt] = gain(fr_estimated, STA, datafolder, appendix) 
        transferdata = {'f':f, 'gain':gain_filt}

      if stim_type == 'step':
        amplitude = 0.1
        appendix = 'tau%sfr%sposNa%samplitude%s'%(tau, fr, posNa, amplitude)
        from transferit import gain_step, firing_rate_step
        List = [randint(1,runs) for i in range(runs)]
        print('length of list is %d'%(len(List)))
        [f, gain, firing_rate_smooth] = gain_step(List, datafolder, appendix, tau, amplitude)
        transferdata = {'fr':firing_rate_smooth, 'gain':abs(gain), 'f':f}

      if os.path.isdir(datafolder+'/%s/bootstrapping'%(appendix)) == False:
        os.mkdir(datafolder+'/%s/bootstrapping'%(appendix))
      np.save(datafolder+'/%s/bootstrapping/transferdata_bootstrapping_%d'%(appendix,ii), transferdata)
