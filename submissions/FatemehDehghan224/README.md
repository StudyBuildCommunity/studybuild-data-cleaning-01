# Project 01 - Data Cleaning

## Overview

This project performs the first-stage data cleaning workflow for an online-store customer dataset. The goal is to assess data quality, identify inconsistencies, apply defensible corrections, document each cleaning decision, and prepare a clean dataset for later analysis or modeling.

The full workflow is implemented in a single Jupyter notebook. The raw Excel workbook is kept unchanged, while the cleaned dataset is exported to Excel after final validation. Quality checks, audit logs, validation tables, and charts are displayed inside the notebook.

## Repository Structure

```text
project-01-data-cleaning-FatemehDehghan224/
+-- clean_data_code/
|   +-- customer_data_cleaning_pipeline.ipynb
|   +-- name_gender_mapping.json
+-- data/
|   +-- raw_dataset_FatemehDehghan224.xlsx
|   +-- cleaned_dataset_FatemehDehghan224.xlsx
+-- requirements.txt
+-- README.md
```

## Inputs and Outputs

- Raw dataset: `data/raw_dataset_FatemehDehghan224.xlsx`
- Name-to-gender reference file: `clean_data_code/name_gender_mapping.json`
- City and province reference rules are defined inside the notebook through `CITY_PROVINCE_REFERENCE`, `CITY_ALIASES`, and `PROVINCE_ALIASES`.
- The final cleaned dataset is stored in the notebook variable `final_df`.
- After final validation passes, the cleaned dataset is written to `data/cleaned_dataset_FatemehDehghan224.xlsx`.
- The notebook also displays assessment tables, audit logs, charts, and final validation results.
- The exported workbook uses the `customers` sheet and preserves the raw workbook as read-only input.

## Requirements

This project uses:

- Python
- pandas
- openpyxl
- matplotlib
- JupyterLab

Install the dependencies with:

```powershell
python -m pip install -r requirements.txt
```

## How to Run

Open the main notebook:

```powershell
jupyter lab clean_data_code\customer_data_cleaning_pipeline.ipynb
```

Then run all notebook cells in order. After the preprocessing and final validation cells pass, the cleaned Excel file is created at:

```text
data/cleaned_dataset_FatemehDehghan224.xlsx
```

Save the notebook so the generated tables, charts, and validation output remain visible in the file.

## Data Cleaning Decisions

### 1. Missing Values

Two missing values were identified:

- `age`
- `total_spending`

The missing `age` value was imputed using the median age, because the median is more robust than the mean when numeric data may contain outliers.

The missing `total_spending` value was recalculated from related fields:

```text
total_spending = round(purchase_count * avg_order_value, 3)
```

This approach was selected because `total_spending` is a derived value, so recalculating it from its source columns is more accurate than using a statistical imputation.

### 2. Duplicate Records

One fully duplicated record was found. Because all values in the duplicated rows were identical, the first occurrence was kept and the duplicate row was removed.

### 3. Invalid Return Counts

Some rows had `returned_items` values greater than `purchase_count`. This is not logically valid, because returned items cannot exceed purchased items.

The correction rule was:

```text
if returned_items > purchase_count:
    returned_items = purchase_count
```

This keeps the record while enforcing the business rule at row level.

### 4. `total_spending` Outliers

The `total_spending` column was reviewed using the IQR method. Outliers were not automatically removed or capped, because high spending can represent valid high-value customers.

Each outlier was checked against the expected formula:

```text
total_spending = round(purchase_count * avg_order_value, 3)
```

Only one value was identified as a true calculation error:

- `customer_id = 1030`
- Original `total_spending = 25000`
- Corrected `total_spending = 4079.140`

Formula-consistent outliers were kept unchanged.

### 5. `total_spending` Precision

All `total_spending` values are standardized to three decimal places:

```text
total_spending = round(total_spending, 3)
```

