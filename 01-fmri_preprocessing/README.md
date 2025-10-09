# Todo-list for preprocessing 7T images

1. Check that the phases are saved *after* the amplitudes, and otherwise, adapt lines 23-28 in `01-prepareNSpinToBids.py`, ***make sure to check the order of INV1, INV2, T1 and UNI for the anatomy!***
2. Prepare data for BIDS import: *adapt the runs if needed* and run `python 01-prepareNSpinToBids.py`
3. Import data from server to BIDS format: run `neurospin_to_bids --dataset-name MRI/BidsDataset` in the `data` folder **on nautilus**, answer "n" to all questions.
4. Once imported, denoise the anatomical maps + change the headers: run `python 02-denoiseAnat.py sub-01_uni.nii.gz sub-01_inv1.nii.gz sub-01_inv2.nii.gz sub-01_T1w.nii.gz 10` and `python 03-changeHeader.py`
5. Make sure fMRIprep takes the right distortion correction file for each run: *adapt the runs if needed* and run `python 04-prep4fMRIprep.py`
6. Start fMRIprep: run `./05-RunfMRIprep.sh [SUB_NO]` in a tmux session **on nautilus**, where `SUB_NO` is in the format `01`, `02`, ... (e.g., `. 05-RunfMRIprep.sh 01` if sub-01).