# Data Quality Assessment

Source file: `data\cleaned_dataset_FatemehDehghan224.xlsx`
Rows: 60
Columns: 17

## Checks

- Missing value columns: 0
- Rows with missing values: 0
- Full duplicate rows: 0
- Duplicate customer_id rows: 0
- Invalid type values: 0
- Invalid logical values: 0
- Text whitespace issues: 0
- Text normalized duplicate groups: 0
- Possible text typo pairs: 0
- IQR outlier values: 5

## Generated Files

- `01_basic_column_info.csv`
- `02_missing_values_summary.csv`
- `02_rows_with_missing_values.csv`
- `03_duplicate_full_rows.csv`
- `03_duplicate_customer_ids.csv`
- `04_data_type_summary.csv`
- `04_invalid_type_values.csv`
- `05_invalid_logical_values.csv`
- `06_text_whitespace_issues.csv`
- `06_text_case_space_groups.csv`
- `06_text_possible_typos.csv`
- `07_outlier_summary_iqr.csv`
- `07_outlier_rows_iqr.csv`
- `charts/*.png`

## Notes For Cleaning Phase

This script only identifies data quality problems. It does not modify or clean the dataset.
Use the generated CSV files to decide how each issue should be handled in the next phase.

## Columns

| column | dtype | non_null_count | null_count | unique_count |
| --- | --- | --- | --- | --- |
| customer_id | int64 | 60 | 0 | 60 |
| first_name | str | 60 | 0 | 12 |
| gender | str | 60 | 0 | 2 |
| age | int64 | 60 | 0 | 33 |
| city | str | 60 | 0 | 8 |
| province | str | 60 | 0 | 8 |
| signup_date | str | 60 | 0 | 58 |
| membership_tier | str | 60 | 0 | 4 |
| purchase_count | int64 | 60 | 0 | 30 |
| avg_order_value | float64 | 60 | 0 | 60 |
| total_spending | float64 | 60 | 0 | 60 |
| last_purchase_days | int64 | 60 | 0 | 54 |
| payment_method | str | 60 | 0 | 3 |
| device | str | 60 | 0 | 3 |
| discount_used | str | 60 | 0 | 2 |
| returned_items | int64 | 60 | 0 | 9 |
| satisfaction_score | int64 | 60 | 0 | 5 |

## Missing Values

| column | missing_count | missing_percent |
| --- | --- | --- |
| age | 0 | 0.0 |
| avg_order_value | 0 | 0.0 |
| city | 0 | 0.0 |
| customer_id | 0 | 0.0 |
| device | 0 | 0.0 |
| discount_used | 0 | 0.0 |
| first_name | 0 | 0.0 |
| gender | 0 | 0.0 |
| last_purchase_days | 0 | 0.0 |
| membership_tier | 0 | 0.0 |
| payment_method | 0 | 0.0 |
| province | 0 | 0.0 |
| purchase_count | 0 | 0.0 |
| returned_items | 0 | 0.0 |
| satisfaction_score | 0 | 0.0 |
| signup_date | 0 | 0.0 |
| total_spending | 0 | 0.0 |

## Outlier Summary

| column | q1 | q3 | iqr | lower_bound | upper_bound | outlier_count | outlier_percent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| age | 31.75 | 58.0 | 26.25 | -7.625 | 97.375 | 0 | 0.0 |
| purchase_count | 10.75 | 24.5 | 13.75 | -9.875 | 45.125 | 0 | 0.0 |
| avg_order_value | 108.1375 | 324.1075 | 215.97 | -215.8175 | 648.0625 | 0 | 0.0 |
| total_spending | 1167.035 | 4213.1175 | 3046.0825 | -3402.0888 | 8782.2413 | 5 | 8.33 |
| last_purchase_days | 134.25 | 273.75 | 139.5 | -75.0 | 483.0 | 0 | 0.0 |
| returned_items | 1.0 | 6.0 | 5.0 | -6.5 | 13.5 | 0 | 0.0 |
| satisfaction_score | 2.0 | 4.0 | 2.0 | -1.0 | 7.0 | 0 | 0.0 |
