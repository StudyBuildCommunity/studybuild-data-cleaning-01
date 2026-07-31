# Data Cleaning Report

## Overview
I cleaned up a raw customer dataset to fix data quality issues, handle missing values, and make sure the numbers add up logically before doing any further analysis.

---

## 1. Issues Found in Raw Data
When checking the dataset, I ran into a few problems:
* Missing data in several columns.
* Duplicate customer entries based on `customer_id`.
* Inconsistent text formats (spaces, lowercase/uppercase mix, typos in city names).
* Wrong gender entries that didn't match first names.
* Unrealistic numbers (e.g. age > 100, or returned items higher than total purchases).
* Date columns stored as regular text instead of dates.

---

## 2. What I Fixed & Why

* **Missing Data & Duplicates:** 
  Filled missing numbers with the column median to keep things balanced, and filled missing categories with the most frequent value. Dropped duplicate rows based on `customer_id`.

* **Text Formatting & Gender Fix:**
  Trimmed extra spaces and fixed capitalization across text columns. Corrected the `gender` column by matching it against first names to fix conflicts.

* **Fixing Logic & Math Errors:**
  Recalculated `total_spending` (`purchase_count * avg_order_value`) so the math actually makes sense. Capped `returned_items` at `purchase_count` so no one has more returns than actual buys.

* **Outliers & Dates:**
  Replaced ages over 100 with the median age. Converted `signup_date` to `datetime64` so it's ready for any time-based analysis.

---

## 3. Tools Used
* Python (Pandas, NumPy)

---

## 4. Quick Comparison

| Feature | Raw Data | Cleaned Data |
| :--- | :--- | :--- |
| **Duplicates & Missing Values** | Present | Fully cleaned |
| **Math & Logic** | Had mismatches in spending & returns | Fixed and consistent |
| **Text & Names** | Typos, extra spaces, mixed casing | Clean and standardized |
| **Dates** | Stored as text | Converted to proper dates |
