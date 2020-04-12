'''

Calculate of the dynamic gain function with the STA method, vector strength method, and step current method.

Self-test script.

'''

def firing_rate_estimate(List, datafolder, appendix):
  '''
  This function estimates the firing rate based on the simulated spike times.
  '''
  import numpy as np
  import os
  file_number=0 
  data = np.load(datafolder + appendix + '/param.npy', allow_pickle=True)
  param = data.item()
  T = param['T']/1000.0 
  fr_estimated = []
  for k in List:
    datafile = datafolder + appendix + '/Series%s/spiketimelist.npy'%(k)
    if os.path.isfile(datafile) == True:
      data = np.load(datafile, allow_pickle=True)
      spike_list_dict = data.item()
      spiketimelist = spike_list_dict['spiketimelist'] 
      spike_number = [len(sp) for sp in spiketimelist]
      fr_estimated.append(np.mean(spike_number)/T)
    else: continue
  return np.mean(fr_estimated)


def STA_average(List, datafolder, appendix):
  '''

  This function averages STAs over different jobs to get the final STA for dynamic gain functions.
  List: a list of job indices for STA average.
  datafolder: directory of data
  appendix: appendix for neuron model and stimulus parameters

  '''
  import numpy as np
  import os
  file_number=0 
  data = np.load(datafolder + appendix + '/param.npy', allow_pickle=True)
  param = data.item()
  L = param['L']
  STA = np.zeros(L)  
  for k in List:
    datafile = datafolder + appendix + '/Series%s/STA.npy'%(k)
    if os.path.isfile(datafile) == True:
      STA_nspikes = np.load(datafile, allow_pickle=True)
      STA_nspikes_dict = STA_nspikes.item()       
      STA_tmp = STA_nspikes_dict['STA']
      STA = STA + STA_tmp  
      file_number += 1
    else: continue 
  print("Total file number is %s"%(file_number))     
  STA = STA/float(file_number) 
  return STA


def gain(fr_estimated, STA, datafolder, appendix):
  '''
  
  This function calculates the dynamic gain function based on final STA and parameters of stimulus.

  The dynamic gain function is the ratio of Fourier transform of STA to power spectral density of OU stimulus.

  '''
  import numpy as np
  import math
  data = np.load(datafolder + appendix + '/param.npy', allow_pickle=True)
  param = data.item()
  sf = param['sf']
  L = param['L']
  dt_s = param['dt_s']
  f = sf/2*np.linspace(0,1,L/2+1) # frequency
  idx = 4000 # length of the dynamic gain components to be shown
  # filter STA with a trapezoid shaped fileter, such that two ends of STA are zero. This suppresses the noise in Fourier transform. 
  sidelength = 0.05 
  side = np.arange(0,1+dt_s/sidelength, dt_s/sidelength) # A linear slope of width 0.05 and hight 1
  window = np.array(list(side) + list([1]*(L-2*len(side))) + list(1-side))
  STA = STA*window # make the STA begin and end with 0
  ftSTA = np.fft.fft(np.append(STA[int(L/2):], STA[0:int(L/2)]))/float(sf) # cross power spectral density
  ftSTA = ftSTA[0:int(L/2)+1] 
  tau = param['tau']
  std = param['std']
  psd = 2*tau*(10**-3)*(std**2)/(1+(2*math.pi*tau*10**-3*f)**2) # analytical formula of the power spectral density of the OU stimulus
  gain_filt = np.zeros(idx)
  for i in range(idx):
    if i == 0:
      g = np.array([0]*len(ftSTA))
      g[0] = 1 # The fileter doesn't apply to the first component of ftSTA.
    else:
      g = math.e**(-2*math.pi**2*(f-f[i])**2/f[i]**2) # Gaussian filters, the variance increase with the frequency.
      g = g/float(sum(g)) # Normalize the filter to have a sum of one.
    gain_filt[i] = abs(sum(ftSTA*g))/float(psd[i]) # filter out the noise in the high frequency components

  return f[range(idx)], gain_filt*fr_estimated


def gain_sin(List, datafolder, appendix, freq):
  '''

  This function   

  '''
  import os
  import numpy as np
  from cmath import exp
  from math import pi
  foldername = datafolder + appendix
  nspikes = 0
  gain_vec = 0
  for i in List:
    if os.path.isfile(foldername+'/Series%d/spiketimelist.npy'%(i)) == True:
      data = np.load(foldername+'/Series%d/spiketimelist.npy'%(i), allow_pickle=True)
      dic = data.item()
      sp = dic['spiketimelist']
      for k in range(len(sp)):
        gain_vec = gain_vec + np.sum(np.exp(2*pi*1j*freq*np.array(sp[k])))
        nspikes = nspikes + len(sp[k])
  gain_vec = abs(gain_vec)/nspikes
  print('gain_vec is %f'%(gain_vec))
  return gain_vec

