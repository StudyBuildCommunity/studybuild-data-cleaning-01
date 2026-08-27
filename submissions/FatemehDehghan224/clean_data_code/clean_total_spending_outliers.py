from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "cleaned_dataset_step2_FatemehDehghan224.xlsx"
OUTPUT_PATH = PROJECT_ROOT / "data" / "cleaned_dataset_step3_FatemehDehghan224.xlsx"
REPORT_DIR = PROJECT_ROOT / "report"
DOCUMENTATION_PATH = REPORT_DIR / "data_cleaning_documentation.md"
CHANGE_LOG_PATH = REPORT_DIR / "cleaning_step3_total_spending_change_log.csv"
VALID_OUTLIERS_PATH = REPORT_DIR / "cleaning_step3_valid_total_spending_outliers.csv"


def load_dataset() -> pd.DataFrame:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input dataset was not found: {INPUT_PATH}")
    return pd.read_excel(INPUT_PATH, sheet_name="customers")


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"

    text_df = df.fillna("").astype(str)
    headers = list(text_df.columns)
    rows = text_df.values.tolist()

    def clean_cell(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")

    header = "| " + " | ".join(clean_cell(column) for column in headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(clean_cell(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def identify_total_spending_outliers(df: pd.DataFrame) -> tuple[pd.DataFrame, float, float]:
    total_spending = pd.to_numeric(df["total_spending"], errors="coerce")
    q1 = total_spending.quantile(0.25)
    q3 = total_spending.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outlier_mask = (total_spending < lower_bound) | (total_spending > upper_bound)
    outliers = df.loc[outlier_mask].copy()
    outliers.insert(0, "excel_row_after_step2", outliers.index + 2)
    outliers["expected_total_spending"] = (
        outliers["purchase_count"] * outliers["avg_order_value"]
    ).round(2)
    outliers["formula_difference"] = (
        outliers["total_spending"].round(2) - outliers["expected_total_spending"]
    ).round(2)
    outliers["iqr_lower_bound"] = round(lower_bound, 2)
    outliers["iqr_upper_bound"] = round(upper_bound, 2)

    return outliers, lower_bound, upper_bound


def clean_total_spending_formula_errors(
    df: pd.DataFrame, outliers: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cleaned_df = df.copy()
    formula_error_mask = outliers["formula_difference"].abs() > 0.01
    formula_errors = outliers.loc[formula_error_mask].copy()
    valid_outliers = outliers.loc[~formula_error_mask].copy()

    changes = []
    for _, row in formula_errors.iterrows():
        source_idx = int(row["excel_row_after_step2"]) - 2
        old_value = cleaned_df.at[source_idx, "total_spending"]
        new_value = row["expected_total_spending"]
        changes.append(
            {
                "step": "correct_total_spending_formula_error",
                "excel_row_after_step2": row["excel_row_after_step2"],
                "customer_id": row["customer_id"],
                "purchase_count": row["purchase_count"],
                "avg_order_value": row["avg_order_value"],
                "old_total_spending": old_value,
                "new_total_spending": new_value,
                "formula": "purchase_count * avg_order_value",
                "reason": "total_spending was an outlier and did not match the derived formula, so it was recalculated.",
            }
        )
        cleaned_df.at[source_idx, "total_spending"] = new_value

    change_log = pd.DataFrame(changes)
    return cleaned_df, change_log, valid_outliers


def append_documentation(
    *,
    outliers: pd.DataFrame,
    change_log: pd.DataFrame,
    valid_outliers: pd.DataFrame,
    lower_bound: float,
    upper_bound: float,
    original_rows: int,
    cleaned_rows: int,
) -> None:
    section_marker = "## مرحله سوم: بررسی outlierهای ستون `total_spending`"
    base_documentation = ""
    if DOCUMENTATION_PATH.exists():
        base_documentation = DOCUMENTATION_PATH.read_text(encoding="utf-8")
        if section_marker in base_documentation:
            base_documentation = base_documentation.split(section_marker)[0].rstrip()

    stale_line = "- ناسازگاری `total_spending` برای مقدارهای غیرخالی هنوز اصلاح نشده است."
    updated_line = "- ناسازگاری `total_spending` برای مقدارهای غیرخالی در مرحله سوم بررسی شد؛ خطای فرمول اصلاح شد و outlierهای معتبر نگه داشته شدند."
    base_documentation = base_documentation.replace(stale_line, updated_line)

    outlier_table = dataframe_to_markdown(
        outliers[
            [
                "excel_row_after_step2",
                "customer_id",
                "purchase_count",
                "avg_order_value",
                "total_spending",
                "expected_total_spending",
                "formula_difference",
            ]
        ]
    )
    change_table = dataframe_to_markdown(change_log)
    valid_outlier_table = dataframe_to_markdown(
        valid_outliers[
            [
                "excel_row_after_step2",
                "customer_id",
                "purchase_count",
                "avg_order_value",
                "total_spending",
                "expected_total_spending",
                "formula_difference",
            ]
        ]
    )

    documentation = f"""
{section_marker}

تاریخ اجرا: {date.today().isoformat()}

فایل ورودی این مرحله: `data/cleaned_dataset_step2_FatemehDehghan224.xlsx`

فایل خروجی این مرحله: `data/cleaned_dataset_step3_FatemehDehghan224.xlsx`

### شرح مشکل

در مرحله assessment ستون `total_spending` با روش IQR بررسی شد. طبق این روش، مقدارهای بزرگ تر از حد بالایی outlier محسوب می شوند. حدهای محاسبه شده برای این مرحله:

| معیار | مقدار |
| --- | --- |
| lower bound | {lower_bound:.2f} |
| upper bound | {upper_bound:.2f} |
| تعداد outlierهای `total_spending` | {len(outliers)} |

نکته مهم این است که outlier بودن همیشه به معنی خطای داده نیست. در ستون `total_spending` ممکن است مشتریانی با خرید زیاد واقعا مبلغ بالایی داشته باشند. بنابراین قبل از اصلاح، هر outlier با رابطه اصلی ستون بررسی شد:

```text
total_spending = purchase_count * avg_order_value
```

### outlierهای شناسایی شده

{outlier_table}

### راه حل های بررسی شده

| راه حل | نتیجه |
| --- | --- |
| حذف همه outlierها | مناسب نیست، چون مشتریان پرخرج از تحلیل فروش حذف می شوند و درآمد واقعی کمتر از مقدار واقعی نشان داده می شود. |
| cap کردن همه outlierها به حد بالایی IQR | مناسب نیست، چون مقدارهای واقعی مشتریان high-value را مصنوعی کاهش می دهد. |
| جایگزینی همه outlierها با median یا mean | مناسب نیست، چون ساختار فروش واقعی و رفتار مشتریان با خرید بالا را خراب می کند. |
| بررسی فرمول و اصلاح فقط مقدار ناسازگار | مناسب ترین روش است، چون بین outlier معتبر و خطای واقعی داده تفاوت می گذارد. |

### تصمیم نهایی

روش انتخاب شده:

```text
expected_total_spending = purchase_count * avg_order_value

if total_spending is an IQR outlier and total_spending != expected_total_spending:
    total_spending = expected_total_spending
else:
    keep total_spending unchanged
```

### دلیل انتخاب

این روش دقیق تر از حذف یا cap کردن همه outlierها است، چون:

- `total_spending` یک ستون مشتق شده است و می توان آن را با فرمول منطقی بررسی کرد.
- outlierهای معتبر می توانند نشان دهنده مشتریان پرخرج باشند و برای تحلیل فروش ارزشمند هستند.
- فقط رکوردی اصلاح می شود که هم outlier است و هم با فرمول ستون ناسازگار است.
- با این تصمیم، داده واقعی حفظ می شود و فقط خطای واضح ورود/محاسبه داده اصلاح می شود.

### تغییر اعمال شده

{change_table}

### outlierهای معتبر که نگه داشته شدند

این رکوردها با وجود outlier بودن، با فرمول `purchase_count * avg_order_value` سازگار بودند؛ بنابراین تغییر نکردند:

{valid_outlier_table}

### خلاصه تغییرات این مرحله

| مورد | مقدار |
| --- | --- |
| تعداد ردیف های ورودی مرحله سوم | {original_rows} |
| تعداد ردیف های خروجی مرحله سوم | {cleaned_rows} |
| تعداد outlierهای بررسی شده | {len(outliers)} |
| تعداد مقدارهای اصلاح شده | {len(change_log)} |
| تعداد outlierهای معتبر نگه داشته شده | {len(valid_outliers)} |

### موارد باقی مانده برای مراحل بعدی

- سن غیرمنطقی مثل `age = 145` هنوز اصلاح نشده است.
- outlierهای دیگر هنوز فقط شناسایی شده اند و برای اصلاح آن ها تصمیم نهایی گرفته نشده است.
"""
    DOCUMENTATION_PATH.write_text(
        base_documentation.rstrip() + "\n\n" + documentation.lstrip(),
        encoding="utf-8",
    )


def write_outputs(
    cleaned_df: pd.DataFrame, change_log: pd.DataFrame, valid_outliers: pd.DataFrame
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_excel(OUTPUT_PATH, sheet_name="customers", index=False)
    change_log.to_csv(CHANGE_LOG_PATH, index=False, encoding="utf-8-sig")
    valid_outliers.to_csv(VALID_OUTLIERS_PATH, index=False, encoding="utf-8-sig")


def main() -> None:
    df = load_dataset()
    outliers, lower_bound, upper_bound = identify_total_spending_outliers(df)
    cleaned_df, change_log, valid_outliers = clean_total_spending_formula_errors(
        df, outliers
    )
    write_outputs(cleaned_df, change_log, valid_outliers)
    append_documentation(
        outliers=outliers,
        change_log=change_log,
        valid_outliers=valid_outliers,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
        original_rows=len(df),
        cleaned_rows=len(cleaned_df),
    )

    print("Step 3 cleaning completed.")
    print(f"Total spending outliers checked: {len(outliers)}")
    print(f"Formula errors corrected: {len(change_log)}")
    print(f"Valid outliers kept: {len(valid_outliers)}")
    print(f"Output dataset: {OUTPUT_PATH}")
    print(f"Documentation: {DOCUMENTATION_PATH}")
    print(f"Change log: {CHANGE_LOG_PATH}")


if __name__ == "__main__":
    main()
