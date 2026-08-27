from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "cleaned_dataset_FatemehDehghan224.xlsx"
OUTPUT_PATH = PROJECT_ROOT / "data" / "cleaned_dataset_step1_FatemehDehghan224.xlsx"
REPORT_DIR = PROJECT_ROOT / "report"
DOCUMENTATION_PATH = REPORT_DIR / "data_cleaning_documentation.md"
CHANGE_LOG_PATH = REPORT_DIR / "cleaning_step1_change_log.csv"


def load_dataset() -> pd.DataFrame:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input dataset was not found: {INPUT_PATH}")
    return pd.read_excel(INPUT_PATH, sheet_name="customers")


def add_change(
    changes: list[dict[str, object]],
    *,
    step: str,
    excel_row: int,
    customer_id: object,
    column: str,
    old_value: object,
    new_value: object,
    reason: str,
) -> None:
    changes.append(
        {
            "step": step,
            "excel_row": excel_row,
            "customer_id": customer_id,
            "column": column,
            "old_value": old_value,
            "new_value": new_value,
            "reason": reason,
        }
    )


def clean_missing_age(df: pd.DataFrame, changes: list[dict[str, object]]) -> float:
    age_median = float(pd.to_numeric(df["age"], errors="coerce").median())
    missing_age_mask = df["age"].isna()

    for idx in df.index[missing_age_mask]:
        add_change(
            changes,
            step="fill_missing_age",
            excel_row=idx + 2,
            customer_id=df.at[idx, "customer_id"],
            column="age",
            old_value=df.at[idx, "age"],
            new_value=age_median,
            reason="Missing age was replaced with the median age because median is robust for numeric demographic data.",
        )

    df.loc[missing_age_mask, "age"] = age_median
    return age_median


def clean_missing_total_spending(
    df: pd.DataFrame, changes: list[dict[str, object]]
) -> None:
    missing_total_mask = df["total_spending"].isna()
    calculated_total = (df["purchase_count"] * df["avg_order_value"]).round(2)

    for idx in df.index[missing_total_mask]:
        add_change(
            changes,
            step="fill_missing_total_spending",
            excel_row=idx + 2,
            customer_id=df.at[idx, "customer_id"],
            column="total_spending",
            old_value=df.at[idx, "total_spending"],
            new_value=calculated_total.at[idx],
            reason="Missing total_spending was recalculated from purchase_count * avg_order_value.",
        )

    df.loc[missing_total_mask, "total_spending"] = calculated_total[missing_total_mask]


def remove_full_duplicates(
    df: pd.DataFrame, changes: list[dict[str, object]]
) -> tuple[pd.DataFrame, int]:
    duplicate_mask = df.duplicated(keep="first")
    duplicate_count = int(duplicate_mask.sum())

    for idx in df.index[duplicate_mask]:
        add_change(
            changes,
            step="remove_full_duplicate_row",
            excel_row=idx + 2,
            customer_id=df.at[idx, "customer_id"],
            column="all_columns",
            old_value="full duplicate row",
            new_value="removed",
            reason="The full record was duplicated, so only the first occurrence was kept.",
        )

    cleaned = df.loc[~duplicate_mask].copy()
    return cleaned, duplicate_count


