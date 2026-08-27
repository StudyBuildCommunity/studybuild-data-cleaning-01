from __future__ import annotations

import itertools
import os
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".matplotlib_cache"))

import matplotlib.pyplot as plt
import pandas as pd
from pandas.api.types import is_numeric_dtype


DATA_PATH = PROJECT_ROOT / "data" / "cleaned_dataset_FatemehDehghan224.xlsx"
OUTPUT_DIR = PROJECT_ROOT / "report" / "data_quality_assessment"
CHARTS_DIR = OUTPUT_DIR / "charts"


EXPECTED_SCHEMA = {
    "customer_id": "integer",
    "first_name": "text",
    "gender": "category",
    "age": "numeric",
    "city": "text",
    "province": "text",
    "signup_date": "date",
    "membership_tier": "category",
    "purchase_count": "integer",
    "avg_order_value": "numeric",
    "total_spending": "numeric",
    "last_purchase_days": "integer",
    "payment_method": "category",
    "device": "category",
    "discount_used": "category",
    "returned_items": "integer",
    "satisfaction_score": "integer",
}

ALLOWED_VALUES = {
    "gender": {"M", "F"},
    "membership_tier": {"Bronze", "Silver", "Gold", "VIP"},
    "payment_method": {"Card", "Cash", "Online Wallet"},
    "device": {"Android", "iPhone", "Web"},
    "discount_used": {"Yes", "No"},
}


def ensure_output_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)


def load_dataset() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    try:
        return pd.read_excel(DATA_PATH, sheet_name="customers")
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency for reading Excel files. Run:\n"
            "python -m pip install -r requirements.txt"
        ) from exc


