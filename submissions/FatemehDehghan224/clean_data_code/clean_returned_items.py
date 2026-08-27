from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "cleaned_dataset_step1_FatemehDehghan224.xlsx"
OUTPUT_PATH = PROJECT_ROOT / "data" / "cleaned_dataset_step2_FatemehDehghan224.xlsx"
REPORT_DIR = PROJECT_ROOT / "report"
DOCUMENTATION_PATH = REPORT_DIR / "data_cleaning_documentation.md"
CHANGE_LOG_PATH = REPORT_DIR / "cleaning_step2_returned_items_change_log.csv"


def load_dataset() -> pd.DataFrame:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input dataset was not found: {INPUT_PATH}")
    return pd.read_excel(INPUT_PATH, sheet_name="customers")


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


def cap_returned_items(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cleaned_df = df.copy()
    invalid_mask = cleaned_df["returned_items"] > cleaned_df["purchase_count"]
    changes = []

    for idx in cleaned_df.index[invalid_mask]:
        old_value = cleaned_df.at[idx, "returned_items"]
        new_value = cleaned_df.at[idx, "purchase_count"]
        changes.append(
            {
                "step": "cap_returned_items_to_purchase_count",
                "excel_row_before_step1_duplicate_removal": idx + 2,
                "customer_id": cleaned_df.at[idx, "customer_id"],
                "purchase_count": cleaned_df.at[idx, "purchase_count"],
                "old_returned_items": old_value,
                "new_returned_items": new_value,
                "reason": "returned_items cannot be greater than purchase_count, so it was capped to the maximum valid value.",
            }
        )
        cleaned_df.at[idx, "returned_items"] = new_value

    return cleaned_df, pd.DataFrame(changes)


def append_documentation(changes: pd.DataFrame, original_rows: int, cleaned_rows: int) -> None:
    change_table = dataframe_to_markdown(changes)
    section_marker = "## مرحله دوم: اصلاح ناسازگاری `returned_items > purchase_count`"
    base_documentation = ""
    if DOCUMENTATION_PATH.exists():
        base_documentation = DOCUMENTATION_PATH.read_text(encoding="utf-8")
        if section_marker in base_documentation:
            base_documentation = base_documentation.split(section_marker)[0].rstrip()

    documentation = f"""

{section_marker}

تاریخ اجرا: {date.today().isoformat()}

فایل ورودی این مرحله: `data/cleaned_dataset_step1_FatemehDehghan224.xlsx`

فایل خروجی این مرحله: `data/cleaned_dataset_step2_FatemehDehghan224.xlsx`

### شرح مشکل

در این مرحله ردیف هایی بررسی شدند که در آن ها مقدار `returned_items` از مقدار `purchase_count` بیشتر بود. از نظر منطقی تعداد آیتم های برگشتی نمی تواند بیشتر از تعداد خرید باشد؛ بنابراین این مقدارها برای تحلیل قابل اعتماد نیستند و باید اصلاح شوند.

### راه حل های بررسی شده

| راه حل | نتیجه |
| --- | --- |
| حذف کل ردیف | باعث از دست رفتن اطلاعات مفید مشتری مثل شهر، روش پرداخت، مبلغ خرید و رضایت مشتری می شود. چون مشکل فقط در یک ستون است، حذف کل ردیف انتخاب مناسبی نیست. |
| جایگزینی با `NaN` و سپس imputation | محافظه کارانه است، اما بعدا باید دوباره درباره مقدار جایگزین تصمیم بگیریم و ممکن است رابطه منطقی با `purchase_count` حفظ نشود. |
| جایگزینی با median ستون `returned_items` | ساده است، اما ممکن است برای مشتریانی با خرید کم دوباره مقدار غیرمنطقی تولید کند. مثلا median می تواند از `purchase_count` یک مشتری بیشتر باشد. |
| محدود کردن مقدار به `purchase_count` | قانون منطقی دیتاست را حفظ می کند و مقدار را به بیشترین مقدار مجاز تبدیل می کند. |

### تصمیم نهایی

روش انتخاب شده:

```text
if returned_items > purchase_count:
    returned_items = purchase_count
```

### دلیل انتخاب

این روش برای این دیتاست منطقی تر است، چون:

- قانون معتبر بودن داده را مستقیم اعمال می کند: `returned_items <= purchase_count`
- کل رکورد را حذف نمی کند و بقیه اطلاعات مشتری حفظ می شود.
- برخلاف median، مقدار جدید همیشه با `purchase_count` همان ردیف سازگار است.
- مقدار اصلاح شده بیشترین مقدار ممکن و مجاز برای تعداد برگشتی است؛ یعنی اصلاح بیش از حد انجام نمی دهد.

### خلاصه تغییرات این مرحله

| مورد | مقدار |
| --- | --- |
| تعداد ردیف های ورودی مرحله دوم | {original_rows} |
| تعداد ردیف های خروجی مرحله دوم | {cleaned_rows} |
| تعداد رکوردهای اصلاح شده | {len(changes)} |

### لاگ تغییرات این مرحله

{change_table}

### موارد باقی مانده برای مراحل بعدی

- سن غیرمنطقی مثل `age = 145` هنوز اصلاح نشده است.
- ناسازگاری `total_spending` برای مقدارهای غیرخالی هنوز اصلاح نشده است.
- outlierها هنوز فقط شناسایی شده اند و برای اصلاح آن ها تصمیم نهایی گرفته نشده است.
"""
    DOCUMENTATION_PATH.write_text(
        base_documentation.rstrip() + "\n\n" + documentation.lstrip(),
        encoding="utf-8",
    )


def write_outputs(cleaned_df: pd.DataFrame, changes: pd.DataFrame) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_excel(OUTPUT_PATH, sheet_name="customers", index=False)
    changes.to_csv(CHANGE_LOG_PATH, index=False, encoding="utf-8-sig")


def main() -> None:
    df = load_dataset()
    cleaned_df, changes = cap_returned_items(df)
    write_outputs(cleaned_df, changes)
    append_documentation(changes, original_rows=len(df), cleaned_rows=len(cleaned_df))

    print("Step 2 cleaning completed.")
    print(f"Rows changed: {len(changes)}")
    print(f"Output dataset: {OUTPUT_PATH}")
    print(f"Documentation: {DOCUMENTATION_PATH}")
    print(f"Change log: {CHANGE_LOG_PATH}")


if __name__ == "__main__":
    main()
