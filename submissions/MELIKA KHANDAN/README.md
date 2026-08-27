# Project 01 - Data Cleaning

## About

This project is the first project of the StudyBuild program.

The main goal of the project was to take a raw e-commerce customer dataset, check the quality of the data, identify existing problems, and clean the dataset so it can be used for further analysis.

I used Python and Pandas for the data cleaning process and Jupyter Notebook to run and document the steps.

---

## Dataset

The dataset contains customer information such as:

- Customer ID
- Name
- Gender
- Age
- City and Province
- Signup Date
- Membership Tier
- Purchase Count
- Average Order Value
- Total Spending
- Last Purchase Days
- Payment Method
- Device
- Discount Usage
- Returned Items
- Satisfaction Score

The original dataset contained **61 rows** and **17 columns**.

---

## Data Problems

After checking the dataset, I found the following problems:

- One missing value in the `age` column
- One missing value in the `total_spending` column
- One unrealistic age value (`145`)
- One duplicate record
- `signup_date` was stored as an object instead of a datetime value
- One inconsistent value in `total_spending`

---

## Cleaning Steps

### 1. Missing Age

There was one missing value in the `age` column.

The missing value was filled using the median age of the dataset.

---

### 2. Invalid Age

One customer had an age of `145`, which is not a reasonable value for this dataset.

This value was replaced with the median age.

After the correction, the age values were checked to make sure they were within a reasonable range.

---

### 3. Duplicate Record

A duplicate record was found for customer `1014`.

The duplicate row was completely identical to another row, so it was removed.

The number of records changed from **61 to 60**.

---

### 4. Signup Date

The `signup_date` column was converted from object format to datetime format.

No invalid dates were found after the conversion.

This makes the column easier to use for future date-based analysis.

---

### 5. Total Spending

The relationship between `purchase_count`, `avg_order_value`, and `total_spending` was checked.

For customer `1030`, the dataset contained:

- `purchase_count = 26`
- `avg_order_value = 156.89`
- Original `total_spending = 25000`

Based on the purchase information, the expected total spending was:

`26 × 156.89 = 4079.14`

The original value of `25000` was inconsistent with the calculated value, so it was corrected.

The same calculation was also used to fill the missing `total_spending` value for customer `1040`.

After completing the corrections, the temporary calculation columns used during the validation process were removed from the final dataset.

---

## Validation

After completing the cleaning steps, the dataset was checked again for:

- Missing values
- Duplicate rows
- Data types
- Invalid ages
- Invalid satisfaction scores

The final validation showed that there were no remaining missing values or duplicate rows.

The age values were also within the expected range, and all satisfaction scores were within the valid range of 1 to 5.

---

## Before and After

| Check | Before | After |
|---|---:|---:|
| Rows | 61 | 60 |
| Columns | 17 | 17 |
| Missing Values | 2 | 0 |
| Duplicate Rows | 1 | 0 |
| Invalid Age | 1 | 0 |
| Invalid Satisfaction Score | 0 | 0 |

---

## Final Result

The final dataset contains:

- **60 rows**
- **17 columns**
- **0 missing values**
- **0 duplicate rows**
- **No invalid age values**
- **No invalid satisfaction scores**
- `signup_date` converted to datetime
- Corrected `total_spending` values

The final dataset was also checked to make sure the temporary calculation columns used during the cleaning process were removed.

The cleaned dataset was saved as:

`cleaned_dataset.xlsx`

---

## Tools Used

- Python
- Pandas
- NumPy
- Jupyter Notebook
- OpenPyXL
- Microsoft Excel

---

## Project Structure

```text
project-01-data-cleaning/

│
├── data/
│   └── cleaned_dataset.xlsx
│
├── notebook/
│   └── data_cleaning.ipynb
│
└── README.md
```

---

## Result

The raw dataset was checked and cleaned step by step.

The final dataset is now more consistent and ready to be used for further analysis and future projects.

---

## Author

**Melika Khandan**

**Project:** StudyBuild - Project 01  
**Topic:** Data Cleaning  
**Date:** August 2026