def firing_rate_step(List, datafolder, appendix):
  import numpy as np
  import os
  file_number=0 # total file number
  data = np.load(datafolder + appendix + '/param.npy', allow_pickle=True)
  param = data.item()
  T = param['T']
  dt = param['dt']
  firing_rate_average = np.zeros(int(T/dt))  
  file_number = 0
  for k in List:
    datafile = datafolder + appendix + '/Series%s/firing_rate.npy'%(k)
    if os.path.isfile(datafile) == True:
      file_number += 1
      firing_rate_average += np.load(datafile, allow_pickle=True)       
    else: continue 
  print("Total file number is %s"%(file_number))     
  firing_rate_average = firing_rate_average/float(file_number) 
  firing_rate_smooth = []
  for i in range(40000):
    firing_rate_smooth.append(np.mean(firing_rate_average[i*2:(i+1)*2])) 

  return np.array(firing_rate_smooth)*40000 # in Hz

def gain_step(List, datafolder, appendix, tau, amplitude):
  import numpy as np
  import math
  param = np.load(datafolder+appendix+'/param.npy', allow_pickle=True)
  param = param.item()
  I_std = param['std']
  firing_rate_smooth = firing_rate_step(List, datafolder, appendix)
  firing_rate_smooth = list(firing_rate_smooth)
  if tau==5:
    fft_firing_rate = np.fft.fft(firing_rate_smooth[20035:] + firing_rate_smooth[0:20035]) 
  if tau==50:
    fft_firing_rate = np.fft.fft(firing_rate_smooth)
  fft_fr = fft_firing_rate[0:len(fft_firing_rate)//2+1]
  fft_firing_odd = np.array([fft_fr[4*i+1] for i in range(len(fft_fr)//4)]) 
  f = np.arange(len(fft_fr)//4)*4+1 
  f = f*(1.0/2000*1000) 
  gain_filt = np.zeros(len(f))
  for i in range(len(f)):
    g = math.e**(-2*math.pi**2*(f-f[i])**2/(f[i]**2)) # Gaussian filters
    g = g/float(sum(g)) # Normalize the filter to have a sum of one.
    gain_filt[i] = abs(sum(fft_firing_odd*g))
  step = np.array([0]*10000+[1]*20000+[0]*10000)*(I_std*amplitude) # in nA
  fft_step = np.fft.fft(step)
  fft_step = fft_step[:len(fft_step)//2+1]
  fft_step_odd = np.array([fft_step[4*i+1] for i in range(len(fft_step)//4)])
  gain = gain_filt/fft_step_odd
  return f, gain, firing_rate_smooth

# self-test
if __name__ == '__main__':
  import numpy as np
  import scipy.io as sio
  hostname = 'chenfei'
  model = 'GE_diam_0'
  runs = 400
  datafolder = '/scratch/%s/%s/'%(hostname, model)

  for tau in (5, ) : 
    for posNa in (47, ): 
      for fr in (519,):
        stim_type = 'OU'
        if stim_type == 'OU':
          appendix = 'tau%sfr%sposNa%s'%(tau, fr, posNa)
          fr_estimated = firing_rate_estimate(range(1, runs+1), datafolder, appendix)
          print('Firing rate is estimated to be %sHz.'%(fr_estimated))
          STA = STA_average(range(1, runs+1), datafolder, appendix) # averaged STA
          [f, gain_filt] = gain(fr_estimated, STA, datafolder, appendix)    
          transferdata = {'f':f, 'gain_tau%sfr%sposNa%s'%(tau, fr, posNa):gain_filt, 'STA':STA}
          np.save(datafolder+'dynamic_gain_Hz_per_nA_tau%sfr%sposNa%s.npy'%(tau, fr, posNa), transferdata)

        if stim_type == 'sinusoidal':
          for amplitude in ([0.2],):
           f = []
           gain_all = []
           for frequency in ([1],): 
             appendix = 'tau%sfr%sposNa%sfrequency%samplitude%s'%(tau, fr, posNa, frequency[0], amplitude[0])
             fr_estimated = firing_rate_estimate(range(1, runs+1), datafolder, appendix)
             print('Firing rate is estimated to be %sHz.'%(fr_estimated))
             param = np.load(datafolder+appendix+'/param.npy', allow_pickle=True)
             param = param.item()
             Istd = param['std']
             gain_vec = gain_sin(range(1, runs+1), datafolder, appendix, frequency[0])
             gain = gain_vec*fr_estimated*2.0/(Istd*amplitude[0])
             f.append(frequency[0])
             gain_all.append(gain)
           np.save(datafolder+'dynamic_gain_all_tau%sfr%sposNa%s_amplitude%s'%(tau,fr,posNa,amplitude[0]), {'f':f, 'gain':gain_all})
          
        if stim_type == 'step':
           amplitude = 0.1
           appendix = 'tau%sfr%sposNa%samplitude%s'%(tau, fr, posNa, amplitude)
           [f, gain, firing_rate_smooth] = gain_step(range(1, runs+1), datafolder, appendix, tau, amplitude)
           transferdata = {'fr_tau%sfr%sposNa%s'%(tau, fr, posNa):firing_rate_smooth, 'gain_step_tau%sfr%sposNa%s'%(tau, fr, posNa):abs(gain), 'f_step_tau%sfr%sposNa%s'%(tau, fr, posNa):f}
           np.save(datafolder+'dynamic_gain_step_%s'%(appendix), transferdata)
