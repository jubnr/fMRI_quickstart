#!usr/bin/env python
# coding: UTF-8

import os
import numpy as np
import pandas as pd
import json


if __name__ == "__main__":
    SUBJECT_NUMBER = int(input("Participant number: "))

    bids_dir = '/specify/your/path/BidsDataset'
    sub_dir = f'sub-{SUBJECT_NUMBER:02}'
    prefix = f'sub-{SUBJECT_NUMBER:02}'


    # Specify the path to your JSON file
    for run_number in list(range(1, 9)): # put back 9
            fileNameFmapAP = os.path.join(
                bids_dir,
                sub_dir,
                'fmap',
                f'{prefix}_acq-lpp_dir-ap_run-{run_number:02}_epi')

            fileNameFuncSbrefAP = os.path.join(
                bids_dir,
                sub_dir,
                'func',
                f'{prefix}_task-lpp_dir-ap_run-{run_number:02}_sbref')

            # Copy file
            os.system(f'cp {fileNameFuncSbrefAP}.nii.gz {fileNameFmapAP}.nii.gz')
            os.system(f'cp {fileNameFuncSbrefAP}.json {fileNameFmapAP}.json')

            shortFileNameFunc = os.path.join(
                'func',
                f'{prefix}_task-lpp_dir-ap_run-{run_number:02}_bold' )
            shortFileNameSbref = os.path.join(
                'func',
                f'{prefix}_task-lpp_dir-ap_run-{run_number:02}_sbref' )

            # Update fmap AP json
            fileNameFmapAP = os.path.join(
                bids_dir,
                sub_dir,
                'fmap',
                f'{prefix}_acq-lpp_dir-ap_run-{run_number:02}_epi')

            descriptionFmapAP = dict()
            with open(f'{fileNameFmapAP}.json', 'r') as f:
                descriptionFmapAP = json.load(f)

            descriptionFmapAP['B0FieldIdentifier'] = f'pepolar_lpp_{run_number:02}'
            descriptionFmapAP['IntendedFor'] = [
                f'{shortFileNameFunc}.nii.gz',
                f'{shortFileNameSbref}.nii.gz']

            with open(f'{fileNameFmapAP}.json', 'w') as f:
                json.dump(descriptionFmapAP,f, indent=2)

            # Update fmap PA json
            fileNameFmapPA = os.path.join(
                bids_dir,
                sub_dir,
                'fmap',
                f'{prefix}_acq-lpp_dir-pa_run-{run_number:02}_epi')
            
            descriptionFmapPA = dict()
            with open(f'{fileNameFmapPA}.json', 'r') as f:
                descriptionFmapPA = json.load(f)

            descriptionFmapPA['B0FieldIdentifier'] = f'pepolar_lpp_{run_number:02}'
            descriptionFmapPA['IntendedFor'] = [
                f'{shortFileNameFunc}.nii.gz',
                f'{shortFileNameSbref}.nii.gz']

            with open(f'{fileNameFmapPA}.json', 'w') as f:
                json.dump(descriptionFmapPA,f, indent=2)


    # Specify the path to your JSON file
    task = 'localizer'

    fileNameFmapAP = os.path.join(
            bids_dir,
            sub_dir,
            'fmap',
            f'{prefix}_acq-{task}_dir-ap_epi')

    fileNameFuncSbrefAP = os.path.join(
            bids_dir,
            sub_dir,
            'func',
            f'{prefix}_task-{task}_dir-ap_sbref')

    # Copy file
    os.system(f'cp {fileNameFuncSbrefAP}.nii.gz {fileNameFmapAP}.nii.gz')
    os.system(f'cp {fileNameFuncSbrefAP}.json {fileNameFmapAP}.json')

    shortFileNameFunc = os.path.join(
            'func',
            f'{prefix}_task-{task}_dir-ap_bold' )
    shortFileNameSbref = os.path.join(
            'func',
            f'{prefix}_task-{task}_dir-ap_sbref' )

            # Update fmap AP json
    fileNameFmapAP = os.path.join(
            bids_dir,
            sub_dir,
            'fmap',
            f'{prefix}_acq-{task}_dir-ap_epi')

    descriptionFmapAP = dict()
    with open(f'{fileNameFmapAP}.json', 'r') as f:
            descriptionFmapAP = json.load(f)

    descriptionFmapAP['B0FieldIdentifier'] = f'pepolar_{task}'
    descriptionFmapAP['IntendedFor'] = [
            f'{shortFileNameFunc}.nii.gz',
            f'{shortFileNameSbref}.nii.gz']

    with open(f'{fileNameFmapAP}.json', 'w') as f:
            json.dump(descriptionFmapAP,f, indent=2)

    # Update fmap PA json
    fileNameFmapPA = os.path.join(
            bids_dir,
            sub_dir,
            'fmap',
            f'{prefix}_acq-{task}_dir-pa_epi')
            
    descriptionFmapPA = dict()
    with open(f'{fileNameFmapPA}.json', 'r') as f:
            descriptionFmapPA = json.load(f)

    descriptionFmapPA['B0FieldIdentifier'] = f'pepolar_{task}'
    descriptionFmapPA['IntendedFor'] = [
            f'{shortFileNameFunc}.nii.gz',
            f'{shortFileNameSbref}.nii.gz']

    with open(f'{fileNameFmapPA}.json', 'w') as f:
            json.dump(descriptionFmapPA,f, indent=2)
