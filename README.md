# fMRI-Quickstart

This repository provides a streamlined starting point for fast fMRI analyses and preprocessing workflows. Initially designed for rapid GLM-based analyses, this project will progressively integrate more advanced modeling and preprocessing strategies.

## 🔍 Overview

This project includes:
- Step-by-step guide to create a valid BIDS dataset structure 
- A minimal working setup for first-level GLM analysis on fMRI 7T data (simple localizer task)
- Integration with [DeepPrep](https://github.com/pBFSLab/DeepPrep) for automated preprocessing (faster and way more accurate than fMRIprep for 7T data)
- Modular scripts that can be expanded or replaced as the project scales

## 📁 Project Structure

```
.
├── fmri_preprocessing
│   ├── 01-prepareNSpinToBids.py
│   ├── 02-denoiseAnat.py
│   ├── 03-changeHeader.py
│   ├── 04-prep4fMRIprep.py
│   ├── 05-RunfMRIprep.sh
│   └── README.md
├── glm_first_model
│   └── localizer_analysis_tuto.ipynb
├── README.md
└── run_deepprep.sh
```

## 🧠 Goals

- Enable reproducible and scalable fMRI 7T workflows
- Provide a clear entry point for beginners with BIDS + GLM
- Serve as a base to build more complex pipelines over time (e.g., MVPA, RSA, connectivity)

## 🚀 Getting Started

1. Prepare your dataset in BIDS format (see `/fmri_preprocessing`)
2. Run the preprocessing pipeline using DeepPrep (`. run_deepprep.sh`)
3. Launch your GLM analysis (`/glm_analysis/localizer_analysis_tuto.ipynb`)

## 📦 Requirements

- Python 3.8+
- `nibabel`, `nilearn`, `pandas`, `deepprep`, `bids-validator`, etc.
(See `requirements.txt` for the full list)

---

This repo is under active development and will evolve over time. Contributions and feedback are welcome!
