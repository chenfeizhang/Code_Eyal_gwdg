'''

This file calls param_step1_runme.py to find the constant input that reproduce target firing rates.

'''

import os
import numpy as np
import subprocess
from subprocess import call 

# model name, code directory and data directory
hostname = 'chenfei'
model = 'GE_diam_0' # model name
electrode_place = 'soma' # The place of input electrode
codedirectory = '..'
datafolder = '/scratch/%s/%s/'%(hostname, model)
outputdirectory = '%sOutput/'%(datafolder)

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

# Make directories for data and output files.
if os.path.isdir(datafolder) == False:
  os.mkdir(datafolder)
if os.path.isdir(outputdirectory) == False:
  os.mkdir(outputdirectory)
rootfolder = datafolder + 'Param/'
if os.path.isdir(rootfolder) == False:
  os.mkdir(rootfolder)


for tau in (5, 50): 
  for (spthr, posNa) in ((-10, 47),): 
    for fr in (5,):
      leftI = -0.1 # lowerbound, chosen by hand
      rightI = 0.1 # upperbound, chosen by hand
      precisionFiringOnset = 1e-2 # Searching stops when the upper and lower bounds are close enough.
      T = 20000 
      dt = 0.025
      param = {}
      param['codedirectory'] = codedirectory   
      param['model'] = model
      param['electrode_place'] = electrode_place
      param['tau'] = tau
      param['spthr'] = spthr
      param['posNa'] = posNa
      param['fr'] = fr
      param['T'] = T  
      param['dt'] = dt
      param['leftI'] = leftI
      param['rightI'] = rightI
      param['precisionFiringOnset'] = precisionFiringOnset
      appendix = 'tau%dfr%dspthr%dposNa%d'%(tau, fr, spthr, posNa)
      foldername = rootfolder + appendix
      call('mkdir -p ' + foldername, shell=True) 
      np.save(foldername+'/param', param)
      submit_job_array(1, ".", "runme.sh", [model, "param_step1_runme.py", foldername])



