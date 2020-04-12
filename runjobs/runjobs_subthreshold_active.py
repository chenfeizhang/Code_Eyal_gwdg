'''

This file calls runme_subthreshold_active.py to generate axonal voltages and stimuli for calculating electrotonic filtering. Electrotonic filtering is defined as the Fourier transform of subthreshold voltage (voltage trace not containing spike waveforms) to the Fourier transform of corresponding stimulus.

Neuron models are injected with the same stochastic stimuli for calculating linear response curves, togeter with a small amplitude sinusoidal signal. 

'''

import os, sys
import numpy as np
from subprocess import call
import subprocess

# model name, code directory and data directory
hostname = 'chenfei'
model = 'GE_diam_0'
runs = 400
codedirectory = '..'
datafolder = '/scratch/%s/%s/'%(hostname, model) 
outputdirectory = '%sOutput/'%(datafolder)
if os.path.isdir(datafolder) == False:
  os.mkdir(datafolder)
  os.mkdir(outputdirectory)

sys.path.append('%s/scripts'%(codedirectory))
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
    command += ["-t", "500:00"]                  # maximum runtime
    command += ["--array=1-{}".format(num_jobs)]  # make this a job array
    command += ["-C", "scratch"]                # request access to scratch2
    command += ["--chdir", working_directory]   # set working directory
    command += ["--output", outputdirectory+"%A_%a.out"]
    command += [programme] + args

    print(" ".join(command))
    subprocess.check_call(command)

for tau in (5,): 
  for posNa in (47,): 
    for fr in (519, ):
      param = {'tau':tau, 'fr':fr, 'posNa':posNa}
      param = addparam(param, IparamTableFile) # add thr, spthr, mean, std to param.
      param['T'] = 100000 # duration of model simulation for va (ms)
      param['T_relax'] = 1000 # duration of initial condition randomization (ms)
      param['rep'] = 200 # repetition number
      param['codedirectory'] = codedirectory   
      param['model'] = model 
      param['dt'] = 0.025
      appendix = 'tau%sfr%sposNa%s'%(tau, fr, posNa)
      foldername = datafolder + appendix + '_subthreshold_v2' # appendix with subthreshold
      if os.path.isdir(foldername) == False:
        os.mkdir(foldername)
      np.save(foldername+'/param.npy', param)  
      submit_job_array(runs, ".", "runme.sh", [model, "runme_subthreshold_active.py", foldername])
