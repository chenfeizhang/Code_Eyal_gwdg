'''

Calculate confidence intervals of linear response curves.

This file calls bootstrapping_runme.py and creates 1000 jobs for bootstrapping. For each bootstrapping, it randomly select STA files from series folder with replacement. The total number of STAs is the same with than in runjobs.py. Linear response curves are calculated with the randomly selected STAs.

Bootstrapping boundary is the middle 95 percent range of 1000 curves. The boundary is determined by bootstrapping_step2.py.

'''
import subprocess
from subprocess import call

hostname = 'chenfei'
model = 'GE_diam_0'
runs = 1000
stim_type = 'OU'
codedirectory = '..'
datafolder = '/scratch/%s/%s/'%(hostname, model)
outputdirectory = '%sOutput/'%(datafolder)

def submit_job_array(num_jobs: int, working_directory: str, programme: str, args: list):
    command = ["sbatch"]
    command += ["-p", "medium"]                 # select the partition (queue)
    command += ["-t", "10:00"]                  # maximum runtime
    command += ["--array=1-{}".format(num_jobs)]  # make this a job array
    command += ["-C", "scratch"]                # request access to scratch2
    command += ["--chdir", working_directory]   # set working directory
    command += ["--output", outputdirectory+"%A_%a.out"]
    command += [programme] + args

    print(" ".join(command))
    subprocess.check_call(command)

submit_job_array(runs, ".", "runme2.sh", [model, "bootstrapping_runme.py",stim_type, datafolder])
