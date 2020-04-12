'''

This module file provides a simulation function of Eyal's model and a stimulus generation function. 

Action potential voltages are recorded on the AIS with a distance of 47um from the soma. If the maximum voltage is not larger than the half-activation voltage of sodium channels, it is assumed to have no spikes generated. For Eyal's model, half-activation voltage is (tha-vshift). See na.mod in Models/GE_diam_0 for definitions of 'tha' and 'vshift'.

Axonal voltage with the maximum votlage derivative is defined for spike time detection. 

The stimulus generation function can generate both constant and stochastic stimuli. The stochastic stimuli are generated with the Ornstein-Uhlenbeck process. When the std of the stochastic stimulus is set to zero, the stimulus is a constant. One can also add a sinusoidal current or a step current to the stochastic stimulus.

This file also provides a test. To run the test: ~/Code_Eyal/Models/GE_diam_0/x86_64/special -python model_simulation.py GE_diam_0 (Here GE_diam_0 refers to the Eyal's model without the dendrite compartment.)

'''

def simulation(model, tau, posNa, T, stim_mean, stim_std, dt=0.025, seednumber=1, stim_type='OU', amplitude=[0], frequency=[0], electrode_place = 'soma'): 
  '''

  simulation(object) -> va (axonal voltage at the AP initiation site in mV)

  Simulate the neuron model based on model setup and stimulus parameters.
  
  Parameters: Meanings [Example Values]
  model: model name ['GE_diam_0']
  tau: correlation time of stimulus (ms) [5]
  posNa: AP initiation site on axon (um) [47]
  T: duration of stimulus and simulation (ms) [20000]
  stim_mean: mean of stochastic stimulus (nA) [0.0]
  stim_std: std of stochastic stimulus (nA) [0.0346]
  dt: time step of model simulation (ms) [0.025]
  seednumber: random seed number for stimulus generation [1]
  stim_type: type of stimulus ['OU']
  amplitude: amplitude of the sinusoidal signal in unit of stim_std [0.1] 
  frequency: frequency of the sinusoidal signal added to background noise (Hz) [1, 2, 5, 10, 20, ..., 1000] 
  electrode_place: the place of the input stimulus ['soma']
  '''
  import os, sys
  from neuron import h

  # Load parameters into NEURON.
  h('dt=%f'%(dt))
  h('posNa=%f'%(posNa)) 
  
  # Set up neuron model.
  h.load_file('nrngui.hoc') # Load nrngui.
  h('objref cell') # create neuron model
  h.load_file('../Models/%s/%s.hoc'%(model, model))
  exec('h.cell = h.%s()'%(model))
  h.cell.create_model()
  h.cell.biophys()
  h('v_init = -90') # initial voltage
  h('objref stimulus, stim, vAIS')
  if electrode_place == 'soma':
    h.stimulus = h.IClamp(0.5)
  else:
    h.stimulus = h.IClamp(h.cell.axon[0](0.94))
  h.stimulus.dur = T

  h.stim = h.Vector()
  h.stim.from_python(stimulate([stim_mean, stim_std, tau, dt, T, seednumber, stim_type, amplitude, frequency])) # Generate the stimulus with the OU process.
  h('stim.play(&stimulus.amp, dt)') 
  h.finitialize()
  h.frecord_init()
  
  # Axonal voltage recording
  h.vAIS = h.Vector(int(T/dt)) 
  h.vAIS.record(h.cell.axon[0](h.posNa/h.cell.axon[0].L)._ref_v) # Axonal voltage is recorded on the AIS with a distance of posNa. Total length of AIS is L.
  # h.vAIS.record(h.cell.soma[0](0.5)._ref_v)
  h.tstop = T # duration of simulation

  # Initiate model simulation
  h.finitialize()
  h.frecord_init()
  h.run()

  va = h.vAIS.to_python() # Convert NEURON vector to numpy array.
  return va


def stimulate(li): # li = [stim_mean, stim_std, tau, dt, T, seednumber, stim_type, amplitude, frequency]
  '''
  simulate (object) -> x (stimulus in nA)

  Generate stimulus for model simulation.

  Parameters and related meanings are the same as those defined in function simulation.

  '''
  from random import seed, gauss
  from math import exp, sqrt, pi, sin

  # Load parameters.
  stim_mean = li[0] 
  stim_std = li[1]
  tau = li[2] 
  dt = li[3] 
  T = li[4] 
  seednumber = li[5]
  stim_type = li[6]
  amplitude = li[7]
  frequency = li[8]

  # Generate stimulus.
  seed(seednumber) # Define random seed.
  x = [stim_mean] # Start stimulus with stim_mean.
  for i in range(int(T/dt)): # Generate stimulus with Ornstein-Uhlenbeck process.
    if tau != 0:
      x.append(x[-1] + (1 - exp(-dt/tau)) * (stim_mean - x[-1]) + sqrt(1 - exp(-2*dt/tau))*stim_std*gauss(0,1))
    else:
      x.append(stim_mean + stim_std*gauss(0,1)) # white noise for tau=0.
  
  if stim_type == 'sinusoidal':
    for i in range(len(x)): # add sinusoidal components
      sinusoidal_components_list = [(stim_std*amplitude[k])*sin(2*pi*frequency[k]*i*dt/1000.0) for k in range(len(amplitude))]
      x[i] += sum(sinusoidal_components_list)

  if stim_type == 'step':
    onset_time = 1000 # ms
    for i in range(int(T/dt)): # add the step current
      if i > int(onset_time/dt - 1) and i < int((onset_time+1000)/dt + 1): 
        x[i] = x[i] + stim_std*amplitude[0]/2.0
      else:
        x[i] = x[i] - stim_std*amplitude[0]/2.0

  return x


if __name__ == "__main__":
  '''
  Self-test for model simulation.

  To estimate the axonal voltage with the maximum votlage derivative, set threshold to 60mV, then inject the neuron model with a constant input.
  '''
  import numpy as np
  import scipy.io as sio
  import sys

  # Load parameters.
  model = sys.argv[-1]
  dt = 0.025
  tau = 50
  posNa = 47
  T = 20000
  stim_mean = -0.018
  stim_std = 0.04343

  # Run model simulation.
  print("Model name is %s."%(model))
  va = simulation(model, tau, posNa, T, stim_mean, stim_std, dt=dt, seednumber=1, stim_type='OU', amplitude=[0], frequency=[0])
  stim = stimulate([stim_mean, stim_std, tau, dt, T, 1,'OU', [0], [0]])
  v_half = -25
  maxva = max(va)
  if maxva<v_half: 
    print("Maximum voltage is %s. Stimulus is not large enough."%(maxva))
  else:
    # Take the axonal voltage with maximum voltage derivative for spike detection voltage.
    spthrV = va[np.argmax(np.diff(va)/dt)] 
    print("Spike time threshold is estimated to be %f mV."%(spthrV))
    # Estimate the firing rate and the coefficient variation (CV) of interspike intervals (ISI).
    a = np.diff((np.array(va)>spthrV)*1.0)
    itemindex = np.where(a==1)
    sp = np.array(itemindex[0]*dt)
    fr_estimated = len(sp)/float(T)*1000
    print(sp)
    print("Fr is %f Hz."%(fr_estimated))
    if len(sp)>1:
      isi = np.diff(sp)
      CV = np.std(isi)/np.mean(isi)
      print("CV is %f."%(CV))
    else: print("Not enough spikes for CV estimation.")
