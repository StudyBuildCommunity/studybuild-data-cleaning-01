# studybuild-data-cleaning-01
Project 01: Data Cleaning on a Real E-commerce Dataset

## Project Overview

This project focuses on cleaning a customer dataset using Python and Pandas. The objective is to identify and resolve data quality issues to ensure the dataset is consistent, accurate, and ready for further analysis.

---

## Dataset Overview

The dataset contains customer information, including:

- Customer ID
- First Name
- Gender
- Age
- City
- Province
- Signup Date
- Membership Tier
- Purchase Count
- Average Order Value
- Total Spending
- Days Since Last Purchase
- Payment Method
- Device
- Discount Usage
- Returned Items
- Satisfaction Score

---

## Libraries Used

- pandas

---

## Data Cleaning Process

### 1. Initial Data Inspection

The dataset was inspected to understand its overall structure.

The following checks were performed:

- Dataset dimensions (`shape`)
- Column names
- Data types (`info()`)
- Summary statistics (`describe()`)

---

### 2. Duplicate Records

Duplicate rows were identified using the `duplicated()` method.

The duplicated record was removed to avoid redundant information during analysis.

---

### 3. Missing Values

Missing values were identified using `isnull()`.

Two columns contained missing values:

- `age`
- `total_spending`

#### Handling Strategy

- Missing values in **Age** were replaced using the **median**, since age may contain outliers and the median is more robust than the mean.
- Missing values in **Total Spending** were recalculated using the following business rule:

```
Total Spending = Purchase Count × Average Order Value
```

This preserved the logical relationship between the columns.

---

### 4. Data Type Correction

The `signup_date` column was originally stored as an `object` (string).

It was converted to the `datetime` data type to enable proper date-based analysis in later stages.

---

### 5. Invalid Values

Several invalid values were detected and corrected.

#### Unrealistic Age

An age value greater than 100 years was considered invalid.

The invalid value was replaced with the median age of the dataset.

---

### 6. Inconsistent Categorical Values

Categorical columns were inspected using frequency counts (`value_counts()`).

The following columns were reviewed:

- Gender
- City
- Province
- Membership Tier
- Payment Method
- Device
- Discount Used

A consistency check between **First Name** and **Gender** revealed several incorrect gender labels.

Examples included:

- Arash → Female
- Kimia → Male
- Maryam → Male
- Zahra → Male

Since this is an educational dataset with predefined Iranian names, the gender values were corrected using a mapping dictionary based on the customer's first name.

---

### 7. Business Rule Validation

Logical relationships between columns were validated.

#### Returned Items

A customer cannot return more items than they have purchased.

The following rule was checked:

```
Returned Items ≤ Purchase Count
```

Records violating this rule were corrected by setting the number of returned items equal to the purchase count.

---

#### Total Spending Validation

The following relationship was verified:

```
Purchase Count × Average Order Value = Total Spending
```

Two records were found to be inconsistent with this rule. Since the correct values could not be inferred confidently, these records were intentionally left unchanged and flagged for further review instead of being modified.

---

## Summary of Data Issues Found

The following data quality problems were identified:

- Duplicate records
- Missing values
- Incorrect data types
- Unrealistic age values
- Inconsistent gender labels
- Invalid business rule violations (Returned Items > Purchase Count)

---

## Final Result

After completing the cleaning process, the dataset:

- Contains no duplicate records.
- Contains no unresolved missing values.
- Uses appropriate data types.
- Contains corrected gender values.
- Contains realistic age values.
- Returned item inconsistencies were corrected.
- Total spending was validated against the business rule, and inconsistent records were identified but intentionally left unchanged for further investigation.
- Is ready for Exploratory Data Analysis (EDA) and machine learning tasks.

---

## Output

The cleaned dataset was exported as an Excel file:

```
cleaned_dataset_maralfarahmandfar.xlsx
```

---

## Author

**Maral Farahmandfar**