def add_excel_row(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result.insert(0, "excel_row", result.index + 2)
    return result


def save_csv(df: pd.DataFrame, filename: str) -> None:
    df.to_csv(OUTPUT_DIR / filename, index=False, encoding="utf-8-sig")


def summarize_basic_info(df: pd.DataFrame) -> pd.DataFrame:
    info = pd.DataFrame(
        {
            "column": df.columns,
            "dtype": [str(dtype) for dtype in df.dtypes],
            "non_null_count": [int(df[col].notna().sum()) for col in df.columns],
            "null_count": [int(df[col].isna().sum()) for col in df.columns],
            "unique_count": [int(df[col].nunique(dropna=False)) for col in df.columns],
        }
    )
    save_csv(info, "01_basic_column_info.csv")
    return info


def check_missing_values(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    missing_summary = (
        df.isna()
        .sum()
        .rename("missing_count")
        .reset_index()
        .rename(columns={"index": "column"})
    )
    missing_summary["missing_percent"] = (
        missing_summary["missing_count"] / len(df) * 100
    ).round(2)
    missing_summary = missing_summary.sort_values(
        ["missing_count", "column"], ascending=[False, True]
    )

    missing_rows = add_excel_row(df[df.isna().any(axis=1)])

    save_csv(missing_summary, "02_missing_values_summary.csv")
    save_csv(missing_rows, "02_rows_with_missing_values.csv")
    return missing_summary, missing_rows


def check_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    duplicate_rows = add_excel_row(df[df.duplicated(keep=False)]).sort_values(
        list(df.columns)
    )

    duplicate_keys = pd.DataFrame()
    if "customer_id" in df.columns:
        duplicate_keys = add_excel_row(
            df[df.duplicated(subset=["customer_id"], keep=False)]
        ).sort_values("customer_id")

    save_csv(duplicate_rows, "03_duplicate_full_rows.csv")
    save_csv(duplicate_keys, "03_duplicate_customer_ids.csv")
    return duplicate_rows, duplicate_keys


def _invalid_type_mask(series: pd.Series, expected_type: str) -> pd.Series:
    non_missing = series.notna()

    if expected_type in {"integer", "numeric"}:
        converted = pd.to_numeric(series, errors="coerce")
        invalid = non_missing & converted.isna()
        if expected_type == "integer":
            invalid = invalid | (non_missing & converted.notna() & (converted % 1 != 0))
        return invalid

    if expected_type == "date":
        converted = pd.to_datetime(series, errors="coerce")
        return non_missing & converted.isna()

    if expected_type in {"text", "category"}:
        return non_missing & ~series.map(lambda value: isinstance(value, str))

    return pd.Series(False, index=series.index)


def check_data_types(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    type_summary_rows = []
    invalid_rows = []

    for column, expected_type in EXPECTED_SCHEMA.items():
        if column not in df.columns:
            type_summary_rows.append(
                {
                    "column": column,
                    "expected_type": expected_type,
                    "actual_dtype": "missing_column",
                    "invalid_value_count": None,
                }
            )
            continue

        invalid_mask = _invalid_type_mask(df[column], expected_type)
        type_summary_rows.append(
            {
                "column": column,
                "expected_type": expected_type,
                "actual_dtype": str(df[column].dtype),
                "invalid_value_count": int(invalid_mask.sum()),
            }
        )

        for idx, value in df.loc[invalid_mask, column].items():
            invalid_rows.append(
                {
                    "excel_row": idx + 2,
                    "column": column,
                    "value": value,
                    "expected_type": expected_type,
                    "actual_python_type": type(value).__name__,
                }
            )

    type_summary = pd.DataFrame(type_summary_rows)
    invalid_type_values = pd.DataFrame(invalid_rows)

    save_csv(type_summary, "04_data_type_summary.csv")
    save_csv(invalid_type_values, "04_invalid_type_values.csv")
    return type_summary, invalid_type_values


def check_invalid_values(df: pd.DataFrame) -> pd.DataFrame:
    issues = []

    def add_issue(mask: pd.Series, column: str, issue: str, expected: str) -> None:
        for idx, value in df.loc[mask, column].items():
            customer_id = df.at[idx, "customer_id"] if "customer_id" in df.columns else None
            issues.append(
                {
                    "excel_row": idx + 2,
                    "customer_id": customer_id,
                    "column": column,
                    "value": value,
                    "issue": issue,
                    "expected": expected,
                }
            )

    numeric_columns = [
        "age",
        "purchase_count",
        "avg_order_value",
        "total_spending",
        "last_purchase_days",
        "returned_items",
        "satisfaction_score",
    ]
    numeric = {
        column: pd.to_numeric(df[column], errors="coerce")
        for column in numeric_columns
        if column in df.columns
    }

    if "age" in numeric:
        add_issue(numeric["age"].notna() & ~numeric["age"].between(13, 100), "age", "unrealistic_age", "13 to 100")

    for column in ["purchase_count", "avg_order_value", "total_spending", "last_purchase_days", "returned_items"]:
        if column in numeric:
            add_issue(numeric[column].notna() & (numeric[column] < 0), column, "negative_value", ">= 0")

    for column in ["purchase_count", "last_purchase_days", "returned_items", "satisfaction_score"]:
        if column in numeric:
            add_issue(numeric[column].notna() & (numeric[column] % 1 != 0), column, "non_integer_value", "integer")

    if "satisfaction_score" in numeric:
        add_issue(
            numeric["satisfaction_score"].notna() & ~numeric["satisfaction_score"].between(1, 5),
            "satisfaction_score",
            "score_out_of_range",
            "1 to 5",
        )

    if {"returned_items", "purchase_count"}.issubset(numeric):
        mask = (
            numeric["returned_items"].notna()
            & numeric["purchase_count"].notna()
            & (numeric["returned_items"] > numeric["purchase_count"])
        )
        add_issue(mask, "returned_items", "returned_items_greater_than_purchase_count", "<= purchase_count")

    if {"total_spending", "purchase_count", "avg_order_value"}.issubset(numeric):
        expected_total = (numeric["purchase_count"] * numeric["avg_order_value"]).round(2)
        actual_total = numeric["total_spending"].round(2)
        mask = actual_total.notna() & expected_total.notna() & ((actual_total - expected_total).abs() > 0.01)
        for idx in df.index[mask]:
            issues.append(
                {
                    "excel_row": idx + 2,
                    "customer_id": df.at[idx, "customer_id"] if "customer_id" in df.columns else None,
                    "column": "total_spending",
                    "value": df.at[idx, "total_spending"],
                    "issue": "total_spending_formula_mismatch",
                    "expected": f"purchase_count * avg_order_value = {expected_total.at[idx]}",
                }
            )

    if "signup_date" in df.columns:
        parsed_dates = pd.to_datetime(df["signup_date"], errors="coerce")
        add_issue(parsed_dates.isna() & df["signup_date"].notna(), "signup_date", "invalid_date", "valid date")
        add_issue(parsed_dates.dt.date > date.today(), "signup_date", "future_date", "<= today")

    for column, allowed in ALLOWED_VALUES.items():
        if column in df.columns:
            mask = df[column].notna() & ~df[column].isin(allowed)
            add_issue(mask, column, "unexpected_category", ", ".join(sorted(allowed)))

    invalid_values = pd.DataFrame(
        issues,
        columns=["excel_row", "customer_id", "column", "value", "issue", "expected"],
    )
    if not invalid_values.empty:
        invalid_values = invalid_values.sort_values(
            ["excel_row", "column"], ignore_index=True
        )
    save_csv(invalid_values, "05_invalid_logical_values.csv")
    return invalid_values


def normalize_text(value: object) -> object:
    if not isinstance(value, str):
        return value
    return " ".join(value.strip().split()).casefold()


def check_text_inconsistencies(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    text_columns = [column for column in df.columns if df[column].dtype == "object"]
    whitespace_issues = []
    normalized_groups = []
    fuzzy_pairs = []

    for column in text_columns:
        series = df[column].dropna()

        for idx, value in series.items():
            if isinstance(value, str):
                stripped = value.strip()
                collapsed = " ".join(stripped.split())
                if value != stripped or value != collapsed:
                    whitespace_issues.append(
                        {
                            "excel_row": idx + 2,
                            "column": column,
                            "value": value,
                            "suggested_value": collapsed,
                        }
                    )

        values = sorted({value for value in series if isinstance(value, str)})
        grouped = {}
        for value in values:
            grouped.setdefault(normalize_text(value), []).append(value)

        for normalized, originals in grouped.items():
            if len(originals) > 1:
                normalized_groups.append(
                    {
                        "column": column,
                        "normalized_value": normalized,
                        "original_values": " | ".join(originals),
                    }
                )

        # Simple typo candidate detection for low-cardinality text columns.
        if len(values) <= 50:
            for left, right in itertools.combinations(values, 2):
                if left.casefold() == right.casefold():
                    continue
                similarity = _similarity(left, right)
                if 0.84 <= similarity < 1:
                    fuzzy_pairs.append(
                        {
                            "column": column,
                            "value_1": left,
                            "value_2": right,
                            "similarity": round(similarity, 3),
                        }
                    )

    whitespace_df = pd.DataFrame(whitespace_issues)
    normalized_df = pd.DataFrame(normalized_groups)
    fuzzy_df = pd.DataFrame(
        fuzzy_pairs, columns=["column", "value_1", "value_2", "similarity"]
    )
    if not fuzzy_df.empty:
        fuzzy_df = fuzzy_df.sort_values(
            ["column", "similarity"], ascending=[True, False], ignore_index=True
        )

    save_csv(whitespace_df, "06_text_whitespace_issues.csv")
    save_csv(normalized_df, "06_text_case_space_groups.csv")
    save_csv(fuzzy_df, "06_text_possible_typos.csv")
    return whitespace_df, normalized_df, fuzzy_df


def _similarity(left: str, right: str) -> float:
    from difflib import SequenceMatcher

    return SequenceMatcher(None, left.casefold(), right.casefold()).ratio()


def check_outliers(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    numeric_columns = [
        column
        for column in df.columns
        if is_numeric_dtype(df[column]) and column != "customer_id"
    ]
    summary_rows = []
    outlier_rows = []

    for column in numeric_columns:
        values = pd.to_numeric(df[column], errors="coerce").dropna()
        if values.empty:
            continue

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        mask = df[column].notna() & (
            (df[column] < lower_bound) | (df[column] > upper_bound)
        )

        summary_rows.append(
            {
                "column": column,
                "q1": round(q1, 4),
                "q3": round(q3, 4),
                "iqr": round(iqr, 4),
                "lower_bound": round(lower_bound, 4),
                "upper_bound": round(upper_bound, 4),
                "outlier_count": int(mask.sum()),
                "outlier_percent": round(mask.sum() / len(df) * 100, 2),
            }
        )

        for idx, value in df.loc[mask, column].items():
            outlier_rows.append(
                {
                    "excel_row": idx + 2,
                    "customer_id": df.at[idx, "customer_id"] if "customer_id" in df.columns else None,
                    "column": column,
                    "value": value,
                    "lower_bound": round(lower_bound, 4),
                    "upper_bound": round(upper_bound, 4),
                }
            )

        plot_outlier_charts(df, column, lower_bound, upper_bound)

    outlier_summary = pd.DataFrame(summary_rows)
    outlier_values = pd.DataFrame(
        outlier_rows,
        columns=[
            "excel_row",
            "customer_id",
            "column",
            "value",
            "lower_bound",
            "upper_bound",
        ],
    )
    if not outlier_values.empty:
        outlier_values = outlier_values.sort_values(
            ["column", "excel_row"], ignore_index=True
        )

    save_csv(outlier_summary, "07_outlier_summary_iqr.csv")
    save_csv(outlier_values, "07_outlier_rows_iqr.csv")
    return outlier_summary, outlier_values


def plot_outlier_charts(
    df: pd.DataFrame, column: str, lower_bound: float, upper_bound: float
) -> None:
    values = pd.to_numeric(df[column], errors="coerce").dropna()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].hist(values, bins="auto", edgecolor="black", color="#4c78a8")
    axes[0].axvline(lower_bound, color="#d62728", linestyle="--", linewidth=1)
    axes[0].axvline(upper_bound, color="#d62728", linestyle="--", linewidth=1)
    axes[0].set_title(f"Histogram - {column}")
    axes[0].set_xlabel(column)
    axes[0].set_ylabel("Frequency")

    axes[1].boxplot(values, orientation="vertical", patch_artist=True)
    axes[1].set_title(f"Boxplot - {column}")
    axes[1].set_ylabel(column)

    fig.tight_layout()
    fig.savefig(CHARTS_DIR / f"{column}_histogram_boxplot.png", dpi=150)
    plt.close(fig)


def write_markdown_report(
    df: pd.DataFrame,
    basic_info: pd.DataFrame,
    missing_summary: pd.DataFrame,
    missing_rows: pd.DataFrame,
    duplicate_rows: pd.DataFrame,
    duplicate_keys: pd.DataFrame,
    type_summary: pd.DataFrame,
    invalid_type_values: pd.DataFrame,
    invalid_values: pd.DataFrame,
    whitespace_df: pd.DataFrame,
    normalized_df: pd.DataFrame,
    fuzzy_df: pd.DataFrame,
    outlier_summary: pd.DataFrame,
    outlier_values: pd.DataFrame,
) -> None:
    report_path = OUTPUT_DIR / "data_quality_assessment_report.md"
    lines = [
        "# Data Quality Assessment",
        "",
        f"Source file: `{DATA_PATH.relative_to(PROJECT_ROOT)}`",
        f"Rows: {len(df)}",
        f"Columns: {len(df.columns)}",
        "",
        "## Checks",
        "",
        f"- Missing value columns: {(missing_summary['missing_count'] > 0).sum()}",
        f"- Rows with missing values: {len(missing_rows)}",
        f"- Full duplicate rows: {len(duplicate_rows)}",
        f"- Duplicate customer_id rows: {len(duplicate_keys)}",
        f"- Invalid type values: {len(invalid_type_values)}",
        f"- Invalid logical values: {len(invalid_values)}",
        f"- Text whitespace issues: {len(whitespace_df)}",
        f"- Text normalized duplicate groups: {len(normalized_df)}",
        f"- Possible text typo pairs: {len(fuzzy_df)}",
        f"- IQR outlier values: {len(outlier_values)}",
        "",
        "## Generated Files",
        "",
        "- `01_basic_column_info.csv`",
        "- `02_missing_values_summary.csv`",
        "- `02_rows_with_missing_values.csv`",
        "- `03_duplicate_full_rows.csv`",
        "- `03_duplicate_customer_ids.csv`",
        "- `04_data_type_summary.csv`",
        "- `04_invalid_type_values.csv`",
        "- `05_invalid_logical_values.csv`",
        "- `06_text_whitespace_issues.csv`",
        "- `06_text_case_space_groups.csv`",
        "- `06_text_possible_typos.csv`",
        "- `07_outlier_summary_iqr.csv`",
        "- `07_outlier_rows_iqr.csv`",
        "- `charts/*.png`",
        "",
        "## Notes For Cleaning Phase",
        "",
        "This script only identifies data quality problems. It does not modify or clean the dataset.",
        "Use the generated CSV files to decide how each issue should be handled in the next phase.",
        "",
    ]

    if not basic_info.empty:
        lines.extend(["## Columns", "", dataframe_to_markdown(basic_info), ""])
    if not missing_summary.empty:
        lines.extend(["## Missing Values", "", dataframe_to_markdown(missing_summary), ""])
    if not outlier_summary.empty:
        lines.extend(["## Outlier Summary", "", dataframe_to_markdown(outlier_summary), ""])

    report_path.write_text("\n".join(lines), encoding="utf-8")


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return ""

    text_df = df.fillna("").astype(str)
    headers = list(text_df.columns)
    rows = text_df.values.tolist()

    def clean_cell(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")

    header_line = "| " + " | ".join(clean_cell(column) for column in headers) + " |"
    separator_line = "| " + " | ".join("---" for _ in headers) + " |"
    body_lines = [
        "| " + " | ".join(clean_cell(cell) for cell in row) + " |" for row in rows
    ]
    return "\n".join([header_line, separator_line, *body_lines])


def main() -> None:
    ensure_output_dirs()
    df = load_dataset()

    basic_info = summarize_basic_info(df)
    missing_summary, missing_rows = check_missing_values(df)
    duplicate_rows, duplicate_keys = check_duplicates(df)
    type_summary, invalid_type_values = check_data_types(df)
    invalid_values = check_invalid_values(df)
    whitespace_df, normalized_df, fuzzy_df = check_text_inconsistencies(df)
    outlier_summary, outlier_values = check_outliers(df)

    write_markdown_report(
        df,
        basic_info,
        missing_summary,
        missing_rows,
        duplicate_rows,
        duplicate_keys,
        type_summary,
        invalid_type_values,
        invalid_values,
        whitespace_df,
        normalized_df,
        fuzzy_df,
        outlier_summary,
        outlier_values,
    )

    print("Data quality assessment completed.")
    print(f"Input: {DATA_PATH}")
    print(f"Output folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise
