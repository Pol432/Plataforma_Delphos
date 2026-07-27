# DELPHOS

**Career recommendation engine** — predicts whether a user will engage with a
job recommendation using a Wide&Deep neural network trained with MindSpore.

Built over 3 weeks as a structured deep learning project, covering data
sourcing, exploratory analysis, feature engineering, model training, and
evaluation.

| | |
|---|---|
| **Model** | Wide&Deep (Huawei / MindSpore) |
| **Task** | Binary engagement classification |
| **Best AUC-ROC** | 0.7763 |
| **Training set** | 18,501 labelled interactions |
| **Framework** | MindSpore 2.8.0+ · Python 3.10 · Ubuntu 22.04 |

→ For model architecture, inputs/outputs, and inference code see
[`notebooks/Week 3 - Model Training/README.md`](notebooks/Week%203%20-%20Model%20Training/README.md)

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Getting Started](#2-getting-started)
3. [Repository Structure](#3-repository-structure)
4. [Notebook Execution Order](#4-notebook-execution-order)
5. [Data](#5-data)
6. [Checkpoints](#6-checkpoints)
7. [Development Notes](#7-development-notes)

---

## 1. Prerequisites

**Required on the host machine:**

- [Docker Engine 24+](https://docs.docker.com/engine/install/)
- 10 GB free disk space (container image + workspace)
- *Optional:* NVIDIA GPU + [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
  for GPU-accelerated training

**No Python installation needed on the host.** Everything runs inside the
container.

---

## 2. Getting Started

### 2.1 Clone the repository

```bash
git clone https://github.com/Pol432/Wide-Deep-Career-Recommendation-System.git
cd delphos
```

### 2.2 Download the raw datasets

The raw Kaggle datasets are not included in the repository. Download them
before initialising the container:

```bash
# Requires a Kaggle API token at ~/.kaggle/kaggle.json
bash scripts/01_download_datasets.sh
```

This populates `data/raw/` with the source CSV files used in Week 2.

### 2.3 Initialise and enter the container

```bash
# Create the container for the first time
bash initialize-container

# On subsequent sessions — start and enter
docker start dao-recommender
bash enter-container.sh
```

> **Note:** `initialize-container` only needs to be run once. It creates the
> `dao-recommender` Docker container and mounts this directory as `/workspace`
> inside it. After that, use `docker start` / `docker stop` to manage the
> container lifecycle.

### 2.4 Start Jupyter Lab

Once inside the container:

```bash
bash start_services.sh   # starts Jupyter Lab on port 8888
bash get_token.sh        # prints the access token
```

Open `http://localhost:8888` in your browser and paste the token.

### 2.5 Stop everything

```bash
# Inside container
bash stop_services.sh    # stop Jupyter

# On host
docker stop dao-recommender
```

---

## 3. Repository Structure

```
delphos/
│
├── initialize-container       ← Run once to create the Docker container
├── enter-container.sh         ← Open a shell inside the running container
├── start_services.sh          ← Start Jupyter Lab (run inside container)
├── stop_services.sh           ← Stop Jupyter Lab
├── stop-container.sh          ← Stop the container from the host
├── setup_env.sh               ← Install/verify Python dependencies
├── get_token.sh               ← Print Jupyter access token
├── status.sh                  ← Show container and service status
├── quick_test.sh              ← Smoke-test MindSpore installation
├── QUICK_REFERENCE.md         ← All commands on one page
│
├── notebooks/
│   ├── Week 1 - Mindspore Setup/      ← Environment + architecture study
│   ├── Week 2 - Dataset Selection/    ← EDA, unification, MindRecord conversion
│   └── Week 3 - Model Training/
│       ├── 01_pre_training_validation.ipynb
│       ├── 02_model_build_and_train.ipynb
│       └── README.md                  ← Model architecture, inference guide
│
├── data/
│   ├── raw/                   ← Kaggle source files (not in repo — see §5)
│   ├── processed/             ← Cleaned CSVs, label encoders, skill vectors
│   ├── mindrecord/            ← MindSpore binary format (not in repo — see §5)
│   ├── eda_outputs/           ← Summary tables from Week 2 EDA
│   └── visualizations/        ← Charts from EDA and preprocessing steps
│
├── checkpoints/
│   ├── baseline/
│   │   └── dao_wide_deep_best.ckpt    ← Best checkpoint (epoch ~828)
│   ├── dao_wide_deep_final.ckpt       ← Final epoch checkpoint
│   ├── evaluation_results.json        ← Test-set metrics
│   └── training_config.json           ← Full hyperparameter snapshot
│
├── logs/
│   ├── training_history_baseline.csv  ← Per-epoch loss and AUC (980 epochs)
│   ├── training_curves_baseline_final.png
│   └── evaluation_charts_baseline.png
│
├── src/
│   └── wide_and_deep.py               ← Vendored model source (see §7)
│
└── scripts/
    └── 01_download_datasets.sh        ← Kaggle dataset downloader
```

**Not included in this repository** (see §5 and §7):
- `data/raw/` — raw Kaggle CSV files
- `data/mindrecord/*.mindrecord` — derived binary, regenerate from processed data
- `mindspore/` — MindSpore framework source (install via pip)

---

## 4. Notebook Execution Order

Run notebooks in this order on a fresh setup. Each week builds on the outputs
of the previous one.

### Week 1 — Environment & Architecture Study

Familiarisation with MindSpore. No data dependencies. Can be run in any order.

```
00_environment_test.ipynb   ← Verify MindSpore installation and GPU access
01_documentation_study.ipynb
02_model_explained.ipynb
03_preprocessing_explained.ipynb
04_exercises.ipynb
05_mindspore_basics.ipynb
```

### Week 2 — Dataset Selection & Preprocessing

**Requires:** raw data in `data/raw/` (run `scripts/01_download_datasets.sh` first)

```
01_initial_eda.ipynb                         ← First look at each dataset
01_linkedin_eda.ipynb                        ← LinkedIn-specific analysis
02_comprehensive_eda_complete.ipynb          ← Full EDA across all sources
03_data_unification.ipynb                   ← Merge sources → unified_training_dataset_v3.csv
                                              Produces: data/processed/label_encoders.pkl
                                                        data/processed/skills_catalog.csv
                                                        data/processed/user_skill_vectors.npy
01_data_transformation_unified_dataset.ipynb ← Feature engineering pass
04_mindrecord_conversion.ipynb              ← Convert CSV → MindRecord binary
                                              Produces: data/mindrecord/widedeep_training.mindrecord
```

### Week 3 — Model Training & Evaluation

**Requires:** `data/mindrecord/widedeep_training.mindrecord` and
`data/processed/label_encoders.pkl`

```
01_pre_training_validation.ipynb   ← Sanity checks before training
                                     (shapes, class balance, vocab sizes)

02_model_build_and_train.ipynb     ← Full training pipeline
                                     Produces: checkpoints/baseline/dao_wide_deep_best.ckpt
                                               logs/training_history_baseline.csv
                                               checkpoints/evaluation_results.json
```

---

## 5. Data

### Source datasets

| Dataset | Source | License |
|---|---|---|
| LinkedIn job postings | Kaggle | See Kaggle dataset page |
| Salary survey | Kaggle | See Kaggle dataset page |
| AI career dataset | Kaggle (`ai_career.csv`) | See Kaggle dataset page |
| Career paths | Kaggle (`career_paths.csv`) | See Kaggle dataset page |

Raw files are **not committed** to this repository. Use
`scripts/01_download_datasets.sh` to download them. A valid Kaggle API token
(`~/.kaggle/kaggle.json`) is required.

### Processed files (included in repo)

| File | Description |
|---|---|
| `data/processed/unified_training_dataset_v3.csv` | 18,501 merged, cleaned interaction records |
| `data/processed/label_encoders.pkl` | Fitted LabelEncoders + vocab offsets (required for inference) |
| `data/processed/skills_catalog.csv` | Canonical 52-skill vocabulary |
| `data/processed/user_skill_vectors.npy` | Pre-computed user skill multi-hot arrays |
| `data/processed/simulation_skill_vectors.npy` | Pre-computed job skill multi-hot arrays |
| `data/processed/dataset_metadata.json` | Field sizes, vocab sizes, class counts |

### Regenerating the MindRecord binary

The `.mindrecord` file is a large derived binary and is not committed. To
regenerate it from the processed CSV, run
`notebooks/Week 2 - Dataset Selection/04_mindrecord_conversion.ipynb`.

---

## 6. Checkpoints

| File | Description |
|---|---|
| `checkpoints/baseline/dao_wide_deep_best.ckpt` | **Use this for inference.** Best test-set AUC across all epochs (~ep 828). |
| `checkpoints/dao_wide_deep_final.ckpt` | Final epoch checkpoint. Slightly lower AUC due to late oscillation. |
| `checkpoints/training_config.json` | Complete hyperparameter snapshot. Load this to recreate the exact training config. |
| `checkpoints/evaluation_results.json` | AUC-ROC, F1, accuracy, confusion matrix on the 3,701-sample test set. |

For detailed instructions on loading a checkpoint and running inference, see
[`notebooks/Week 3 - Model Training/README.md`](notebooks/Week%203%20-%20Model%20Training/README.md).

---

## 7. Development Notes

### Container scripts

| Script | Where to run | Purpose |
|---|---|---|
| `initialize-container` | Host | **Run once.** Creates the `dao-recommender` container. |
| `enter-container.sh` | Host | Open a bash shell inside the running container. |
| `stop-container.sh` | Host | Stop the container. |
| `start_services.sh` | Inside container | Start Jupyter Lab. |
| `stop_services.sh` | Inside container | Stop Jupyter Lab. |
| `setup_env.sh` | Inside container | Install/verify Python packages. |
| `status.sh` | Inside container | Show running processes and disk usage. |

> All git operations should be run **on the host machine**, not inside the
> container. Git credentials live on the host, and the workspace is fully
> accessible at `~/dao-wide-deep/` without entering the container.

### Vendored model source — `src/wide_and_deep.py`

`src/wide_and_deep.py` is a verbatim copy of the Wide&Deep model source from
`mindspore-ai/models`, vendored directly into this repository. It is **not
modified** — the attribution header at the top of the file records the exact
upstream commit hash it was taken from.

It is vendored rather than imported from a live clone for one reason:
**reproducibility**. The checkpoint in `checkpoints/baseline/` was trained
against a specific version of that file. If Huawei updates the upstream model
(changed layer names, removed ops, altered the constructor signature), a fresh
clone would silently break checkpoint loading. The vendored copy pins the exact
version that works.

To import it in your own code:

```python
# From /workspace (container root) or repo root on host
from src.wide_and_deep import WideDeepModel
```

No `sys.path` manipulation needed — `src/` sits at the root of the workspace,
which is the default Python working directory inside the container.

**License:** Apache 2.0 —
`https://github.com/mindspore-ai/models/blob/master/LICENSE`

### MindSpore framework

Install via pip inside the container. No source clone needed:

```bash
pip install mindspore==2.8.0
```

### Python environment

All dependencies run inside the container. Key packages:

```
mindspore    2.8.0
numpy        1.24.3
pandas       2.0.3
scikit-learn 1.3.0
jupyterlab   4.0.5
kaggle       1.5.16
```

---

*DELPHOS — internal project — last updated February 2026*
