from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_DATASET_PATH = PROJECT_ROOT / "data" / "cleaned_dataset_FatemehDehghan224.xlsx"
RAW_BACKUP_PATH = PROJECT_ROOT / "data" / "raw_dataset_FatemehDehghan224.xlsx"
INPUT_PATH = PROJECT_ROOT / "data" / "cleaned_dataset_step3_FatemehDehghan224.xlsx"
FINAL_OUTPUT_PATH = PROJECT_ROOT / "data" / "cleaned_dataset_FatemehDehghan224.xlsx"
REPORT_DIR = PROJECT_ROOT / "report"
DOCUMENTATION_PATH = REPORT_DIR / "data_cleaning_documentation.md"
CHANGE_LOG_PATH = REPORT_DIR / "cleaning_step4_age_change_log.csv"


def load_dataset() -> pd.DataFrame:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input dataset was not found: {INPUT_PATH}")
    return pd.read_excel(INPUT_PATH, sheet_name="customers")


def preserve_raw_dataset() -> None:
    if RAW_BACKUP_PATH.exists():
        return
    if not ORIGINAL_DATASET_PATH.exists():
        raise FileNotFoundError(f"Original dataset was not found: {ORIGINAL_DATASET_PATH}")
    shutil.copy2(ORIGINAL_DATASET_PATH, RAW_BACKUP_PATH)


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


def clean_invalid_age(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, float]:
    cleaned_df = df.copy()
    age = pd.to_numeric(cleaned_df["age"], errors="coerce")
    valid_age_mask = age.between(13, 100)
    invalid_age_mask = age.notna() & ~valid_age_mask
    median_age = float(age[valid_age_mask].median())

    changes = []
    for idx in cleaned_df.index[invalid_age_mask]:
        old_value = cleaned_df.at[idx, "age"]
        changes.append(
            {
                "step": "replace_invalid_age_with_valid_age_median",
                "excel_row_after_step3": idx + 2,
                "customer_id": cleaned_df.at[idx, "customer_id"],
                "old_age": old_value,
                "new_age": median_age,
                "median_rule": "median of valid ages between 13 and 100",
                "reason": "Age outside the valid human range was treated as a data-entry error and replaced with the valid-age median.",
            }
        )
        cleaned_df.at[idx, "age"] = median_age

    return cleaned_df, pd.DataFrame(changes), median_age


