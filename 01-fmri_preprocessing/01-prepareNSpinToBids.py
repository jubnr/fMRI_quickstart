#!usr/bin/env python
# coding: UTF-8

import os
import numpy as np
import pandas as pd
import json

if __name__ == "__main__":

    SUBJECT_NUMBER = "{:02}".format(int(input("Participant number: ")))
    NIP = input("Participant NIP: ")
    session_label = ""
    partAge = input("Participant age: ")
    partGender = input("Participant gender (M/F): ")
    infos_participant = json.dumps({"sex": partGender, "age": int(partAge)})
    acq_date = input("Acquisition date (yyyy-mm-dd): ")
    location = "7t"

    os.chdir(f"/specify/your/path/") #/neurospin/unicog/protocols/IRMf/


    # set the run ids
    ANAT_ID = 36 # Check everytime for inv2, t1 and uni
    LOCA_ID = 35 # Actual func run / -1 for SBRef and -3 for fmap PA SBRef
    LPP_IDs = [21, 25, 29, 39, 43, 47, 51] # Actual func run / -1 for SBRef and -3 for fmap PA SBRef

    to_import = []

    # anat
    inv1 = (ANAT_ID, "anat", "inv1")
    inv2 = (ANAT_ID + 2, "anat", "inv2")
    t1 = (ANAT_ID + 4, "anat", "t1")
    uni = (ANAT_ID + 6, "anat", "uni")

    to_import.append(inv1)
    to_import.append(inv2)
    to_import.append(t1)
    to_import.append(uni)


    # localizer
    loca = (LOCA_ID, "func", "task-localizer_dir-ap_bold")
    sbref = (LOCA_ID - 1, "func", "task-localizer_dir-ap_sbref")
    fmap_pa = (LOCA_ID - 3, "fmap", "acq-localizer_dir-pa_epi")

    to_import.append(loca)
    to_import.append(sbref)
    to_import.append(fmap_pa)


    # LPP
    for i, run_id in enumerate(LPP_IDs):
        i += 1
        run = (run_id, "func", f"task-lpp_dir-ap_run-{i:02}_bold")
        sbref = (run_id - 1, "func", f"task-lpp_dir-ap_run-{i:02}_sbref")
        fmap_pa = (run_id - 3, "fmap", f"acq-lpp_dir-pa_run-{i:02}_epi")

        to_import.append(run)
        to_import.append(sbref)
        to_import.append(fmap_pa)
    
    # save data
    participant_dict = {
        'participant_id': f"sub-{SUBJECT_NUMBER}",
        'NIP': NIP,
        'infos_participant': infos_participant,
        'session_label': session_label,
        'acq_date': acq_date,
        'acq_label':'',
        'location': location,
        'to_import': to_import
    }

    if not os.path.exists('exp_info'):
        os.mkdir('exp_info')

    if not os.path.exists('BidsDataset'):
        os.mkdir('BidsDataset')

    participants_to_import = pd.DataFrame([participant_dict])
    participants_to_import.to_csv(f"exp_info/participants_to_import.tsv", sep="\t", index=False)

    print("now run: neurospin_to_bids --dataset-name BidsDataset")