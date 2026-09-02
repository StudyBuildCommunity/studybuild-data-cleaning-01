## Data Cleaning and Validation

### Missing Values and Invalid Data

First, the values in the different columns were examined. One **missing value (NaN)** was identified in the `age` column. In addition, one **invalid age value** was detected. The missing and invalid values were replaced using the **median age**. The median was chosen because it is generally more robust to outliers than the mean. The data type of the `age` column was also changed from `float` to `integer`.

In the `total_spending` column, one missing value (NaN) and one value inconsistent with the underlying calculation logic were identified. To validate this column, its values were compared with the result of `purchase_count × avg_order_value`, and the inconsistent values were corrected accordingly.

### Gender Reference Dataset
Several values in the gender column were inconsistent with the gender associated with the corresponding names. To validate these values, the names in the dataset were compared with a reference dataset containing Iranian names and their associated genders. For gender validation, a reliable dataset or name dictionary specific to the same country should be used, since naming patterns and gender associations vary across countries.

The gender reference dataset was obtained from the [Persian Gender Detection by Name] (https://github.com/farbodbj/persian-gender-by-name) repository. The reference data was used only to generate a `suggested_gender` value and flag potential inconsistencies. The original `gender` values were not automatically modified, since name-based gender classification is not necessarily definitive.

### Purchase and Spending Validation
Records with zero purchases but a positive average order value were flagged for review. These cases may potentially be explained by returned items being excluded from purchase totals while their associated order values remain recorded. However, this is only a possible explanation and is not treated as a confirmed business rule. No values were automatically modified.

### Returned Items Validation
Records where the number of returned items exceeded the number of purchases were also flagged for review, rather than being automatically corrected.

### Duplicate Records
Duplicate records were checked using `duplicated().sum()`. One duplicate record was identified and removed.

### Data Types

The data types of the columns were reviewed and modified where necessary to match the nature of the data. The `age` column was converted to `int64`, `signup_date` to `datetime64[ns]`, and `discount_used` to `bool`.

### Outlier Analysis

During the outlier analysis, one unusual value was identified in the `age` column and corrected. In addition, five outlier values were detected in `avg_order_value`. After investigation, these values were determined not to be data errors, so they were retained without modification.

### Tools

**Pandas** and **NumPy** were used for data inspection, validation, and cleaning.

### Final Dataset

Finally, the dataset was re-evaluated to ensure that the issues identified above had been addressed. The cleaned dataset was saved as `cleaned_dataset.xlsx`.
