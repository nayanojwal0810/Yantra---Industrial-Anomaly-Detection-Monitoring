# FreshRetailNet-50K Task 1 Validation — Run Guide

This guide describes how to execute the Task 1 Data Integrity and Schema Census for the **FreshRetailNet-50K** retail demand dataset.

---

## 1. Prerequisites and Environment Setup

The validation script requires Python 3.10+ with `pandas` and `pyarrow`. No machine learning frameworks or GPU acceleration are required.

To install dependencies using the minimal requirements file:

```bash
pip install -r validation/freshretail/requirements.txt
```

Verified versions in this environment:
- **Python:** 3.13.3
- **pandas:** 3.0.3
- **pyarrow:** 24.0.0

---

## 2. Input Data Placement

The script expects the two raw Parquet files to be placed in `data/raw/`:

- `data/raw/train.parquet`
- `data/raw/eval.parquet`

Official download sources:
- **Hugging Face Hub:** `https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K`
- **Direct Train Parquet:** `https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K/resolve/main/data/train.parquet`
- **Direct Eval Parquet:** `https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K/resolve/main/data/eval.parquet`

*Note: Raw data files in `data/raw/` must never be modified, renamed, or committed to GitHub.*

---

## 3. Execution Commands

From the project root directory (`d:\Aarohan`), run:

```bash
python validation/freshretail/scripts/validate_dataset.py
```

### Optional Command-Line Arguments

The script accepts optional path arguments for custom directories:

| Flag | Default Value | Description |
|:---|:---|:---|
| `--data-dir` | `data/raw` | Path to directory containing `train.parquet` and `eval.parquet` |
| `--output-dir` | `validation/freshretail` | Destination directory for census reports |
| `--log-file` | `validation/freshretail/logs/task1_validation.log` | Destination path for the execution log file |

Example with explicit arguments:

```bash
python validation/freshretail/scripts/validate_dataset.py \
  --data-dir data/raw \
  --output-dir validation/freshretail \
  --log-file validation/freshretail/logs/task1_validation.log
```

---

## 4. Generated Artifacts and Output Files

All validation outputs are written under `validation/freshretail/`:

| File Path | Description |
|:---|:---|
| `validation/freshretail/reports/task1_data_census.md` | Human-readable comprehensive Markdown report detailing file integrity, schema mappings, missingness, entity coverage, numeric distributions, stockout representations, and cross-file consistency. |
| `validation/freshretail/reports/task1_data_census.json` | Complete machine-readable JSON object with all raw statistics, hashes, schema mappings, preview records, and check decisions. |
| `validation/freshretail/logs/task1_validation.log` | Detailed timestamped execution log recording progress, metrics, and process termination code. |

---

## 5. Pass / Fail Evaluation Rules

- **PASS:** Both files exist, are valid Parquet files, schemas match official documentation, zero missing values, zero duplicate grain records, SHA-256 digests match official Hugging Face Git LFS pointers, and cross-file temporal split semantics are valid.
- **CONDITIONAL PASS:** Files are readable and usable, but non-critical schema or format mismatches exist that are thoroughly documented.
- **FAIL:** File corruption, unreadable Parquet, missing essential fields, critical schema mismatches, or invalid provenance.
- **BLOCKED:** One or more expected Parquet files are missing from the input directory.

The script exits with code `0` on **PASS** and **CONDITIONAL PASS**, and nonzero on **FAIL** or **BLOCKED**.
