#!/bin/sh
source /home/despoB/dlurie/.bashrc;
source activate fmriprep;
SUB_ID="${SGE_TASK}";
cd /home/despoB/DistractWM/data/derivatives/fmriprep;
fmriprep \
    /home/despoB/DistractWM/data/raw/BIDS \
    /home/despoB/DistractWM/data/derivatives/fmriprep/out \
    participant \
    --participant_label $SUB_ID \
    --nthreads 6 \
    --mem_mb 10240 \
    --ignore slicetiming \
    --output-space T1w template \
    --no-freesurfer \
    --no-submm-recon \
    -w /home/despoB/DistractWM/data/derivatives/fmriprep/work;
END_TIME=$(date);
echo "FMRIPREP run attempt for $SUB_ID completed at $END_TIME";


