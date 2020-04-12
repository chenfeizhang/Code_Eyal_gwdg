"""
Searching for std to reproduce the expected firing rate.

The searching algorithm is the same as that of firingoset.py.

"""

def DetermineStdI(simulation, param, leftStd, rightStd, precision_std, stim_mean, fr_set, electrode_place='soma'):
  import numpy as np
  import sys
  # Load parameters.  
  T = param['T']
  model = param['model']
  tau = param['tau']
  posNa = param['posNa']
  dt = param['dt']
  spthr = param['spthr']
  T *= 10 # Simulation time is 10 times of that in constant stimulus searching.
  # Middle point searching
  while ((rightStd-leftStd) > precision_std*max([abs(rightStd), abs(leftStd)])):
    print("leftStd is %f, rightStd is %f"%(leftStd, rightStd))
    stim_std = (leftStd+rightStd)/2
    print('std for test is %f'%(stim_std))
    va = simulation(model, tau, posNa, T, stim_mean, stim_std, dt, electrode_place=electrode_place)
    a = np.diff((np.array(va)>spthr)*1.0)
    itemindex = np.where(a==1)
    sp = np.array(itemindex[0]*dt)
    fr = len(sp)/float(T)*1000
    isi = np.diff(sp)
    cv = np.std(isi)/np.mean(isi) # estimate the CV of ISI 
    print('fr is %f'%(fr))
    print('cv is %f'%(cv))
    sys.stdout.flush()
    if (fr <= fr_set): 
      leftStd = stim_std
    else:
      rightStd = stim_std

  return stim_std, cv
