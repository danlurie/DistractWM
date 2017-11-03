import os
import traceback
import numpy as np
import pandas as pd
import nibabel as nib
from glob import glob
from nilearn import input_data

# Define hard-coded input/output parameters and file path templates.
SUBJECT_LIST_FILE = '/home/despoB/DistractWM/code/fmriprep/sge/subject_list.txt'
FUNC_FILE_GLOB_FPT = '/home/despoB/DistractWM/data/derivatives/fmriprep/out/fmriprep/sub-{0}/func/sub-{0}_task-*_bold_space-MNI152NLin2009cAsym_preproc.nii.gz'
BNA_FILE = '/home/despoB/dlurie/Data/reference/Brainnetome/BNA-maxprob-thr25-1mm.nii.gz' 
DERIVATIVES_OUT_DIR = '/home/despoB/DistractWM/data/derivatives/custom'

# Load the subject list.
subject_list = np.loadtxt(SUBJECT_LIST_FILE, dtype='int')
subject_list = [str(i) for i in subject_list]

# Loop through subjects.
for sub_id in subject_list:
    try:
        print("Subject {0}...".format(sub_id))
        
        # Get a list of all preprocessed functional files.
        func_files = glob(FUNC_FILE_GLOB_FPT.format(sub_id))

        # If the subject custom derivatives /func directory doesn't exist, raise an error.
        subject_out_dir = os.path.join(DERIVATIVES_OUT_DIR, 'sub-{0}'.format(sub_id), 'func')
        assert (os.path.isdir(subject_out_dir)),"No ../func/custom derivatives directory found!"
  
        # Loop through functional files.
        for bold_mni_preproc in func_files:
            print("Scan: "+os.path.basename(bold_mni_preproc))
            # Set the paths to input files.
            bold_mni_mask = bold_mni_preproc.rstrip('preproc.nii.gz')+'brainmask.nii.gz'
            assert (os.path.exists(bold_mni_mask)),"Brain mask file does not exist!"
            confounds_tsv = bold_mni_preproc.rstrip('space-MNI152NLin2009cAsym_preproc.nii.gz')+'_confounds.tsv'
            assert (os.path.exists(confounds_tsv)),"Confounds file does not exist!"
            motion_tsv = os.path.join(subject_out_dir, os.path.basename(confounds_tsv).rstrip('confounds.tsv')+'motion.tsv')
            assert (os.path.exists(motion_tsv)),"Motion parameters file does not exist!"

            # Read in confounds and motion parameters
            confounds = pd.read_csv(confounds_tsv, sep='\t', usecols=[
                'aCompCor00', 'aCompCor01', 'aCompCor02', 'aCompCor03', 'aCompCor04', 'aCompCor05'])
            motion = pd.read_csv(motion_tsv)

            # Join confounds and motion parameters to form our nuisance regressors.
            nuisance = pd.concat([confounds, motion], axis=1)
            nuisance = nuisance.as_matrix()

            # Load Brainnetome atlas
            bna_img = nib.load(BNA_FILE)

            # Load brain mask
            bold_mni_mask_img = nib.load(bold_mni_mask)

            # Set up the Brainnetome Labels Masker
            bna_masker = input_data.NiftiLabelsMasker(labels_img=bna_img, background_label=0, mask_img=bold_mni_mask_img,
                                                      standardize=True,  detrend=True, low_pass=0.1, high_pass=0.01, t_r=2,
                                                      resampling_target="data")

            # Extract and save ROI timeseries
            print("...extracting Brainnetome timeseries...")
            timeseries = bna_masker.fit_transform(bold_mni_preproc, nuisance)
            ts_out_fname = os.path.basename(bold_mni_preproc).rstrip('preproc.nii.gz')+'atlas-BNA_variant-Motion24CompCor_timeseries.npy'
            np.save(os.path.join(subject_out_dir, ts_out_fname), timeseries)
        
            # Compute and save correlation matrix
            print("...computing correlation matrix...")
            corrmat = np.corrcoef(timeseries.T)
            corrmat_out_fname = os.path.basename(bold_mni_preproc).rstrip('preproc.nii.gz')+'atlas-BNA_variant-Motion24CompCor_corrmat.npy'
            np.save(os.path.join(subject_out_dir, corrmat_out_fname), corrmat)

            print("...Done!")

    except:
        print("Something went wrong!")
        traceback.print_exc()
        print("Moving on to the next subject.")
        pass

