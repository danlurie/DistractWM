import os
import traceback
import numpy as np
import pandas as pd
from glob import glob

# Define hard-coded input/output parameters and file path templates.
SUBJECT_LIST_FILE = '/home/despoB/DistractWM/code/fmriprep/sge/subject_list.txt'
SKIP_LIST = '/home/despoB/DistractWM/data/derivatives/group_level_analyses/custom/meta/subjects_to_skip.csv'
COVERAGE_FILE_GLOB_FPT = '/home/despoB/DistractWM/data/derivatives/custom/sub-{0}/func/sub-{0}_task-*_bold_space-MNI152NLin2009cAsym_atlas-BNA_EPIcoverage.csv'
DERIVATIVES_OUT_DIR = '/home/despoB/DistractWM/data/derivatives/group_level_analyses/custom/meta'
assert (os.path.exists(DERIVATIVES_OUT_DIR)),"Output directory does not exist!"
ATLAS_ROIS = 246

# Load the subject list.
subject_list = np.loadtxt(SUBJECT_LIST_FILE, dtype='int')
subject_list = [str(i) for i in subject_list]

# Load the skip list.
skip_list_df = pd.read_csv(SKIP_LIST, usecols=['sub-id'])
skip_list = [str(i) for i in skip_list_df['sub-id'].values]

# Initialize a list with all ROIs.
superset = set(range(1,ATLAS_ROIS+1))

# Loop through subjects.
for sub_id in subject_list:
    if sub_id not in skip_list:
        try:
            print("Subject {0}...".format(sub_id))
            
            # Get a list of all brain masks.
            coverage_files = glob(COVERAGE_FILE_GLOB_FPT.format(sub_id))
      
            # Loop through covearge files.
            for cov_csv in coverage_files:
                # Load the coverage data.
                cov_data = pd.read_csv(cov_csv, index_col='roi_label')
                # Get the set of ROI's with sufficient coverage. 
                to_keep = set(cov_data[cov_data['pct_cov'] > 50].index.values)
                # Keep only ROI's that have good coverage in everyone so far.
                superset.intersection_update(to_keep)
                # If many ROIs are missing, notify the user.
                n_missing = ATLAS_ROIS - len(to_keep)
                if n_missing >= 15:
                    print("...{0} has {1} missing ROIs".format(os.path.basename(cov_csv), n_missing))

            print('...Done!')

        except:
            print("Something went wrong!")
            traceback.print_exc()
            print("Moving on to the next subject.")
            pass

# Save the list of common ROIs
np.savetxt(os.path.join(DERIVATIVES_OUT_DIR, 'common-ROIs_exclude-skips__brainnetome.txt'),
        np.array(list(superset)), fmt='%s')
print('Final ROI set contains {0} regions.'.format(len(superset)))
