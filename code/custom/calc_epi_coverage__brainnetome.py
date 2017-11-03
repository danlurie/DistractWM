import os
import traceback
import numpy as np
import pandas as pd
import nibabel as nib
from glob import glob
from nilearn import image

# Define a function to calculate mask-atlas overlap.
def epi_atlas_coverage(brain_mask, atlas):
    atlas_img = nib.load(atlas)
    mask_img = nib.load(brain_mask)
    atlas_resample = image.resample_to_img(atlas_img, mask_img, interpolation='nearest')
    mask_data = mask_img.get_data()
    atlas_data = atlas_resample.get_data()
    coverage_data = mask_data*atlas_data
    roi_labels = np.unique(atlas_data)
    
    roi_sizes = []
    for roi in roi_labels:
        roi_sizes.append(np.count_nonzero(atlas_data == roi))
    
    roi_coverage = []
    for roi in roi_labels:
        roi_coverage.append(np.count_nonzero(coverage_data == roi))
    
    df = pd.DataFrame.from_records(np.array([roi_sizes, roi_coverage]).T, columns=['roi_size', 'roi_count'])
    df = df.set_index(roi_labels.astype('uint8')) 
    df.loc[:,'pct_cov'] = df['roi_count']/df['roi_size']*100
    df.index.name = 'roi_label'
    return df

# Define hard-coded input/output parameters and file path templates.
SUBJECT_LIST_FILE = '/home/despoB/DistractWM/code/fmriprep/sge/subject_list.txt'
MASK_FILE_GLOB_FPT = '/home/despoB/DistractWM/data/derivatives/fmriprep/out/fmriprep/sub-{0}/func/sub-{0}_task-*_bold_space-MNI152NLin2009cAsym_brainmask.nii.gz'
BNA_FILE = '/home/despoB/dlurie/Data/reference/Brainnetome/BNA-maxprob-thr25-1mm.nii.gz'
assert (os.path.exists(BNA_FILE)),"Brainnetome atlas file does not exist!"
DERIVATIVES_OUT_DIR = '/home/despoB/DistractWM/data/derivatives/custom'

# Load the subject list.
subject_list = np.loadtxt(SUBJECT_LIST_FILE, dtype='int')
subject_list = [str(i) for i in subject_list]

# Loop through subjects.
for sub_id in subject_list:
    try:
        print("Subject {0}...".format(sub_id))
        
        # Get a list of all brain masks.
        mask_files = glob(MASK_FILE_GLOB_FPT.format(sub_id))

        # If the subject custom derivatives /func directory doesn't exist, raise an error.
        subject_out_dir = os.path.join(DERIVATIVES_OUT_DIR, 'sub-{0}'.format(sub_id), 'func')
        assert (os.path.isdir(subject_out_dir)),"No ../func/custom derivatives directory found!"
  
        # Loop through brain masks.
        for bold_mni_mask in mask_files:
            print("Mask: "+os.path.basename(bold_mni_mask))
            # Calculate overlaps.
            print('...calculating EPI mask coverage...')
            df = epi_atlas_coverage(bold_mni_mask, BNA_FILE)
            # Save the coverage data.
            print('...saving coverage data...')
            df_out_fname = os.path.basename(bold_mni_mask).rstrip('brainmask.nii.gz')+'atlas-BNA_EPIcoverage.csv'
            out_path = os.path.join(subject_out_dir, df_out_fname)
            df.to_csv(out_path)
            
            print('...Done!')

    except:
        print("Something went wrong!")
        traceback.print_exc()
        print("Moving on to the next subject.")
        pass
