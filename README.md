# Project Title: Code and Data for Naked Mole-Rat Behavioral Study

This repository contains the data processing and analysis code for a manuscript on behavioral study in naked mole-rats. The workflow is divided into two main parts: data preprocessing using Python and statistical analysis and visualization using R. The code is intended to be run in a specific order, starting with Python scripts and followed by R scripts.

---

## Directory Structure

```
.
├── python_scripts/           # Python scripts for data preprocessing (run first)
│   ├── preprocess_1.py
│   ├── preprocess_2.py
│   ├── preprocess_3.py
│   └── preprocess_4.py
├── r_scripts/                # R scripts for analysis and visualization (run second)
│   ├── Figure 1.Rmd
│   ├── Figure 2-3.Rmd
│   ├── Figure 4.Rmd
│   ├── Figure 5.Rmd
│   └── Figure 6.Rmd
├── data/
│   ├── event_data/          # Raw detection data
│   ├── pre_info_data/       # Individual information, observation day, & pre-observation 
│   ├── processed_data/      # Processed data
│   ├── statistical_result/  # statistical results generated by R scripts
│   └── Figure/              # Figures generated by R scripts
├── install_packages.R       # R package installation script
├── LICENSE                
└── README.md              # Project documentation (this file)
```

---

## Overview

- **Python scripts** (in `python_scripts/`) process the raw data and generate output files.
- **R scripts** (in `r_scripts/`) perform statistical analyses and generate figures based on the processed data.

---

## Environment

### Python
- Version: Tested with Python 3.10.12
  - numpy
  - pandas
- Install with:

```bash
pip install numpy pandas

### R
- Version: Tested with R 4.2.3
- Install required packages by running the following in R:

```R
source("install_packages.R")
```

---

## Execution Workflow

1. Run the Python scripts in the `python_scripts/` folder in order.
   - These scripts read raw data from `data/event_data/` and output processed data to `data/processed_data/`.

2. Run the Rmd scripts in the `r_scripts/` folder in order.
   - These scripts read data from `data/pre_info_data/` and `data/processed_data/` and output processed data to `data/processed_data/` folder.
   - Statistical results will be saved in the `data/statistical_result/` folder.
   - Figures will be saved in the `data/Figure/` folder.

---

## Data Organization Note

- The R scripts assume that **all processed data are stored under `data/processed_data/`**, organized first by data type, and then by colony.
- For example, each type of data (e.g., `table_data_with_nan_filled_by_nest/`, `room_def_with_nan/`) has its own subfolder, and within each of these, there should be subfolders for each colony (`2B/`, `2D/`, `HG/`, `HT/`, `LOC/`).

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Contact

For questions or comments, please contact:

**Masanori Yamakawa**
Email: yamakawamanori1008@gmail
