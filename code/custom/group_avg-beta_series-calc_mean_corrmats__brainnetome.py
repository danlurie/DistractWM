import os
import traceback
import numpy as np

# Define hard-coded input/output parameters and file path templates.
SUBJECT_LIST_FILE = '/home/despoB/DistractWM/code/fmriprep/sge/subject_list.txt'
EXCLUDE_LIST_FILE = '/home/despoB/DistractWM/data/derivatives/group_level_analyses/custom/meta/subjects_to_skip.csv'
BS_CORRMATZ_FPT = '/home/despoB/DistractWM/data/derivatives/custom/sub-{0}/func/alg-Louvain_thresh-None_gamma-1.0_graphdata/sub-{0}_task-DistractWM_contrast-cond{1}_space-MNI152Lin2009Asym_atlas-BNA_corrmat_z.txt'
DERIVATIVES_OUT_DIR = '/home/despoB/DistractWM/data/derivatives/group_level_analyses/custom/group_avg_networks'
CMAT_FNAME_FPT = 'groupavg_task-DistractWM_contrast-cond{0}_space-MNI152Lin2009Asym_atlas-BNA_corrmat_z.txt'

# If necessary, create the output directory:
if os.path.isdir(DERIVATIVES_OUT_DIR) is not True:
    os.makedirs(DERIVATIVES_OUT_DIR)

# Load the subject list.
subject_list = np.loadtxt(SUBJECT_LIST_FILE, dtype='int')
subject_list = [str(i) for i in subject_list]

# Load the exclude list.
exclude_list = np.loadtxt(EXCLUDE_LIST_FILE, skiprows=1, usecols=0, dtype='i', delimiter=',')
exclude_list = [str(i) for i in exclude_list]

# Define contrast conditions.
conditions = range(1,13)
conditions = [str(i) for i in conditions]

# Loop throuch contrasts
for contrast in conditions:
    mat_stack = []
    print("Condition: {0}...".format(contrast))
    
    # Loop through subjects.
    for sub_id in subject_list:
        if sub_id not in exclude_list:
            try:
                # Define the path to the z-scored correlation matrix
                corrmat_z_path = BS_CORRMATZ_FPT.format(sub_id, contrast)
                assert (os.path.exists(corrmat_z_path)),"Z-scored correlation matrix does not exist for subject {0}, contrast {1}!".format(sub_id, contrast)
               
                # Load the correlation matrix.
                cmz = np.loadtxt(corrmat_z_path)
                
                # Add the matrix to the stack.
                mat_stack.append(cmz)

            except:
                print("Something went wrong!")
                traceback.print_exc()
                print("Moving on to the next subject.")
                pass

    # Compute the mean across subjects
    mean_mat = np.mean(np.array(mat_stack), axis=0)
    
    # Save the mean matrix.
    corrmat_out_fname = CMAT_FNAME_FPT.format(contrast)
    np.savetxt(os.path.join(DERIVATIVES_OUT_DIR, corrmat_out_fname),mean_mat)

    print("...Done!")

            

