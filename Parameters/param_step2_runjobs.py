'''

For a given mean of the stimulus, search for the std of the stimulus that generates expected firing rate. Finishing param_step1_runjobs.py is required before running this file.

Current file defines model name and parameters, calls param_step2_runme.py, and submits jobs to clusters for std searching. 

Parameter definitions are the same with those in param_step1_runjobs.py

'''

import numpy as np
import subprocess
from subprocess import call

# model name, code directory and data directory
hostname = 'chenfei'
model = 'GE_diam_0'
codedirectory = '..'
datafolder = '/scratch/%s/%s/'%(hostname, model)
outputdirectory = '%sOutput/'%(datafolder)

# command for submitting jobs
runs = 400
def submit_job_array(num_jobs: int, working_directory: str, programme: str, args: list):
    command = ["sbatch"]
    command += ["-p", "medium"]                 # select the partition (queue)
    command += ["-t", "240:00"]                  # maximum runtime
    command += ["--array=1-{}".format(num_jobs)]  # make this a job array
    command += ["-C", "scratch"]                # request access to scratch2
    command += ["--chdir", working_directory]   # set working directory
    command += ["--output", outputdirectory+"%A_%a.out"]
    command += [programme] + args

    print(" ".join(command))
    subprocess.check_call(command)


for tau in (5, 50, ): 
  for (spthr,posNa) in ((-10, 47),):
    for fr in (5, ):
      appendix = 'tau%dfr%dspthr%dposNa%d'%(tau, fr, spthr, posNa)
      foldername = datafolder + 'Param/' + appendix  
      data = np.load(foldername + '/param.npy', allow_pickle=True)
      param = data.item() 
      param['leftStd'] = 0.000001 # lowerbound
      param['rightStd'] = 1 # upperbound
      param['precision_std'] = 1e-3 # relative error for parameter searching
      param['runs'] = runs
      np.save(foldername+'/param', param)
      for i in range(1,runs+1):
        call('mkdir -p ' + foldername + '/mean'+str(i), shell=True)
      submit_job_array(runs, ".", "runme.sh", [model, "param_step2_runme.py",  foldername]) # Submit jobs, pass runs and foldername into the job script.
