import os
import traceback
import matlab.engine
import numpy as np
import pandas as pd
from glob import glob

# Define subject list and subject-skip list.
SUBJECT_LIST_FILE = '/home/despoB/DistractWM/code/fmriprep/sge/subject_list.txt'
SKIP_LIST = '/home/despoB/DistractWM/data/derivatives/group_level_analyses/custom/meta/subjects_to_skip.csv'

# Define input file path templates and output directory.
CORRMAT_GLOB_FPT = '/home/despoB/DistractWM/data/derivatives/custom/sub-{0}/func/cond*_beta-series/sub-{0}_task-DistractWM_contrast-cond*_space-MNI152Lin2009Asym_atlas-BNA_corrmat.npy'
DERIVATIVES_OUT_DIR = '/home/despoB/DistractWM/data/derivatives/custom/'
assert (os.path.exists(DERIVATIVES_OUT_DIR)),"Output directory does not exist!"

# Load ROI labels (full-atlas and common-coverage)
BNA_roi_labels_all = range(1,247)
common_roi_labels = np.loadtxt('/home/despoB/DistractWM/data/derivatives/group_level_analyses/custom/meta/common-ROIs_exclude-skips__brainnetome.txt', dtype='int')
common_roi_index = np.in1d(BNA_roi_labels_all, common_roi_labels)

# Load the subject list.
subject_list = np.loadtxt(SUBJECT_LIST_FILE, dtype='int')
subject_list = [str(i) for i in subject_list]

# Load the skip list.
skip_list_df = pd.read_csv(SKIP_LIST, usecols=['sub-id'])
skip_list = [str(i) for i in skip_list_df['sub-id'].values]

# Initialize MATLAB interface
eng = matlab.engine.start_matlab()
eng.addpath('/home/despoB/dlurie/Software/matlab/custom', nargout=0)

# Set pipeline parameters
alg = 'Louvain'
thresh = 'None'
gamma = 1.0

# Loop through subjects.
for sub_id in subject_list[0:1]:
    if sub_id not in skip_list:
        try:
            print("Subject {0}...".format(sub_id))
            
            # Get a list of all brain masks.
            corrmat_files = glob(CORRMAT_GLOB_FPT.format(sub_id))

            # If the subject graph output directory for these paramters doen't already exist, create it.
            subject_out_dir = os.path.join(DERIVATIVES_OUT_DIR, 'sub-{0}'.format(sub_id), 'func')
            graph_out_dir = os.path.join(subject_out_dir, 'alg-{0}_thresh-{1}_gamma-{2}_graphdata'.format(alg, thresh, str(gamma)))
            if os.path.isdir(graph_out_dir) is not True:
                os.makedirs(graph_out_dir)
      
            # Loop through scans.
            for corrmat_npy in corrmat_files:
                print('...Contrast: {0}...'.format(os.path.basename(corrmat_npy)))
                print('......Preparing data...')

                # Load the raw correlation matrix and zero the diagonal.
                corrmat = np.load(corrmat_npy)
                np.fill_diagonal(corrmat, 0)
                
                # Filter the matrix by the list of ROIs
                corrmat_filtered = corrmat[common_roi_index][:,common_roi_index]  
                
                # Z-score the filtered matrix and save it.
                corrmat_filtered_z = np.arctanh(corrmat_filtered)
                corrmat_z_path = os.path.join(graph_out_dir, os.path.basename(corrmat_npy).rstrip('corrmat.npy')+'corrmat_z.txt')
                np.savetxt(corrmat_z_path, corrmat_filtered_z)

                # Run graph-theory pipeline
                print('......Running MATLAB graph pipeline...')
                out_prefix = os.path.join(graph_out_dir, os.path.basename(corrmat_npy).rstrip('_corrmat.npy'))
                res = eng.run_louvain_z(1.0, corrmat_z_path, out_prefix, nargout=0)
            print('...Done!')

        except:
            print("Something went wrong!")
            traceback.print_exc()
            print("Moving on to the next subject.")
            pass


