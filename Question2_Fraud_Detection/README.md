# Question 2 — Fraud Detection: Dataset Loading & Processing

**Dataset:** [Fraud Detection — 1M Transactions, 7 Fraud Types](https://www.kaggle.com/datasets/sergionefedov/fraud-detection-1m-transactions-7-fraud-types)
(Kaggle, by Sergio Nefedov).

This answers the assignment cell *"load and process the dataset you are
going to train your models on"* — scikit-learn is used for the processing
pipeline.

## Files

```
fraud_detection_dataset.ipynb   the notebook cell(s): download, load, clean, preprocess
requirements.txt                 packages needed to run it
```

## How to run it

1. Get a Kaggle API token: Kaggle → Account → *Create New Token* → downloads
   `kaggle.json`. Either:
   - place it at `~/.kaggle/kaggle.json` (local Jupyter), or
   - in Colab, add `KAGGLE_USERNAME` / `KAGGLE_KEY` as Colab secrets, or
     upload `kaggle.json` and run `os.environ["KAGGLE_CONFIG_DIR"] = "."`.
2. `pip install -r requirements.txt`
3. Run the notebook top to bottom.

The first code cell calls `kagglehub.dataset_download(...)`, which pulls
the dataset straight from Kaggle and caches it locally — no manual zip
download/extract needed.

## Why the processing step is schema-agnostic

I don't have network access to Kaggle from this sandbox, so the notebook
was written and reviewed without being able to open the actual CSV and
confirm exact column names. Rather than guess a column list that might be
wrong, the notebook:

- prints `df.info()` / `df.head()` right after loading so you can see the
  real columns before anything else runs,
- auto-detects the fraud label by matching column names containing
  `fraud`/`class`/`label`, preferring the low-cardinality one (the binary
  `is_fraud` flag, as opposed to a free-text `fraud_type` column),
- auto-splits the remaining columns into numeric vs. categorical via
  pandas dtypes rather than hardcoded names,
- drops obvious identifier columns (`transaction_id`, `card_number`, ...)
  by a name-pattern match.

**After running the first "explore" cell, check the printed column list
and the auto-detected target column** — adjust the `id_like` pattern list
or `target_col` selection in the next cell if the real schema doesn't
match what was guessed (e.g. if the fraud-type column is called something
else, or extra ID-like columns should be dropped).

## What the pipeline does

- `train_test_split(..., stratify=y)` — fraud is a rare class, so
  stratifying keeps the same fraud ratio in train and test.
- `ColumnTransformer` with two branches:
  - numeric: median imputation → `StandardScaler`
  - categorical: most-frequent imputation → `OneHotEncoder(handle_unknown="ignore")`
- Fit on train only, then `transform` (not `fit_transform`) on test, to
  avoid leaking test statistics into scaling/encoding.

Class imbalance itself (e.g. resampling with `imbalanced-learn`'s SMOTE,
or `class_weight="balanced"` in the model) is a modeling-stage decision,
left for the "train models" cell — this cell only prepares clean,
model-ready `X`/`y`.