The column remains numeric so it can still be used for calculations, aggregation, and modeling. Notebook display formatting is used when trailing zeroes need to be shown, such as displaying `2066.01` as `2066.010`.

### 6. Invalid Age

One invalid age value was found:

```text
age = 145
```

For this project, valid ages are defined as values from 13 to 100. Invalid ages are replaced with the median of valid ages:

```text
if age < 13 or age > 100:
    age = median(valid ages)
```

### 7. City and Province Standardization

The `city` and `province` columns are validated together, because each city must match its correct province. The notebook uses an explicit city-province reference, for example:

```text
Mashhad -> Khorasan Razavi
Rasht   -> Guilan
Karaj   -> Alborz
```

The location assessment checks for:

- Unknown cities or provinces.
- Known spelling, casing, or alias variants, such as `Gilan`, `Guilan`, and `Giluan`.
- Mismatches between a city and its assigned province.

In this dataset, 16 province values required standardization. For example, `Khorasan` was treated as incomplete for `Mashhad` and standardized to `Khorasan Razavi`. The final spelling selected for the Guilan province is `Guilan`.

Every location correction is recorded in the audit log with the original value, corrected value, and reference rule.

### 8. Name and Gender Alignment

The dataset contains 12 unique first names. The reviewed name-to-gender mapping is stored in `clean_data_code/name_gender_mapping.json`:

- Male (`M`): `Ali`, `Amir`, `Arash`, `Parsa`, `Reza`, `Sina`
- Female (`F`): `Kimia`, `Maryam`, `Mina`, `Neda`, `Sara`, `Zahra`

The notebook loads this JSON file, validates that all current first names are covered, and corrects `gender` values when they conflict with the reference mapping. Names are compared after whitespace normalization and case-folding, but the original `first_name` value is not changed.

After duplicate removal, 38 rows had gender values that conflicted with the reference mapping. These values were corrected and recorded in the audit log.

If a future dataset contains a new name that is not present in the JSON file, the pipeline stops instead of guessing the gender.

### 9. Date Conversion and Binary Gender Encoding

The `signup_date` column is converted from an object/string representation to the pandas datetime type:

```text
datetime64
```

Before finalization, the notebook checks for invalid or future signup dates.

The corrected `gender` column is encoded as a binary numeric field for analysis and modeling:

```text
F -> 0
M -> 1
```

This mapping is defined explicitly in the notebook through `GENDER_BINARY_MAPPING`.

## Final Dataset Status

After cleaning:

- There are no missing values.
- There are no fully duplicated records.
- `customer_id` values are unique.
- There are no cases where `returned_items > purchase_count`.
- `city` and `province` values are consistent with the reviewed location reference.
- All names are covered by the JSON name-gender reference.
- `gender` is consistent with `first_name` and encoded as `F = 0`, `M = 1`.
- `signup_date` is stored as `datetime64`, not as an object/string column.
- `total_spending` is formula-consistent.
- `total_spending` calculations and displays use three-decimal precision.
- Valid high-spending outliers are preserved.
- Only confirmed data errors are corrected.

## Raw vs. Cleaned Dataset

Main changes from the raw dataset to the cleaned dataset:

- Row count changed from 61 to 60 after removing one fully duplicated record.
- Missing values in `age` and `total_spending` were corrected.
- Invalid `returned_items` values were corrected.
- One incorrect `total_spending` calculation was corrected.
- `total_spending` precision was standardized to three decimal places.
- One invalid age value was corrected.
- 16 province values were standardized using the city-province reference.
- 38 gender values were corrected using the reviewed name-gender mapping.
- `signup_date` was converted from object/string format to `datetime64`.
- Final `gender` values were encoded as binary integers.
- The cleaned dataset was exported to `data/cleaned_dataset_FatemehDehghan224.xlsx`.

## Outlier Policy

Outliers are reviewed before correction. In this project, valid outliers are preserved because they may represent high-value customers. Removing them could distort sales analysis and customer value insights.

Only values that violate a clear formula, schema, or business rule are changed.
