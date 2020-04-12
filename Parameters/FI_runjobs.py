#! /usr/bin/python

'''
This file calls FI_runme.py to calculate the F-I curve of the neuron model.

The range of the input I is from leftI to rightI.

In each job, the neuron model is injected with a constant input at the soma to estimate the firing rate.
'''

hostname = 'chenfei'
model = 'GE_diam_0' # model name
codedirectory = '..'
datafolder = '/scratch/%s/%s/'%(hostname, model)
outputdirectory = '%sOutput/'%(datafolder)

runs = 500 # job number
import subprocess
# job submission function
def submit_job_array(num_jobs: int, working_directory: str, programme: str, args: list):
    command = ["sbatch"]
    command += ["-p", "medium"]                 # select the partition (queue)
    command += ["-t", "30:00"]                  # maximum runtime
    command += ["--array=1-{}".format(num_jobs)]  # make this a job array
    command += ["-C", "scratch"]                # request access to scratch2
    command += ["--chdir", working_directory]   # set working directory
    command += ["--output", outputdirectory+"%A_%a.out"]
    command += [programme] + args

    print(" ".join(command))
    subprocess.check_call(command)



import time, os
import numpy as np
from subprocess import call

# make directory
rootfolder = datafolder + 'FI_constant/'
if os.path.isdir(rootfolder) == False:
  os.mkdir(rootfolder)


for (spthr,posNa) in ((-10, 47),): 
  appendix = 'posNa%s'%(posNa)
  foldername = rootfolder + appendix  
  call('mkdir -p ' + foldername, shell=True) 
  param = {} # parameter dictionary
  leftI = 0.0 # nA
  rightI = 0.2 # nA
  Iconst = np.linspace(leftI, rightI, runs)
  T = 100000 # ms
  dt = 0.025 # ms
  param['codedirectory'] = codedirectory 
  param['model'] = model
  param['spthr'] = spthr
  param['posNa'] = posNa
  param['T'] = T  
  param['dt'] = dt
  param['Iconst'] = Iconst
  np.save(foldername+'/param', param)
  submit_job_array(runs, ".", "runme.sh", [model, "FI_runme.py", foldername])
