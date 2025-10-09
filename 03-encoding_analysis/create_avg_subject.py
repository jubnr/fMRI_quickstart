#! /usr/bin/env python3

""" Averaging MRI bold files """
""" applied to the LPP english data set (see main) """

import os
import glob
import nibabel as nib
import numpy as np
from typing import List
from pathlib import Path

BASE_PATH = Path("/neurospin/unicog/protocols/IRMf/LePetitPrince_Pallier_2018/MEG/workspace-LPP/data/MEG/LPP/LPP_IRMEG_visual/derivatives/preprocessed_data/")

def average_4d_fmri_files(file_list: List[str], output_filename: str):
    """
    Reads a list of 4D fMRI NIfTI files, averages them, and saves the result.

    The function averages the images voxel by voxel across all files,
    preserving the time dimension (the 4th dimension). All input files
    must have the same dimensions and affine transformation.

    Args:
        file_list (List[str]): A list of file paths to the 4D fMRI files.
        output_filename (str): The path where the averaged fMRI image will be saved.

    Raises:
        ValueError: If the file list is empty or if the dimensions/affines
                    of the input images do not match.
    """
    if not file_list:
        raise ValueError("Input file list cannot be empty.")

    print(f"Found {len(file_list)} files to average.")

    # --- Load the first image to use as a reference ---
    try:
        first_img = nib.load(file_list[0])
        print(f"Using '{os.path.basename(file_list[0])}' as the reference image.")
    except FileNotFoundError:
        print(f"Error: The first file '{file_list[0]}' was not found.")
        return

    # Get the shape and affine transformation from the first image
    ref_shape = first_img.shape
    ref_affine = first_img.affine
    ref_header = first_img.header

    # Ensure it's a 4D file
    if len(ref_shape) != 4:
        raise ValueError(f"The reference image '{os.path.basename(file_list[0])}' is not 4D. Shape: {ref_shape}")

    # --- Initialize an array to accumulate the data ---
    # Use a float data type to avoid precision issues during summation
    sum_data = np.zeros(ref_shape, dtype=np.float64)

    # --- Loop through all files, validate, and accumulate data ---
    for i, file_path in enumerate(file_list):
        try:
            print(f"Processing file {i+1}/{len(file_list)}: '{os.path.basename(file_path)}'")
            img = nib.load(file_path)
            
            # --- Validation Step ---
            # Check if dimensions and affine match the reference
            if img.shape != ref_shape:
                raise ValueError(
                    f"Dimension mismatch in '{os.path.basename(file_path)}'. "
                    f"Expected {ref_shape}, but got {img.shape}."
                )
            if not np.allclose(img.affine, ref_affine):
                 raise ValueError(
                    f"Affine mismatch in '{os.path.basename(file_path)}'. "
                    f"Please ensure all files are in the same space."
                )

            # Add the image data to the sum array
            # .get_fdata() is used to load data as floating point numbers
            sum_data += img.get_fdata()

        except FileNotFoundError:
            print(f"Warning: File not found, skipping: {file_path}")
            continue
        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")
            return # Stop execution on error

    # --- Calculate the average ---
    num_files = len(file_list)
    if num_files > 0:
        average_data = sum_data / num_files
        print("\nAveraging complete.")
    else:
        print("No files were processed.")
        return

    # --- Save the resulting image ---
    # Create a new NIfTI image object from the averaged data
    # Use the reference affine and header to maintain spatial information
    averaged_img = nib.Nifti1Image(average_data.astype(np.float32), ref_affine, ref_header)

    # Save the image to the specified output file
    try:
        nib.save(averaged_img, output_filename)
        print(f"Successfully saved the averaged image to: '{output_filename}'")
    except Exception as e:
        print(f"Failed to save the output file. Error: {e}")


if __name__ == '__main__':
    output_directory = Path("/home_local/Bonnaire/scripts/source_reconstruction/irmeg/avg/")
    output_directory.mkdir(parents=True, exist_ok=True) 

    for run_num in range(1, 8):
        run_str = f"run-{run_num:02d}" 
        
        fmri_pattern = str(BASE_PATH / '*' / 'fmri/func' / f'*{run_str}*MNI*preproc_bold.nii.gz')
        
        scans_for_this_run = sorted(glob.glob(fmri_pattern))

        print(f"\n--- Processing {run_str} ---")
        print(f"Found {len(scans_for_this_run)} scans for {run_str}.")

        target_filename = output_directory / f"lpp_avg7ss_{run_str}_bold.nii.gz"

        average_4d_fmri_files(scans_for_this_run, str(target_filename))

    print("\n--- All runs processed. ---")
