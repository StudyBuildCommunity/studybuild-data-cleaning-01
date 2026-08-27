# Project 01 - Data Cleaning

## معرفی پروژه

این پروژه مربوط به مرحله اول پاکسازی داده برای یک دیتاست مشتریان فروشگاه آنلاین است. هدف این مرحله بررسی کیفیت داده، شناسایی مشکلات، اصلاح موارد قابل دفاع، مستندسازی تصمیم ها و تولید یک نسخه تمیز و آماده تحلیل از دیتاست است.

## ساختار فایل ها

```text
project-01-data-cleaning-FatemehDehghan224/
├── clean_data_code/
│   ├── data_quality_assessment.py
│   ├── clean_missing_duplicates.py
│   ├── clean_returned_items.py
│   ├── clean_total_spending_outliers.py
│   └── clean_age_finalize.py
├── data/
│   ├── raw_dataset_FatemehDehghan224.xlsx
│   ├── cleaned_dataset_step1_FatemehDehghan224.xlsx
│   ├── cleaned_dataset_step2_FatemehDehghan224.xlsx
│   ├── cleaned_dataset_step3_FatemehDehghan224.xlsx
│   └── cleaned_dataset_FatemehDehghan224.xlsx
├── report/
│   ├── data_cleaning_documentation.md
│   ├── cleaning_step1_change_log.csv
│   ├── cleaning_step2_returned_items_change_log.csv
│   ├── cleaning_step3_total_spending_change_log.csv
│   ├── cleaning_step3_valid_total_spending_outliers.csv
│   └── cleaning_step4_age_change_log.csv
├── requirements.txt
└── README.md
```

## فایل های اصلی خروجی

- دیتاست خام نگهداری شده: `data/raw_dataset_FatemehDehghan224.xlsx`
- دیتاست نهایی تمیز شده: `data/cleaned_dataset_FatemehDehghan224.xlsx`
- مستندات کامل پاکسازی: `report/data_cleaning_documentation.md`

## ابزارها و کتابخانه ها

- Python
- pandas
- openpyxl
- matplotlib

نصب وابستگی ها:

```powershell
python -m pip install -r requirements.txt
```

## ترتیب اجرای کدها

```powershell
python clean_data_code\data_quality_assessment.py
python clean_data_code\clean_missing_duplicates.py
python clean_data_code\clean_returned_items.py
python clean_data_code\clean_total_spending_outliers.py
python clean_data_code\clean_age_finalize.py
```

## مشکلات شناسایی شده و تصمیم های پاکسازی

### 1. Missing Values

دو مقدار خالی پیدا شد:

- ستون `age`
- ستون `total_spending`

برای `age` مقدار خالی با median سن جایگزین شد، چون median برای داده عددی در برابر مقدارهای پرت مقاوم تر از mean است.

برای `total_spending` مقدار خالی با فرمول زیر محاسبه شد:

```text
total_spending = purchase_count * avg_order_value
```

دلیل این تصمیم این بود که `total_spending` یک ستون مشتق شده است و محاسبه مستقیم آن از ستون های مرتبط، دقیق تر از جایگزینی آماری است.

### 2. Duplicate Records

یک رکورد کاملا تکراری شناسایی شد. چون تمام ستون های دو ردیف یکسان بودند، فقط اولین رکورد نگه داشته شد و رکورد تکراری حذف شد.

### 3. ناسازگاری `returned_items > purchase_count`

در چند ردیف مقدار `returned_items` از `purchase_count` بیشتر بود. از نظر منطقی تعداد آیتم های برگشتی نمی تواند بیشتر از تعداد خرید باشد.

راه حل انتخاب شده:

```text
if returned_items > purchase_count:
    returned_items = purchase_count
```

این روش انتخاب شد چون قانون منطقی داده را حفظ می کند، کل رکورد را حذف نمی کند و مقدار اصلاح شده همیشه با همان ردیف سازگار است.

### 4. Outlierهای ستون `total_spending`

ستون `total_spending` با روش IQR بررسی شد. همه outlierها حذف یا cap نشدند، چون outlier بودن همیشه به معنی خطای داده نیست. برخی مشتریان واقعا خرید بالایی داشتند و این داده ها برای تحلیل فروش مهم هستند.

برای هر outlier، مقدار `total_spending` با فرمول زیر کنترل شد:

```text
total_spending = purchase_count * avg_order_value
```

فقط یک مقدار خطای واقعی داشت:

- `customer_id = 1030`
- مقدار قبلی `total_spending = 25000`
- مقدار اصلاح شده `total_spending = 4079.14`

outlierهای معتبر که با فرمول سازگار بودند، بدون تغییر نگه داشته شدند.

### 5. سن غیرمنطقی

یک مقدار سن غیرمنطقی وجود داشت:

```text
age = 145
```

این مقدار با median سن های معتبر جایگزین شد. سن معتبر در این پروژه به صورت بازه 13 تا 100 در نظر گرفته شد.

```text
if age < 13 or age > 100:
    age = median(valid ages)
```

## وضعیت دیتاست نهایی

پس از پاکسازی:

- Missing value وجود ندارد.
- رکورد duplicate کامل وجود ندارد.
- مقدار `returned_items > purchase_count` وجود ندارد.
- ناسازگاری فرمولی در `total_spending` وجود ندارد.
- تاریخ های `signup_date` قابل تبدیل به تاریخ هستند.
- ناسازگاری آشکار متنی مثل فاصله اضافی یا typo candidate پیدا نشد.
- outlierهای معتبر حفظ شدند و فقط خطاهای واقعی اصلاح شدند.

## تفاوت نسخه اولیه و نهایی

- تعداد ردیف ها از 61 به 60 رسید، چون یک رکورد کاملا تکراری حذف شد.
- مقدارهای missing در `age` و `total_spending` اصلاح شدند.
- مقدارهای غیرمنطقی در `returned_items` اصلاح شدند.
- خطای محاسباتی `total_spending` اصلاح شد.
- مقدار سن غیرمنطقی اصلاح شد.
- دیتاست خام در فایل جداگانه نگهداری شد و فایل نهایی با نام استاندارد پروژه ساخته شد.

## نکته درباره outlierها

در این پروژه outlierهای معتبر حذف نشدند، چون برخی از آن ها نشان دهنده مشتریان پرخرج هستند. حذف این داده ها می توانست تحلیل فروش و ارزش مشتریان را دچار خطا کند.
