import os
import numpy as np
import pandas as pd
from glob import glob

# Define hard-coded input/output parameters.
SUBJECT_LIST_FILE = '/home/despoB/DistractWM/code/fmriprep/sge/subject_list.txt'
CONFOUNDS_GLOB_FPT = '/home/despoB/DistractWM/data/derivatives/fmriprep/out/fmriprep/sub-{0}/func/sub-{0}_task-*_bold_confounds.tsv'
DERIVATIVES_OUT_DIR = '/home/despoB/DistractWM/data/derivatives/custom/'

# Load the subject list.
subject_list = np.loadtxt(SUBJECT_LIST_FILE, dtype='int')
subject_list = [str(i) for i in subject_list]

# Loop through subjects.
for sub_id in subject_list:
    # Get a list of all FMRIPREP confounds files.
    confound_files = glob(CONFOUNDS_GLOB_FPT.format(sub_id))

    # If the subject custom derivatives /func directory doesn't exist, create it.
    subject_out_dir = os.path.join(DERIVATIVES_OUT_DIR, 'sub-{0}'.format(sub_id), 'func')
    if os.path.isdir(subject_out_dir) is not True:
        os.makedirs(subject_out_dir)

    # Loop through confounds files.
    for tsv_path in confound_files:
        # Load the FMRIPREP confounds.
        all_confounds = pd.read_csv(tsv_path, sep='\t')

        # Extract the 6 rigid-body motion parameters.
        motion_parameters = all_confounds[['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ']].copy()

        # Create squared versions of each motion parameter at Tt
        for mopar in ['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ']:
            sq_col_name = mopar+'sq'
            sq_col_data = np.square(motion_parameters[mopar])
            motion_parameters.loc[:,sq_col_name] = sq_col_data

        # Include parameter set from volume t-1
        zpad = pd.Series([0])
        for mopar in nuisance_vars.columns[-12:]:
            pv_col_name = mopar+'_t-1'
            pv_col_data = zpad.append(nuisance_vars[mopar], ignore_index=True)[:-1]
            nuisance_vars.loc[:,pv_col_name] = pv_col_data

        nuisance_vars.to_csv(motion24_fpt.format(pid,epi_acq), sep=',', index=False)




def compute_mopars(epi_acq):
    # Load list of subjects with the specified EPI sequence.
    sublist_file = '/home/despoB/dlurie/Projects/despolab_lesion/derivatives/has_acq-{0}.txt'.format(epi_acq)
    subject_list = np.loadtxt(sublist_file, dtype='int')
    subject_list = [str(i) for i in subject_list]

    print("Processing {0} patients who were scanned with the {1} sequence...".format(str(len(subject_list)), epi_acq))

    # Set file path templates
    confounds_fpt = '/home/despoB/dlurie/Projects/despolab_lesion/preproc/out/fmriprep/sub-{0}/func/sub-{0}_task-rest_acq-{1}_run-01_bold_confounds.tsv'
    motion24_fpt = '/home/despoB/dlurie/Projects/despolab_lesion/derivatives/sub-{0}/func/sub-{0}_task-rest_acq-{1}_run-01_bold_confounds-motion24.csv'

    for pid in subject_list:
        print("...computing 24 motion parameters for patient {0}...".format(pid))
        
        os.mkdir('/home/despoB/dlurie/Projects/despolab_lesion/derivatives/sub-{0}/func'.format(pid))
        bold_confounds = confounds_fpt.format(pid,epi_acq)

        all_confounds = pd.read_csv(bold_confounds, sep='\t')

        nuisance_vars = all_confounds[['aCompCor0', 'aCompCor1', 'aCompCor2', 'aCompCor3', 'aCompCor4', 'aCompCor5',
                                      'X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ']].copy()

        # Create squared versions of each motion parameter at Tt
        for mopar in ['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ']:
            sq_col_name = mopar+'sq'
            sq_col_data = np.square(nuisance_vars[mopar])
            nuisance_vars.loc[:,sq_col_name] = sq_col_data

        # Include parameter set from volume t-1
        zpad = pd.Series([0])
        for mopar in nuisance_vars.columns[-12:]:
            pv_col_name = mopar+'_t-1'
            pv_col_data = zpad.append(nuisance_vars[mopar], ignore_index=True)[:-1]
            nuisance_vars.loc[:,pv_col_name] = pv_col_data

        nuisance_vars.to_csv(motion24_fpt.format(pid,epi_acq), sep=',', index=False)

for acq in ['128px', '64px']:
    compute_mopars(acq)

