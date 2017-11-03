import os
import numpy as np
import pandas as pd
from glob import glob
#import pdb
import traceback

# Define hard-coded input/output parameters.
SUBJECT_LIST_FILE = '/home/despoB/DistractWM/code/fmriprep/sge/subject_list.txt'
CONFOUNDS_GLOB_FPT = '/home/despoB/DistractWM/data/derivatives/fmriprep/out/fmriprep/sub-{0}/func/sub-{0}_task-*_bold_confounds.tsv'
DERIVATIVES_OUT_DIR = '/home/despoB/DistractWM/data/derivatives/custom/'

# Load the subject list.
subject_list = np.loadtxt(SUBJECT_LIST_FILE, dtype='int')
subject_list = [str(i) for i in subject_list]

# Loop through subjects.
for sub_id in subject_list:
    try:
        print("...computing 24 motion parameters for subject {0}...".format(sub_id))
        
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

            # Create squared versions of each motion parameter at volume t0
            for mopar in ['X', 'Y', 'Z', 'RotX', 'RotY', 'RotZ']:
                sq_col_name = mopar+'Sq'
                sq_col_data = np.square(motion_parameters[mopar])
                motion_parameters.loc[:,sq_col_name] = sq_col_data

            #pdb.set_trace()

            # Include parameter set from volume t-1
            zpad = pd.Series([0])
            for mopar in motion_parameters.columns:
                if 'Sq' in mopar:
                    pv_col_name = mopar.rstrip('Sq')+'ShiftBackSq'
                else:
                    pv_col_name = mopar+'ShiftBack'

                pv_col_data = zpad.append(motion_parameters[mopar], ignore_index=True)[:-1]
                motion_parameters.loc[:,pv_col_name] = pv_col_data

            out_fname = os.path.basename(tsv_path).rstrip('confounds.tsv')+'motion.tsv'
            print(out_fname)
            motion_parameters.to_csv(os.path.join(subject_out_dir, out_fname), sep=',', index=False)
    except:
        print("Something went wrong!")
        traceback.print_exc()
        print("Moving on to the next subject...")
        pass
