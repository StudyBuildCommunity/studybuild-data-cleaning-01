# studybuild-data-cleaning-01
Project 01: Data Cleaning on a Real E-commerce Dataset

## 1. Problems found in the data
| # | Problem | Column(s) | Rows affected |
|---|---|---|---|
| 1 | Fully duplicated row | all | 1 (customer_id 1014) |
| 2 | Missing value | `age` | 1 |
| 3 | Missing value | `total_spending` | 1 |
| 4 | Impossible value (age = 145) | `age` | 1 |
| 5 | Inconsistent value (25000 vs an expected ~4079) | `total_spending` | 1 (customer_id 1030) |
| 6 | Logical inconsistency: `returned_items` > `purchase_count` | `returned_items` | 6 |
| 7 | `gender` inconsistent with the conventional gender of `first_name` (e.g. "Zahra" as Male, "Ali" as Female) | `gender` | 38 |

## 2. Changes made and why
1. **Duplicate row removed.** Customer 1014 was repeated with identical values in every column — kept the first occurrence.
2. **Impossible age (145) treated as invalid.** No customer can be 145 years old; this was set to missing and then imputed (see below) rather than left in, since it would badly skew any age-based analysis.
3. **Missing `age` imputed with the median age** (45). With only one affected row, the median is a safe, low-bias fill that won't distort the age distribution.
4. **Missing `total_spending` recomputed** as `avg_order_value × purchase_count`. This identity holds exactly for every other row in the dataset, so it's a reliable way to reconstruct the missing value rather than guessing or dropping the row.
5. **Inconsistent `total_spending` corrected** the same way — customer 1030 showed 25000, but `avg_order_value × purchase_count` implied ~4079.14, a >5x mismatch. Treated as a data-entry error and replaced with the consistent value.
6. **`returned_items` capped at `purchase_count`** for 6 rows where returns exceeded purchases — logically impossible (you can't return more than you bought), so the values were capped rather than dropped, keeping the rest of each row's information intact.
7. **`gender` corrected using `first_name`.** These are all common Persian first names with a strongly conventional gender (Ali, Amir, Arash, Reza, Sina, Parsa → male; Kimia, Maryam, Mina, Neda, Sara, Zahra → female). 38 of the 60 rows (almost two-thirds) had the *opposite* gender recorded — clearly not real-world data, most likely shuffled/randomized during dataset creation. Standardized `gender` to match each name's conventional gender, since the original column could not be trusted for any gender-based analysis.
8. **Data types standardized:** `signup_date` → datetime, `age` → integer, `discount_used` → boolean (Yes/No → True/False).

## 3. Missing values — how they were handled
- `age`: median imputation (1 originally missing + 1 invalid value treated as missing).
- `total_spending`: recomputed from `avg_order_value × purchase_count` rather than imputed blindly, since the relationship is deterministic elsewhere in the data.

## 4. Duplicates — how they were checked
Checked both for fully identical rows (`df.duplicated()`) and for repeated `customer_id` values. Found one row that was both — customer 1014 appeared twice with every field identical.

## 5. Data type changes
- `signup_date`: string → datetime
- `age`: float → int
- `discount_used`: Yes/No string → boolean

## 6. Outliers / illogical values
- Age of 145 (impossible).
- `total_spending` of 25000 that didn't match the customer's own `avg_order_value × purchase_count`.
- 6 rows where `returned_items` exceeded `purchase_count` (impossible under normal e-commerce logic).
- 38 rows where `gender` didn't match the customer's `first_name` (e.g., "Zahra" — a female name — recorded as Male).

## 7. Tools used
Python 3, pandas, numpy, openpyxl (for reading/writing the Excel file).

## 8. Final vs. original dataset
- 61 rows → 60 rows (1 exact duplicate removed).
- 0 missing values remaining (previously 2).
- All `total_spending` values now consistent with `avg_order_value × purchase_count`.
- No more impossible ages or impossible return counts.
- Clean, consistent data types throughout.

## Files
- `cleaned_dataset.xlsx` — the cleaned dataset.
- `data_cleaning.ipynb` — full cleaning code + answers to the project's analysis questions, plus extra questions.
- `README.md` — this file.
