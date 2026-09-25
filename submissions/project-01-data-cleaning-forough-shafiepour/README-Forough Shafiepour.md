`# Data Cleaning Project — E-commerce Customer Dataset`

**`**Author:**`** `Forough Shafiepour`    
**`**Course:**`** `StudyBuild - Project 01`    
**`**Tools:**`** `Python 3, pandas, NumPy, Jupyter Notebook`

`---`

`## 1. Project Overview`  
`Cleaning a raw e-commerce customer dataset (61 rows → 60 after dedup)`   
`to prepare it for EDA, visualization, and ML.`

`---`

`## 2. Dataset Summary`

`| Aspect | Before | After |`  
`|--------|--------|-------|`  
`| Rows | 61 | 60 |`  
`| Columns | 17 | 17 |`  
`| Duplicates | 1 | 0 |`  
`| Missing values | 2 | 3 |`  
`| Memory | 12.06 KB | 6.10 KB |`

`---`

`## 3. Issues Identified & Decisions`

`### 3.1 Duplicate Records`  
`- **customer_id = 1014** appeared twice.`  
`- **Action:** Removed duplicate, kept first occurrence.`

`### 3.2 Missing Values`  
``- `age`: 1 missing (customer_id = 1020)``  
``- `total_spending`: 1 missing (customer_id = 1040)``

`| Column | Decision | Reason |`  
`|--------|----------|--------|`  
`| age (1020) | Kept as NA | Other 16 fields intact |`  
`| total_spending (1040) | Imputed: 34 × 37.66 = **1280.44** | Business rule holds in 96.7% of rows |`

`### 3.3 Incorrect Data Types`

`| Column | Before | After | Reason |`  
`|--------|--------|-------|--------|`  
`| signup_date | str | datetime64 | Enable temporal analysis |`  
`| age | float64 | Int64 | Integer + NA preservation |`  
`| discount_used | str | bool | Binary nature |`  
`| gender, city, province, payment_method, device | str | category | Memory + semantics |`  
`| membership_tier | str | ordered category | Hierarchy: Bronze < Silver < Gold < VIP |`

`### 3.4 Invalid Values`

**`**customer_id = 1030:**`** `` `total_spending = 25000` violated rule `total = count × avg` (expected 4079.14). ``    
`→ **Action:** Corrected to 4079.14.`

**`**customer_id = 1010:**`** `` `age = 145` biologically impossible. ``    
`→ **Action:** Replaced with NA.`

`### 3.5 Outliers (IQR Method)`

``Applied to `total_spending`:``  
`- Q1 = 1165.33, Q3 = 4769.25, IQR = 3603.92`  
`- Upper Bound = 10175.13`  
`- 5 outliers detected`

**`**Masking Effect:**`** `After fixing row 1030, upper bound dropped to 8782.24, revealing a new outlier (1059).`

**`**Decision:**`** `Kept 5 outliers (1009, 1012, 1044, 1057, 1059) — all follow the business rule → legitimate high-value customers.`

`### 3.6 Additional Consistency Checks`

`| Check | Result | Action |`  
`|-------|--------|--------|`  
`| Zero spending with purchases | 0 | ✅ |`  
`| Future signup dates | 0 | ✅ |`  
`| Satisfaction range | 1–5 | ✅ |`  
`| Returned > purchased | **6 rows** | ⚠️ Documented, not corrected |`  
`| Unrealistic age (>100) | 1 | ✅ Replaced with NA |`

**`**Finding — Returned > Purchased (6 rows):**`**

`| customer_id | purchase_count | returned_items |`  
`|-------------|----------------|----------------|`  
`| 1008 | 3 | 8 |`  
`| 1015 | 3 | 8 |`  
`| 1024 | 0 | 2 |`  
`| 1029 | 2 | 4 |`  
`| 1037 | 1 | 7 |`  
`| 1056 | 1 | 4 |`

**`**Decision:**`** `Documented only. Cannot determine which column is wrong without source system; correcting speculatively could destroy valid data.`

`---`

`## 4. Final Dataset`

`| Aspect | Value |`  
`|--------|-------|`  
`| Rows | 60 |`  
`| Columns | 17 |`  
`| Duplicates | 0 |`  
`| Missing values | 3 (age ×2, none in total_spending) |`

**`**Final Data Types:**`**

`| Type | Columns |`  
`|------|---------|`  
`| int64 | customer_id, purchase_count, last_purchase_days, returned_items, satisfaction_score |`  
`| Int64 | age |`  
`| float64 | avg_order_value, total_spending |`  
`| bool | discount_used |`  
`| datetime64 | signup_date |`  
`| category | gender, city, province, payment_method, device, membership_tier |`  
`| str | first_name |`

`---`

`## 5. Note on dtype Persistence`  
`Excel does not preserve pandas dtypes (category, Int64, ordered category).`   
``Re-running `data_cleaning_forough-shafiepour.ipynb` restores them.``

`---`

`## 6. Differences from Original`

`| Item | Original | Cleaned |`  
`|------|----------|---------|`  
`| Rows | 61 | 60 |`  
`| Duplicates | 1 | 0 |`  
`| Missing values | 2 | 3 |`  
`| signup_date dtype | object | datetime64 |`  
`| age dtype | float64 | Int64 |`  
`| discount_used dtype | object | bool |`  
`| Categorical columns | object | category |`  
`| membership_tier | str | ordered category |`  
`| total_spending (1030) | 25000 | 4079.14 |`  
`| total_spending (1040) | NaN | 1280.44 |`  
`| age (1010) | 145 | NA |`

`---`

`## 7. Potential EDA Questions`

`1. Which membership tier generates the highest revenue?`  
`2. Does discount usage correlate with total spending?`  
`3. Which cities have the most high-value customers?`  
`4. Average satisfaction score per tier?`  
`5. Signup trend over time?`

`---`

`## 8. Lessons Learned`

``- Always inspect `df.info()` and `df.dtypes` first``  
`- Not all outliers are errors — check business rules`  
`- Masking effect: re-run IQR after removing extremes`  
`- Document every decision with reason`  
`- Excel doesn't preserve dtypes`

`---`

`## 9. File Structure`  
