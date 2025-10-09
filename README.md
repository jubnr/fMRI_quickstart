# fMRI-Quickstart

This repository provides a streamlined starting point for fast fMRI analyses and preprocessing workflows. Initially designed for rapid GLM-based analyses, this project will progressively integrate more advanced modeling and preprocessing strategies.

## 🔍 Overview

This project includes:

- A minimal working setup for first-level GLM analysis on fMRI data
- Step-by-step guide to create a valid BIDS dataset structure
- Integration with [DeepPrep](https://github.com/pBFSLab/DeepPrep) for automated preprocessing
- Modular scripts that can be expanded or replaced as the project scales

## 📁 Project Structure


## 🧠 Goals

- Enable reproducible and scalable fMRI workflows
- Provide a clear entry point for researchers or developers starting with BIDS + GLM
- Serve as a base to build more complex pipelines over time (e.g., MVPA, RSA, connectivity)

## 🚀 Getting Started

1. Prepare your dataset in BIDS format (see `/preprocessing/create_bids_dataset.py`)
2. Run the preprocessing pipeline using DeepPrep (`/preprocessing/run_deepprep.py`)
3. Launch your GLM analysis (`/glm_analysis/run_glm.py`)

## 📦 Requirements

- Python 3.8+
- `nibabel`, `nilearn`, `pandas`, `deepprep`, `bids-validator`, etc.
(See `requirements.txt` for the full list)

---

This repo is under active development and will evolve over time. Contributions and feedback are welcome!
