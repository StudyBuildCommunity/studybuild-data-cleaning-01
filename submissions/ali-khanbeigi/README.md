# Project 01: Customer Data Cleaning

## Project Overview

The objective of this project was to clean and prepare a customer dataset for further analysis. The dataset was examined for missing values, duplicate records, invalid values, and data inconsistencies to improve its overall quality and reliability.

---

## Dataset Issues Identified

During the data cleaning process, the following issues were identified:

- Missing values in the **age** and **total_spending** columns.
- Duplicate records.
- An unrealistic age value (145 years old).
- An inconsistent record where **purchase_count = 0** but **avg_order_value > 0**.
- Incorrect gender values in several records (educational dataset).

---

## Data Cleaning Actions

The following cleaning steps were performed:

- Removed duplicate records.
- Filled missing values in the **age** column using the median.
- Calculated missing values in **total_spending** using:

  **purchase_count × avg_order_value**

- Replaced the unrealistic age value with the median age.
- Corrected incorrect gender values based on first names (for educational purposes).

---

## Why These Changes Were Made

- Duplicate records were removed to prevent duplicated observations.
- The median was used for the **age** column because it is less sensitive to outliers.
- Missing **total_spending** values were calculated using existing business information instead of estimation.
- Invalid values were corrected to improve data quality.
- Gender inconsistencies were corrected because this dataset was created for educational purposes.

---

## Missing Value Handling

Two missing values were identified:

- **age** → Replaced with the median.
- **total_spending** → Calculated using:

  **purchase_count × avg_order_value**

---

## Duplicate Handling

Duplicate records were identified using:

```python
df.duplicated()
```

They were verified and removed using:

```python
df.drop_duplicates()
```

---

## Data Type Changes

No data type conversions were performed in Python.

The final data type formatting was completed in Microsoft Excel after exporting the cleaned dataset.

---

## Outliers and Invalid Values

One unrealistic value was detected:

- **Age = 145**

This value was replaced with the median age.

An inconsistent record was also identified where:

- purchase_count = 0
- avg_order_value > 0

Since the correct value could not be verified, the record was documented and retained.

---

## Tools and Libraries

- Python
- Pandas
- NumPy
- Jupyter Notebook
- Microsoft Excel

---

## Final Dataset Improvements

Compared to the original dataset, the cleaned dataset:

- Contains no duplicate records.
- Contains no missing values.
- Has corrected invalid age values.
- Includes corrected gender values (educational purpose).
- Is cleaner and ready for exploratory data analysis (EDA), dashboard development, and further analytics.

