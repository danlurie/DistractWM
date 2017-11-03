import os
import traceback
import subprocess
import numpy as np
from glob import glob

# Define hard-coded input/output parameters and file path templates.
SUBJECT_LIST_FILE = '/home/despoB/DistractWM/code/fmriprep/sge/subject_list.txt'
BS_DIR_GLOB_FPT = '/home/despoB/kiyonaga/ProcessedData/DistractWM/Results_spm_fromfmriprep/BetaSeries/sub-{0}/cond*' 
DERIVATIVES_OUT_DIR = '/home/despoB/DistractWM/data/derivatives/custom/'

# Load the subject list.
subject_list = np.loadtxt(SUBJECT_LIST_FILE, dtype='int')
subject_list = [str(i) for i in subject_list]

# Loop through subjects.
for sub_id in subject_list:
    try:
        print("Subject {0}...".format(sub_id))
        
        # Get a list of all BetaSeries contrast sub-directories
        bs_contrasts = glob(BS_DIR_GLOB_FPT.format(sub_id))

        # If the subject custom derivatives /func directory doesn't exist, raise an error.
        subject_out_dir = os.path.join(DERIVATIVES_OUT_DIR, 'sub-{0}'.format(sub_id), 'func')
        assert (os.path.isdir(subject_out_dir)),"No /derivatives/custom/../func/ directory found!"
  
        # Loop throuch contrasts
        for contrast in bs_contrasts:
            print("...Beta Series contrast: "+os.path.basename(contrast))

            # Get a list of all the individual beta maps.
            beta_maps = os.listdir(contrast)
            print("......Found {0} beta maps; merging to 4D...".format(len(beta_maps)))

            # Get the full path to each beta map.
            beta_map_paths = [os.path.join(contrast, i) for i in beta_maps]

            # If an output directory for this contrast does not yet exist, create it.
            contrast_out_dir = os.path.join(subject_out_dir, os.path.basename(contrast)+'_beta-series')
            if os.path.isdir(contrast_out_dir) is not True:
                os.mkdir(contrast_out_dir)

            # Define the output file name.
            merged_nifti_fname = 'sub-{0}_task-DistractWM_contrast-{1}_space-MNI152Lin2009Asym_betaseries.nii.gz'.format(sub_id, os.path.basename(contrast))

            # Construct fslmerge command
            fsl_cmd = ['fslmerge', '-t', os.path.join(contrast_out_dir,merged_nifti_fname)]
            fsl_cmd = fsl_cmd + beta_map_paths

            # Run fslmerge
            res = subprocess.check_call(fsl_cmd)

            print("...Done!")

    except:
        print("Something went wrong!")
        traceback.print_exc()
        print("Moving on to the next subject.")
        pass



# for each subject

# look in annies BetaSeries folder for the subject sub-directory

# In each subject sub-directory, list the contrast folders

# For each contrast folder

# Get a list of all nifti files

# Check if an equivalent contrast folder exists in /derivatives/custom, if not create it

# call fslmerge with the list of nifti files
