#!usr/bin/env phython
# coding: UTF-8

import json

SUBJECT_NUMBER = int(input("Subject number: "))

if __name__ == "__main__":
    input_json_path = f"/specify/your/path/BidsDataset/sub-{SUBJECT_NUMBER:02}/anat/sub-{SUBJECT_NUMBER:02}_uni.json"
    output_json_path = f"/specify/your/path/BidsDataset/sub-{SUBJECT_NUMBER:02}/anat/sub-{SUBJECT_NUMBER:02}_T1w.json"

    with open(input_json_path, 'r') as input_file:
        data = json.load(input_file)

    # Modify the desired elements in the Python data structure
    data['SeriesDescription'] = 'mp2rage_iso0.65_iPAT2_angulated_UNI_Images_DEN'
    data['ImageComments'] = 'MP2RAGE Uni Image denoised'

    # Open the output JSON file for writing
    with open(output_json_path, 'w') as output_file:
        json.dump(data, output_file)
