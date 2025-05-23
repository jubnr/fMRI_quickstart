export FMRIPREP=/neurospin/unicog/resources/softwares/FMRIPREP/fmriprep-23.2.1.simg
export PROJECT=/specify/path/to/your/project
export FREESURFER=$FREESURFER_HOME
export SOURCE=BidsDataset
export DEST=fMRIprep
export MINC_TOOL_DIR=/drf/local/freesurfer/mni/bin/mincreshape

for subId in "$@"
do
    singularity run --cleanenv \
                -B "${PROJECT}:/data" \
                -B "${FREESURFER}:/freesurfer" \
                ${FMRIPREP} \
                "/data/${SOURCE}" \
                "/data/$DEST" \
                participant \
                    --participant-label $subId \
                    --output-spaces T1w MNI152NLin2009cAsym \
                    --bold2t1w-init header \ # boldtoanat now
                    --bold2t1w-dof 9 \
                    --fs-license-file "/freesurfer/license.txt" \
                    -w "/data/${DEST}/work_dir" \
                    --skip-bids-validation \ # let the bids validator do its job 
                    --clean-workdir
done