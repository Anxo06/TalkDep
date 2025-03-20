#!/bin/bash
#SBATCH --job-name="anxo-llms-persona-api"
#SBATCH --cpus-per-task=2
#SBATCH --ntasks=1
#SBATCH --gpus-per-node=1
#SBATCH --nodelist=tulkas
#SBATCH --mem-per-cpu=16G
#SBATCH -o /mnt/experiments/slurm/logs/anxo/%x-%j.out # File to which STDOUT will be written
#SBATCH -e /mnt/experiments/slurm/logs/anxo/%x-%j.err # File to which STDERR will be written
################################################ tulkas -> namo -> orome -> elrond -> elros ###############################################


LLM_MODEL=$1
export HF_HOME="/mnt/gpu-fastdata/hf-cache/hub" 


SIF="/mnt/experiments/slurm/singularity-containers/anxo/ollama-server.sif"


# Singularity RUN
singularity run --disable-cache --nv --bind /mnt:/mnt --network=host $SIF $LLM_MODEL
