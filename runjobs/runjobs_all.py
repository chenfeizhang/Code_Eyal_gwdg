'''

This file calls runme_all.py to run neuron model simulation and calculate spike triggered average (STA) for OU stimulus. For the OU stimulus with a sinusoidal current, it calls runme_all.py to generate spike times to calculate vector strengths of different frequencies. For the OU stimulus with a step current, it calls runme_all.py to generate spike times and calculate the population firing rate. 

The mean and std of the stimulus are chosen to fix firing rate and coefficient variation (CV) of inter spike intervals. Stochastic stimulus always starts from its mean. Neuron voltage always starts with resting potential. Gating variables of ion channels start at corresponding voltage values.

In each job, the number of independent model simulation is denoted as rep. The duration of simulation time is T_relax+T. T_relax is the duration for randomization of initial condition. The duration of formal simulation is T.

The average of all spike triggered stimuli centered around corresponding spike times is the STA. The length of STA is denoted as STA_L. Spikes with a complete spike triggered stimulus interval within duration T are included for STA calculation.

Parameter definitions are the same with those in param_step1_runjobs.py

'''

import os, sys
import numpy as np
import subprocess
from subprocess import call

# model name, code directory and data directory
hostname = 'chenfei'
model = 'GE_diam_0'
runs = 1
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


for tau in (5, ):
  for posNa in (47, ): 
    for fr in (519,): 
      for amplitude in ([0],):
        for frequency in ([0],): # sinusoidal: ([1],[2],[5],[10],[20],[50],[100],[200],[500],[1000])
          param = {'tau':tau, 'fr':fr, 'posNa':posNa}
          param = addparam(param, IparamTableFile) # add spthr, mean, std to param.
          param['stim_type'] = 'OU' # 
          if param['stim_type'] == 'OU' or param['stim_type'] == 'sinusoidal':
            param['T'] = 20000 
          if param['stim_type'] == 'step':
            param['T'] = 2000
          param['T_relax'] = 500 # duration of initial condition randomization (ms)
          param['rep'] = 50  # repetition number, rep=50 for OU and sinusoidal, rep=1000 for step
          param['codedirectory'] = codedirectory   
          param['model'] = model 
          param['dt'] = 0.025
          param['amplitude'] = amplitude
          param['frequency'] = frequency
          param['STA_L'] = 1.0 # Length of STA 
          param['electrode_place'] = 'soma' # place of the input electrode
          if frequency == [0] and amplitude == [0]: # 'OU'
            appendix = 'tau%sfr%sposNa%s'%(tau, fr, posNa)  
          elif frequency == [0] and amplitude != [0]: # 'step'
            appendix = 'tau%sfr%sposNa%samplitude%s'%(tau, fr, posNa, amplitude[0])
          else: # 'sinusoidal'
            appendix = 'tau%sfr%sposNa%sfrequency%samplitude%s'%(tau, fr, posNa, frequency[0], amplitude[0])
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
          submit_job_array(runs, ".", "runme.sh", [model, "runme_all.py", foldername])