def append_documentation(
    *,
    change_log: pd.DataFrame,
    median_age: float,
    original_rows: int,
    cleaned_rows: int,
) -> None:
    section_marker = "## مرحله چهارم: اصلاح سن غیرمنطقی و ساخت خروجی نهایی"
    base_documentation = ""
    if DOCUMENTATION_PATH.exists():
        base_documentation = DOCUMENTATION_PATH.read_text(encoding="utf-8")
        if section_marker in base_documentation:
            base_documentation = base_documentation.split(section_marker)[0].rstrip()

    replacements = {
        "- سن غیرمنطقی مثل `age = 145` هنوز اصلاح نشده است.": "- سن غیرمنطقی مثل `age = 145` در مرحله چهارم با median سن های معتبر اصلاح شد.",
        "- outlierهای دیگر هنوز فقط شناسایی شده اند و برای اصلاح آن ها تصمیم نهایی گرفته نشده است.": "- outlierهای معتبر بررسی شدند؛ موارد واقعی و سازگار با منطق داده بدون تغییر نگه داشته شدند.",
        "- outlierها هنوز فقط شناسایی شده اند و برای اصلاح آن ها تصمیم نهایی گرفته نشده است.": "- outlierهای معتبر بررسی شدند؛ موارد واقعی و سازگار با منطق داده بدون تغییر نگه داشته شدند.",
    }
    for old_text, new_text in replacements.items():
        base_documentation = base_documentation.replace(old_text, new_text)

    change_table = dataframe_to_markdown(change_log)
    documentation = f"""
{section_marker}

تاریخ اجرا: {date.today().isoformat()}

فایل ورودی این مرحله: `data/cleaned_dataset_step3_FatemehDehghan224.xlsx`

فایل خروجی نهایی: `data/cleaned_dataset_FatemehDehghan224.xlsx`

فایل داده خام نگهداری شده: `data/raw_dataset_FatemehDehghan224.xlsx`

### شرح مشکل

در دیتاست یک مقدار سن غیرمنطقی وجود داشت:

```text
age = 145
```

سن 145 برای مشتری فروشگاه مقدار قابل قبول و منطقی نیست و به احتمال زیاد خطای ورود داده است.

### راه حل های بررسی شده

| راه حل | نتیجه |
| --- | --- |
| حذف کل ردیف | مناسب نیست، چون مشکل فقط در ستون `age` است و سایر اطلاعات مشتری برای تحلیل قابل استفاده هستند. |
| جایگزینی با mean | به دلیل وجود مقدار پرت، mean می تواند تحت تاثیر داده غیرمنطقی قرار بگیرد. |
| جایگزینی با median تمام سن ها | بهتر از mean است، اما اگر سن های غیرمعتبر داخل محاسبه باشند، همچنان ممکن است کمی تحت تاثیر خطا قرار بگیرد. |
| جایگزینی با median سن های معتبر | بهترین گزینه برای این دیتاست است، چون مقدار جایگزین از سن های منطقی بین 13 تا 100 محاسبه می شود. |

### تصمیم نهایی

روش انتخاب شده:

```text
valid_age = 13 <= age <= 100
invalid_age = age < 13 or age > 100

if invalid_age:
    age = median(valid_age)
```

مقدار median سن های معتبر در این دیتاست:

```text
median = {median_age:g}
```

### دلیل انتخاب

- `age` ستون عددی است و برای مقدارهای عددی، median در برابر outlier مقاوم تر از mean است.
- سن 145 خطای واضح داده است، اما بقیه ستون های همان ردیف قابل استفاده هستند؛ بنابراین حذف کل ردیف منطقی نیست.
- median فقط از سن های معتبر محاسبه شد تا مقدار جایگزین تحت تاثیر سن غیرمنطقی قرار نگیرد.

### لاگ تغییرات این مرحله

{change_table}

### خلاصه خروجی نهایی

| مورد | مقدار |
| --- | --- |
| تعداد ردیف های ورودی مرحله چهارم | {original_rows} |
| تعداد ردیف های خروجی نهایی | {cleaned_rows} |
| تعداد سن های غیرمنطقی اصلاح شده | {len(change_log)} |
| فایل نهایی | `data/cleaned_dataset_FatemehDehghan224.xlsx` |
| فایل خام نگهداری شده | `data/raw_dataset_FatemehDehghan224.xlsx` |
"""
    DOCUMENTATION_PATH.write_text(
        base_documentation.rstrip() + "\n\n" + documentation.lstrip(),
        encoding="utf-8",
    )


def write_outputs(cleaned_df: pd.DataFrame, change_log: pd.DataFrame) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_excel(FINAL_OUTPUT_PATH, sheet_name="customers", index=False)
    change_log.to_csv(CHANGE_LOG_PATH, index=False, encoding="utf-8-sig")


def main() -> None:
    preserve_raw_dataset()
    df = load_dataset()
    cleaned_df, change_log, median_age = clean_invalid_age(df)
    write_outputs(cleaned_df, change_log)
    append_documentation(
        change_log=change_log,
        median_age=median_age,
        original_rows=len(df),
        cleaned_rows=len(cleaned_df),
    )

    print("Step 4 cleaning and final export completed.")
    print(f"Invalid ages corrected: {len(change_log)}")
    print(f"Median valid age: {median_age:g}")
    print(f"Raw dataset backup: {RAW_BACKUP_PATH}")
    print(f"Final cleaned dataset: {FINAL_OUTPUT_PATH}")
    print(f"Documentation: {DOCUMENTATION_PATH}")
    print(f"Change log: {CHANGE_LOG_PATH}")


if __name__ == "__main__":
    main()
