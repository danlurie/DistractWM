for subj in {102..123}; do
    heudiconv \
    -d /home/despoB/DistractWM/data/RawData/Distractwm_{subject}/Despo_Lab_Anastasia*/*/*.dcm \
    -s $subj \
    -c dcm2niix \
    -o /home/despoB/DistractWM/data/BIDS/ \
    -f /home/despoB/dlurie/Software/heudiconv/heuristics/uc_bids_DistractWM.py \
    --bids \
    --minmeta
done
