"""
Search for constant stimulus that generates expected firing rate.

1. Set the upper bound and the lower bound of the constant stimulus by hand.
2. Estimate the firing rate generated with the mean of the upper bound and the lower bound.
3. If the firing rate is too small, replace the lower bound with the middle point. If the firing rate is too large, replace the upper bound with the middle point.
4. Searching iteration will stop when the difference between the upper bound and the lower bound is smaller than 1% of the magnitude of the upper bound or the lower bound. Here the percision parameter 1% is set by hand.
5. If the expected firing rate is larger than 0, it will return the upper bound. If the expected firing rate is 0, it will return the lower bound. 

"""

def FiringOnset(simulation, param, leftI, rightI, precision, fr_set, electrode_place = 'soma'):
  import numpy as np
  import sys
  # Load parameters.  
  model = param['model']
  tau = param['tau']
  posNa = param['posNa']
  T = param['T']
  dt = param['dt']
  spthr = param['spthr']

  # Middle point searching
  while ((rightI-leftI) > precision*max([abs(rightI), abs(leftI)])):
    print("leftI is %f, rightI is %f"%(leftI, rightI))
    mean = (leftI+rightI)/2
    print('mean for test is %f'%(mean))
    va = simulation(model, tau, posNa, T, mean, 0, dt, electrode_place=electrode_place)
    a = np.diff((np.array(va)>spthr)*1.0)
    itemindex = np.where(a==1)
    sp = np.array(itemindex[0]*dt)
    fr = len(sp)/float(T)*1000
    print('fr is %f'%(fr))
    sys.stdout.flush()
    if (fr <= fr_set): 
      leftI = mean # If the firing rate is too small, replace lower bound with middle point
    else:
      rightI = mean # If the firing rate is too large, replace upper bound with middle point
  
  if fr_set>0: 
    return rightI
  else:
    return leftI

