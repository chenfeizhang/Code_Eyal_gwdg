'''

Generate axonal voltages and stimuli for calculating electrotonic filtering.

'''

import os, sys
from neuron import h
import numpy as np

# Load parameters
foldername = sys.argv[-1]
os.environ.keys()
i = int(os.environ['SLURM_ARRAY_TASK_ID'])
print('i = %d'%(i))
frequency = [i]
if i<50:
  amplitude = [0.2]
else:
  amplitude = [0.2]

data = np.load(foldername + '/param.npy', allow_pickle=True)
param = data.item()
for key, val in param.items():
  exec(key + '=val')

# Import model simulation function and stimulus generation function.
sys.path.append('%s/Parameters'%(codedirectory))
from model_simulation_all import simulation, stimulate
T_all = T + T_relax # simulation time and randomization of initial condition time
len_va_average = int(1000/dt)
L = int(1000/dt) + 1
va_average = np.zeros(len_va_average)

for k in range(rep): 
  print('Loop at %d\n' %(k))
  seednumber = i*1000+k # i is Series number. k is repitition number.
  va = simulation(model, tau, posNa, T_all, mean, std, dt=dt, seednumber=seednumber, stim_type='sinusoidal', amplitude=amplitude, frequency=frequency)
  va = va[int(T_relax/dt):]
  for j in range(len(va)):
    if va[j]>-50:
      va[j] = -50
    #if va[j]<-70: # If model name is GE_diam_3 or GE_diam_5, axonal voltages below -70mV are set to -70mV.  
    #  va[j] = -70
  for k in range(int(T/1000)):
    va_average = va_average + np.array(va[k*len_va_average:(k+1)*len_va_average])

va_average = va_average/rep/(T/1000)
ftout = np.fft.fft(va_average)[:int(L/2+1)]/L
ftout = ftout[frequency[0]]/(amplitude[0]*std)
np.save(foldername + '/va_stim_%d'%(frequency[0]), {'ftout':abs(ftout), 'va_average':va_average})
