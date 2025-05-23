singularity run --cleanenv --nv \
             -B /your/path/to/your/BidsDataset:/input \
             -B /your/path/to/deepprep_derivatives:/output \
             -B /data/software/fmriprep/fs_license.txt:/fs_license.txt \
             /data/software/deepprep/deepprep_25.1.0.sif \
             /input \
             /output \
             participant \
	         --bold_task_type lpp \
             --fs_license_file /fs_license.txt \
	         --ignore_error \
             --device gpu