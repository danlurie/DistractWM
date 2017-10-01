#!/bin/sh
source /home/despoB/dlurie/.bashrc;
source activate mriqc;
export PATH=/home/despoB/kaihwang/bin/afni/:$PATH;
SUB_ID="${SGE_TASK}";
cd /home/despoB/DistractWM/data/mriqc;
mriqc \
    /home/despoB/DistractWM/data/BIDS \
    /home/despoB/DistractWM/data/mriqc/out \
    participant \
    --participant_label $SUB_ID \
    -m T1w bold \
    -w /home/despoB/DistractWM/data/mriqc/work \
    --verbose-reports \
    --n_procs 5 \
    --mem_gb 8 \
    --ants-nthreads 3;
END_TIME=$(date);
echo "MRIQC run attempt for $SUB_ID completed at $END_TIME";