def write_outputs(df: pd.DataFrame, changes: list[dict[str, object]]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_excel(OUTPUT_PATH, sheet_name="customers", index=False)
    pd.DataFrame(changes).to_csv(CHANGE_LOG_PATH, index=False, encoding="utf-8-sig")


def write_documentation(
    *,
    original_rows: int,
    cleaned_rows: int,
    age_median: float,
    missing_age_count: int,
    missing_total_count: int,
    duplicate_count: int,
    changes: list[dict[str, object]],
) -> None:
    change_table = dataframe_to_markdown(pd.DataFrame(changes))
    content = f"""# مستندات پاکسازی داده

تاریخ اجرا: {date.today().isoformat()}

فایل ورودی: `data/cleaned_dataset_FatemehDehghan224.xlsx`

فایل خروجی این مرحله: `data/cleaned_dataset_step1_FatemehDehghan224.xlsx`

این سند برای ثبت تصمیم های پاکسازی داده نوشته شده است. در این مرحله فقط روی Missing Data و Duplicate Records کار شده و سایر مشکلات مثل outlierها، سن غیرمنطقی، ناسازگاری های منطقی دیگر و داده های متنی هنوز در مراحل بعدی بررسی/اصلاح می شوند.

## خلاصه مرحله اول

| مورد | مقدار |
| --- | --- |
| تعداد ردیف های اولیه | {original_rows} |
| تعداد ردیف های خروجی | {cleaned_rows} |
| تعداد مقدار خالی اصلاح شده در `age` | {missing_age_count} |
| مقدار جایگزین `age` | median = {age_median:g} |
| تعداد مقدار خالی اصلاح شده در `total_spending` | {missing_total_count} |
| تعداد ردیف duplicate حذف شده | {duplicate_count} |

## تصمیم های پاکسازی

### 1. Missing Value در ستون `age`

مشکل: یک مقدار خالی در ستون `age` وجود داشت.

راه حل: مقدار خالی با median ستون `age` جایگزین شد.

دلیل: ستون `age` عددی است و median نسبت به میانگین در برابر مقدارهای پرت مقاوم تر است. چون در همین دیتاست مقدار سن غیرمنطقی هم دیده شده، median انتخاب مناسب تری از mean است.

### 2. Missing Value در ستون `total_spending`

مشکل: یک مقدار خالی در ستون `total_spending` وجود داشت.

راه حل: مقدار خالی با رابطه زیر محاسبه شد:

```text
total_spending = purchase_count * avg_order_value
```

دلیل: `total_spending` یک ستون مشتق شده از تعداد خرید و میانگین مبلغ سفارش است؛ بنابراین محاسبه مجدد آن دقیق تر از جایگزینی آماری مثل mean یا median است.

### 3. Duplicate Records

مشکل: یک رکورد کاملا تکراری در دیتاست وجود داشت.

راه حل: از بین دو رکورد یکسان، اولین رکورد نگه داشته شد و رکورد تکراری بعدی حذف شد.

دلیل: وقتی تمام ستون های دو ردیف یکسان هستند، نگه داشتن هر دو باعث وزن دادن دوباره به همان مشتری در تحلیل می شود و نتایج آماری را خراب می کند.

## لاگ تغییرات ردیف به ردیف

{change_table}

## نکات باقی مانده برای مراحل بعدی

- سن غیرمنطقی مثل `age = 145` هنوز اصلاح نشده است.
- ناسازگاری `total_spending` برای مقدارهای غیرخالی هنوز اصلاح نشده است.
- مواردی مثل `returned_items > purchase_count` هنوز اصلاح نشده اند.
- outlierها فقط در مرحله assessment شناسایی شده اند و هنوز تصمیم پاکسازی برای آن ها گرفته نشده است.
"""
    DOCUMENTATION_PATH.write_text(content, encoding="utf-8")


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No changes were applied._"

    text_df = df.fillna("").astype(str)
    headers = list(text_df.columns)
    rows = text_df.values.tolist()

    def clean_cell(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")

    header = "| " + " | ".join(clean_cell(column) for column in headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(clean_cell(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def main() -> None:
    df = load_dataset()
    original_rows = len(df)
    changes: list[dict[str, object]] = []

    missing_age_count = int(df["age"].isna().sum())
    missing_total_count = int(df["total_spending"].isna().sum())

    age_median = clean_missing_age(df, changes)
    clean_missing_total_spending(df, changes)
    cleaned_df, duplicate_count = remove_full_duplicates(df, changes)

    write_outputs(cleaned_df, changes)
    write_documentation(
        original_rows=original_rows,
        cleaned_rows=len(cleaned_df),
        age_median=age_median,
        missing_age_count=missing_age_count,
        missing_total_count=missing_total_count,
        duplicate_count=duplicate_count,
        changes=changes,
    )

    print("Step 1 cleaning completed.")
    print(f"Input rows: {original_rows}")
    print(f"Output rows: {len(cleaned_df)}")
    print(f"Output dataset: {OUTPUT_PATH}")
    print(f"Documentation: {DOCUMENTATION_PATH}")
    print(f"Change log: {CHANGE_LOG_PATH}")


if __name__ == "__main__":
    main()
