import os
import traceback
import pandas as pd
import numpy as np
import nibabel as nib
from glob import glob
from nilearn import input_data, image

# Define hard-coded input/output parameters and file path templates.
SUBJECT_LIST_FILE = '/home/despoB/DistractWM/code/fmriprep/sge/subject_list.txt'
SKIP_LIST = '/home/despoB/DistractWM/data/derivatives/group_level_analyses/custom/meta/subjects_to_skip.csv'
BS_DIR_GLOB_FPT = '/home/despoB/DistractWM/data/derivatives/custom/sub-{0}/func/cond*_beta-series'
BS_NII_FPT = 'sub-{0}_task-DistractWM_contrast-{1}_space-MNI152Lin2009Asym_betaseries.nii.gz'
BNA_FILE = '/home/despoB/dlurie/Data/reference/Brainnetome/BNA-maxprob-thr25-1mm.nii.gz' 
DERIVATIVES_OUT_DIR = '/home/despoB/DistractWM/data/derivatives/custom'

# Load the subject list.
subject_list = np.loadtxt(SUBJECT_LIST_FILE, dtype='int')
subject_list = [str(i) for i in subject_list]

# Load the skip list.
skip_list_df = pd.read_csv(SKIP_LIST, usecols=['sub-id'])
skip_list = [str(i) for i in skip_list_df['sub-id'].values]

# Loop through subjects.
for sub_id in subject_list:
    if sub_id not in skip_list:
        try:
            print("Subject {0}...".format(sub_id))
            
            # Get a list of all BetaSeries contrast sub-directories
            bs_contrasts = glob(BS_DIR_GLOB_FPT.format(sub_id))

            # If the subject custom derivatives /func directory doesn't exist, raise an error.
            subject_out_dir = os.path.join(DERIVATIVES_OUT_DIR, 'sub-{0}'.format(sub_id), 'func')
            assert (os.path.isdir(subject_out_dir)),"No /derivatives/custom/../func/ directory found!"

            # Loop throuch contrasts
            for contrast in bs_contrasts:
                print("Contrast: "+os.path.basename(contrast))
                
                # Set the paths to the beta series file
                bs_nii_fname = BS_NII_FPT.format(sub_id, os.path.basename(contrast.rstrip('_beta-series')))
                bs_nii_path = os.path.join(contrast, bs_nii_fname)
                assert (os.path.exists(bs_nii_path)),"Beta Series image does not exist!"

                # Load Brainnetome atlas
                bna_img = nib.load(BNA_FILE)

                # Load beta series image and remove NaN values
                bs_nii_img = nib.load(bs_nii_path)
                bs_nii_img = image.math_img('np.nan_to_num(img1)', img1=bs_nii_img)

                # Set up the Brainnetome Labels Masker
                bna_masker = input_data.NiftiLabelsMasker(labels_img=bna_img, background_label=0, resampling_target="data")

                # Extract ROI beta series
                print("...extracting Brainnetome beta series...")
                beta_series = bna_masker.fit_transform(bs_nii_img)
                        
                # Compute and save correlation matrix
                print("...computing correlation matrix...")
                corrmat = np.corrcoef(beta_series.T)
                corrmat_out_fname = os.path.basename(bs_nii_path).rstrip('betaseries.nii.gz')+'atlas-BNA_corrmat.npy'
                np.save(os.path.join(contrast, corrmat_out_fname), corrmat)

                print("...Done!")

        except:
            print("Something went wrong!")
            traceback.print_exc()
            print("Moving on to the next subject.")
            pass

