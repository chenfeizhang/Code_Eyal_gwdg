'''

This file calls runme_hist.py to estimate the distribution of inter-spike intervals when the neuron model is driven by the given stochastic stimulus.

'''

import os, sys
import numpy as np
import scipy.io as sio
import subprocess
from subprocess import call

# model name, code directory and data directory
hostname = 'chenfei'
model = 'GE_diam_0'
electrode_place = 'soma'
runs = 400
codedirectory = '..'
datafolder = '/scratch/%s/%s/'%(hostname, model)
outputdirectory = '%sOutput/'%(datafolder)
if os.path.isdir(datafolder) == False:
  os.mkdir(datafolder)
  os.mkdir(outputdirectory)

sys.path.append('%s/scripts'%(codedirectory))
from addparam import addparam # Import function addparam for loading parameters from IparamTable.txt.
IparamTableFile = '%s/Models/%s/IparamTable.txt'%(codedirectory,model) # txt file for stimulus parameters

# command for submitting jobs
def submit_job_array(num_jobs: int, working_directory: str, programme: str, args: list):
    command = ["sbatch"]
    command += ["-p", "medium"]                 # select the partition (queue)
    command += ["-t", "60:00"]                  # maximum runtime
    command += ["--array=1-{}".format(num_jobs)]  # make this a job array
    command += ["-C", "scratch"]                # request access to scratch2
    command += ["--chdir", working_directory]   # set working directory
    command += ["--output", outputdirectory+"%A_%a.out"]
    command += [programme] + args

    print(" ".join(command))
    subprocess.check_call(command)

for tau in (5, ): 
  for posNa in (47, ): 
    for fr in (519,): 
      for amplitude in ([0],):
        for frequency in ([0],): # sinusoidal: ([1],[2],[5],[10],[20],[50],[100],[200],[500],[1000])
          data = sio.loadmat('%s_tau%s_mean_std_cv_%s.mat'%(model, tau, electrode_place))
          mean_list = data['mean'][0]
          std_list = data['std'][0]
          param = {'tau':tau, 'fr':fr, 'posNa':posNa}
          param = addparam(param, IparamTableFile) # add spthr, mean, std to param.
          param['stim_type'] = 'OU'  
          if param['stim_type'] == 'OU' or param['stim_type'] == 'sinusoidal':
            param['T'] = 20000 
          if param['stim_type'] == 'step':
            param['T'] = 2000
          param['T_relax'] = 500 # duration of initial condition randomization (ms)
          param['rep'] = 20 # repetition number
          param['codedirectory'] = codedirectory   
          param['model'] = model 
          param['dt'] = 0.025
          param['amplitude'] = amplitude
          param['frequency'] = frequency
          param['STA_L'] = 1.0 # Length of STA
          param['electrode_place'] = 'soma' # !Check!
          if frequency == [0] and amplitude == [0]: # 'OU'
            appendix = 'tau%sfr%sposNa%s'%(tau, fr, posNa)
          elif frequency == [0] and amplitude != [0]: # 'step'
            appendix = 'tau%sfr%sposNa%samplitude%s'%(tau, fr, posNa, amplitude[0])
          else: # 'sinusoidal'
            appendix = 'tau%sfr%sposNa%sfrequency%samplitude%s'%(tau, fr, posNa, frequency[0], amplitude[0])
          foldername = datafolder + appendix
          if os.path.isdir(foldername) == False:
            os.mkdir(foldername)
          for k in range(300, 270, -10):
            call('mkdir -p ' + foldername + '/Series' + str(k) + '/', shell=True) 
            param['mean'] = mean_list[k]
            param['std'] = std_list[k]
            np.save(foldername+ '/Series%s'%(k) +'/param.npy', param)
            submit_job_array(runs, ".", "runme2.sh", [model, "runme_hist.py", str(k), foldername]) 
   
        
