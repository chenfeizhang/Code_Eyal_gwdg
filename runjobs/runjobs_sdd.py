'''

This file calls runme_sdd.py to run neuron model simulation and calculate spike triggered average (STA) for OU stimulus. The spike detection is chosen as the last time axonal voltage increases across V_{loc} before spike initiation.

'''

import os, sys
import numpy as np
import subprocess
from subprocess import call

# model name, code directory and data directory
hostname = 'chenfei'
model = 'GE_diam_0'
runs = 400
codedirectory = '..'
datafolder = '/scratch/%s/%s/'%(hostname, model) # data folder
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
    command += ["-t", "180:00"]                  # maximum runtime
    command += ["--array=1-{}".format(num_jobs)]  # make this a job array
    command += ["-C", "scratch"]                # request access to scratch2
    command += ["--chdir", working_directory]   # set working directory
    command += ["--output", outputdirectory+"%A_%a.out"]
    command += [programme] + args

    print(" ".join(command))
    subprocess.check_call(command)

# local minimum of phase plot
if model == 'GE_diam_0':
  v_loc = -58.05 
if model == 'GE_diam_3':
  v_loc = -54.72 
if model == 'GE_diam_5':
  v_loc = -53.61 

for tau in (5, ):
  for posNa in (47, ): 
    for fr in (519,): 
      for amplitude in ([0],):
        for frequency in ([0],): 
          param = {'tau':tau, 'fr':fr, 'posNa':posNa}
          param = addparam(param, IparamTableFile) # add spthr, mean, std to param.
          param['stim_type'] = 'OU' 
          if param['stim_type'] == 'OU' or param['stim_type'] == 'sinusoidal':
            param['T'] = 20000 
          if param['stim_type'] == 'step':
            param['T'] = 2000
          param['T_relax'] = 500 # duration of initial condition randomization (ms)
          param['rep'] = 50  # repetition number
          param['codedirectory'] = codedirectory   
          param['model'] = model 
          param['dt'] = 0.025
          param['amplitude'] = amplitude
          param['frequency'] = frequency
          param['STA_L'] = 1.0 # Length of STA 
          param['electrode_place'] = 'soma' 
          param['v_loc'] = v_loc
          if frequency == [0] and amplitude == [0]: # 'OU'
            appendix = 'tau%sfr%sposNa%s_sdd'%(tau, fr, posNa)
          elif frequency == [0] and amplitude != [0]: # 'step'
            appendix = 'tau%sfr%sposNa%samplitude%s_sdd'%(tau, fr, posNa, amplitude[0])
          else: # 'sinusoidal'
            appendix = 'tau%sfr%sposNa%sfrequency%samplitude%s_sdd'%(tau, fr, posNa, frequency[0], amplitude[0])
          foldername = datafolder + appendix
          if os.path.isdir(foldername) == False:
            os.mkdir(foldername)
          # make directory for bootstrapping confidence interval
          if os.path.isdir(foldername+'/bootstrapping') == False:
            os.mkdir(foldername+'/bootstrapping')
          # make directory for null hypothesis test
          if os.path.isdir(foldername+'/nullhypothesis') == False:
            os.mkdir(foldername+'/nullhypothesis')
          for i in range(1,runs+1):
            call('mkdir -p ' + foldername + '/Series' + str(i) + '/', shell=True) 
          np.save(foldername+'/param.npy', param)        
          submit_job_array(runs, ".", "runme.sh", [model, "runme_sdd.py", foldername]) 
