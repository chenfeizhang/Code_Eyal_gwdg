#! /bin/bash
hostname
module load conda
source activate /scratch/chenfei/nrn
CODEDIR=${HOME}/Code_Eyal
${CODEDIR}/Models/$1/x86_64/special -python $2 $3 $4

