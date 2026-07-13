# Question 2 — Diabetes Dataset Overview

## Name and source

**Diabetes dataset** — one of scikit-learn's built-in "toy" datasets,
loaded via `sklearn.datasets.load_diabetes()`.

- scikit-learn documentation: https://scikit-learn.org/stable/datasets/toy_dataset.html#diabetes-dataset
- Original source: Bradley Efron, Trevor Hastie, Iain Johnstone, Robert
  Tibshirani, *"Least Angle Regression"*, Annals of Statistics (2004),
  https://web.stanford.edu/~hastie/Papers/LARS/LeastAngle_2002.pdf

It records baseline clinical measurements for diabetes patients together
with a follow-up measure of disease progression.

## Size

| | |
|---|---|
| Instances (patients) | 442 |
| Attributes (features) | 10 |
| Target | 1 (disease progression) |

## Attributes

All 10 input features are physiological measurements. In the version
scikit-learn ships, each one has already been **mean-centered and scaled**
(divided by its standard deviation times `sqrt(442)`), so every column
is a small real-valued number rather than its original unit — but the
underlying quantity each one represents is:

| Feature | Description | Type |
|---|---|---|
| `age` | Age | Continuous (numeric) |
| `sex` | Sex | Binary/categorical (two levels, numerically encoded) |
| `bmi` | Body mass index | Continuous |
| `bp` | Average blood pressure | Continuous |
| `s1` (`tc`) | Total serum cholesterol | Continuous |
| `s2` (`ldl`) | Low-density lipoproteins | Continuous |
| `s3` (`hdl`) | High-density lipoproteins | Continuous |
| `s4` (`tch`) | Total cholesterol / HDL ratio | Continuous |
| `s5` (`ltg`) | Possibly log of serum triglycerides level | Continuous |
| `s6` (`glu`) | Blood sugar level | Continuous |

So of the 10 attributes, 9 are continuous and 1 (`sex`) is binary/categorical.
There are no missing values in the dataset.

**Target (`y`):** a quantitative measure of disease progression one year
after baseline, a continuous value ranging roughly from 25 to 346.

## Suited machine learning problem

**Regression.** The target is a continuous quantity (disease progression
score), not a class label, so this dataset is designed for predicting a
numeric outcome from the 10 baseline measurements — e.g. linear
regression, ridge/lasso regression, or other regressors. It is not
natively set up for classification unless the continuous target is
manually binned into categories.
