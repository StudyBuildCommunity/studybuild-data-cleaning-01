# Customer Data Cleaning

Cleaning and validating a small synthetic customer dataset (61 rows, 17 columns) with pandas. The notebook handles duplicates, missing values, impossible values, internally inconsistent records and data types, then checks the result and exports a clean CSV.

## Dataset

`First_Dataset.xlsx` contains one row per customer. The data is synthetic.

| Column | Description |
|---|---|
| `customer_id` | Unique customer identifier |
| `first_name`, `gender`, `age` | Customer demographics |
| `city`, `province` | Customer location |
| `signup_date` | Date the customer signed up |
| `membership_tier` | Bronze / Silver / Gold / VIP |
| `purchase_count` | Number of purchases |
| `avg_order_value` | Average value of one purchase |
| `total_spending` | Total amount spent (`purchase_count × avg_order_value`) |
| `last_purchase_days` | Days since the last purchase |
| `payment_method`, `device` | Payment method and device used |
| `discount_used` | Whether the customer used a discount (Yes/No) |
| `returned_items` | Number of returned items |
| `satisfaction_score` | Satisfaction rating from 1 to 5 |

## Data Quality Issues and How They Were Handled

| # | Issue | Action | Rows affected |
|---|---|---|---|
| 1 | Exact duplicate row (customer 1014) | Removed with `drop_duplicates()` | 1 removed |
| 2 | Missing `age` | Row dropped | 1 removed |
| 3 | Missing `total_spending` (customer 1040) | Filled with the value implied by the other columns: 34 × 37.66 = 1,280.44 | 1 filled |
| 4 | Impossible age of 145 (customer 1010) | Replaced with the median age (45); row kept | 1 imputed |
| 5 | `purchase_count = 0` (customer 1024), who also has 2 returned items and a last purchase 298 days ago | Removed: the record contradicts itself | 1 removed |
| 6 | `total_spending` of 25,000 for customer 1030, but 26 × 156.89 = 4,079.14 | Corrected to 4,079.14 | 1 corrected |
| 7 | `returned_items` greater than `purchase_count` (customers 1008, 1015, 1029, 1037, 1056) | Kept: the true values are unknown. See Limitations | 5 identified |
| 8 | Wrong data types | `age` and count columns cast to nullable integers, `signup_date` parsed to datetime, `discount_used` mapped from Yes/No to 1/0 | all |

**Result:** 61 rows in, 58 rows out, 0 missing values.

After the fixes, `purchase_count × avg_order_value` matches `total_spending` for every remaining row.

Five customers spend more than 10,000. Four have totals consistent with their order data and were **kept**, since they are genuine high spenders and not errors. The fifth (customer 1030) was the inconsistent record corrected above.

## Exploration

The notebook also visualizes the age distribution, customers by membership tier, city and payment method, the satisfaction score distribution, box plots of order value and total spending, and the top 10 customers by total spending.

## Limitations

- The dataset is small (58 clean rows), so any difference between groups may be due to chance.
- The imputed age (customer 1010) is an artificial value, not an observed one.
- Five customers have more returned items than purchases, which is impossible. They were kept because their spending columns are consistent, but their `returned_items` values should be treated as unreliable.
- `discount_used` is recorded per customer, not per purchase, so the effect of a discount on a specific order cannot be measured.
- First names and gender are not always consistent with each other (the data is synthetic), so they were not used for validation.

## How to Run

```bash
git clone https://github.com/Fatemenamdar20/project-01-data-cleaning-fatemenamdarlo.git
cd project-01-data-cleaning-fatemenamdarlo
pip install -r requirements.txt
jupyter notebook data_cleaning.ipynb
```

The notebook writes the cleaned data to `cleaned_data.csv`.

## Project Structure

```
.
├── data_cleaning.ipynb    # cleaning and exploration
├── First_Dataset.xlsx     # raw data
├── cleaned_data.csv       # cleaned output
├── requirements.txt
└── README.md
```

## Tools

Python, pandas, matplotlib, openpyxl