# مستندات پاکسازی داده

تاریخ اجرا: 2026-08-26

فایل ورودی: `data/cleaned_dataset_FatemehDehghan224.xlsx`

فایل خروجی این مرحله: `data/cleaned_dataset_step1_FatemehDehghan224.xlsx`

این سند برای ثبت تصمیم های پاکسازی داده نوشته شده است. فرآیند پاکسازی به صورت مرحله ای انجام شد: ابتدا Missing Data و Duplicate Records اصلاح شدند، سپس ناسازگاری های منطقی، outlierهای ستون `total_spending`، و مقدار سن غیرمنطقی بررسی و اصلاح/مستندسازی شدند.

## خلاصه مرحله اول

| مورد | مقدار |
| --- | --- |
| تعداد ردیف های اولیه | 61 |
| تعداد ردیف های خروجی | 60 |
| تعداد مقدار خالی اصلاح شده در `age` | 1 |
| مقدار جایگزین `age` | median = 45 |
| تعداد مقدار خالی اصلاح شده در `total_spending` | 1 |
| تعداد ردیف duplicate حذف شده | 1 |

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

| step | excel_row | customer_id | column | old_value | new_value | reason |
| --- | --- | --- | --- | --- | --- | --- |
| fill_missing_age | 21 | 1020 | age |  | 45.0 | Missing age was replaced with the median age because median is robust for numeric demographic data. |
| fill_missing_total_spending | 41 | 1040 | total_spending |  | 1280.44 | Missing total_spending was recalculated from purchase_count * avg_order_value. |
| remove_full_duplicate_row | 62 | 1014 | all_columns | full duplicate row | removed | The full record was duplicated, so only the first occurrence was kept. |

## نکات باقی مانده برای مراحل بعدی

- سن غیرمنطقی مثل `age = 145` در مرحله چهارم با median سن های معتبر اصلاح شد.
- ناسازگاری `total_spending` برای مقدارهای غیرخالی در مرحله سوم بررسی شد؛ خطای فرمول اصلاح شد و outlierهای معتبر نگه داشته شدند.
- مواردی مثل `returned_items > purchase_count` در مرحله اول اصلاح نشده بودند و در مرحله دوم اصلاح شدند.
- outlierها فقط در مرحله assessment شناسایی شده اند و هنوز تصمیم پاکسازی برای آن ها گرفته نشده است.

## مرحله دوم: اصلاح ناسازگاری `returned_items > purchase_count`

تاریخ اجرا: 2026-08-26

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
| تعداد ردیف های ورودی مرحله دوم | 60 |
| تعداد ردیف های خروجی مرحله دوم | 60 |
| تعداد رکوردهای اصلاح شده | 6 |

### لاگ تغییرات این مرحله

| step | excel_row_before_step1_duplicate_removal | customer_id | purchase_count | old_returned_items | new_returned_items | reason |
| --- | --- | --- | --- | --- | --- | --- |
| cap_returned_items_to_purchase_count | 9 | 1008 | 3 | 8 | 3 | returned_items cannot be greater than purchase_count, so it was capped to the maximum valid value. |
| cap_returned_items_to_purchase_count | 16 | 1015 | 3 | 8 | 3 | returned_items cannot be greater than purchase_count, so it was capped to the maximum valid value. |
| cap_returned_items_to_purchase_count | 25 | 1024 | 0 | 2 | 0 | returned_items cannot be greater than purchase_count, so it was capped to the maximum valid value. |
| cap_returned_items_to_purchase_count | 30 | 1029 | 2 | 4 | 2 | returned_items cannot be greater than purchase_count, so it was capped to the maximum valid value. |
| cap_returned_items_to_purchase_count | 38 | 1037 | 1 | 7 | 1 | returned_items cannot be greater than purchase_count, so it was capped to the maximum valid value. |
| cap_returned_items_to_purchase_count | 57 | 1056 | 1 | 4 | 1 | returned_items cannot be greater than purchase_count, so it was capped to the maximum valid value. |

### موارد باقی مانده برای مراحل بعدی

- سن غیرمنطقی مثل `age = 145` در مرحله چهارم با median سن های معتبر اصلاح شد.
- ناسازگاری `total_spending` برای مقدارهای غیرخالی در مرحله سوم بررسی شد؛ خطای فرمول اصلاح شد و outlierهای معتبر نگه داشته شدند.
- outlierهای معتبر بررسی شدند؛ موارد واقعی و سازگار با منطق داده بدون تغییر نگه داشته شدند.

## مرحله سوم: بررسی outlierهای ستون `total_spending`

تاریخ اجرا: 2026-08-26

فایل ورودی این مرحله: `data/cleaned_dataset_step2_FatemehDehghan224.xlsx`

فایل خروجی این مرحله: `data/cleaned_dataset_step3_FatemehDehghan224.xlsx`

### شرح مشکل

در مرحله assessment ستون `total_spending` با روش IQR بررسی شد. طبق این روش، مقدارهای بزرگ تر از حد بالایی outlier محسوب می شوند. حدهای محاسبه شده برای این مرحله:

| معیار | مقدار |
| --- | --- |
| lower bound | -4120.64 |
| upper bound | 9979.82 |
| تعداد outlierهای `total_spending` | 5 |

نکته مهم این است که outlier بودن همیشه به معنی خطای داده نیست. در ستون `total_spending` ممکن است مشتریانی با خرید زیاد واقعا مبلغ بالایی داشته باشند. بنابراین قبل از اصلاح، هر outlier با رابطه اصلی ستون بررسی شد:

```text
total_spending = purchase_count * avg_order_value
```

### outlierهای شناسایی شده

| excel_row_after_step2 | customer_id | purchase_count | avg_order_value | total_spending | expected_total_spending | formula_difference |
| --- | --- | --- | --- | --- | --- | --- |
| 10 | 1009 | 34 | 341.63 | 11615.42 | 11615.42 | 0.0 |
| 13 | 1012 | 27 | 434.5 | 11731.5 | 11731.5 | 0.0 |
| 31 | 1030 | 26 | 156.89 | 25000.0 | 4079.14 | 20920.86 |
| 45 | 1044 | 33 | 434.98 | 14354.34 | 14354.34 | 0.0 |
| 58 | 1057 | 31 | 436.54 | 13532.74 | 13532.74 | 0.0 |

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

| step | excel_row_after_step2 | customer_id | purchase_count | avg_order_value | old_total_spending | new_total_spending | formula | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| correct_total_spending_formula_error | 31 | 1030 | 26 | 156.89 | 25000.0 | 4079.14 | purchase_count * avg_order_value | total_spending was an outlier and did not match the derived formula, so it was recalculated. |

### outlierهای معتبر که نگه داشته شدند

این رکوردها با وجود outlier بودن، با فرمول `purchase_count * avg_order_value` سازگار بودند؛ بنابراین تغییر نکردند:

| excel_row_after_step2 | customer_id | purchase_count | avg_order_value | total_spending | expected_total_spending | formula_difference |
| --- | --- | --- | --- | --- | --- | --- |
| 10 | 1009 | 34 | 341.63 | 11615.42 | 11615.42 | 0.0 |
| 13 | 1012 | 27 | 434.5 | 11731.5 | 11731.5 | 0.0 |
| 45 | 1044 | 33 | 434.98 | 14354.34 | 14354.34 | 0.0 |
| 58 | 1057 | 31 | 436.54 | 13532.74 | 13532.74 | 0.0 |

### خلاصه تغییرات این مرحله

| مورد | مقدار |
| --- | --- |
| تعداد ردیف های ورودی مرحله سوم | 60 |
| تعداد ردیف های خروجی مرحله سوم | 60 |
| تعداد outlierهای بررسی شده | 5 |
| تعداد مقدارهای اصلاح شده | 1 |
| تعداد outlierهای معتبر نگه داشته شده | 4 |

### موارد باقی مانده برای مراحل بعدی

- سن غیرمنطقی مثل `age = 145` در مرحله چهارم با median سن های معتبر اصلاح شد.
- outlierهای معتبر بررسی شدند؛ موارد واقعی و سازگار با منطق داده بدون تغییر نگه داشته شدند.

## مرحله چهارم: اصلاح سن غیرمنطقی و ساخت خروجی نهایی

تاریخ اجرا: 2026-08-27

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
median = 45
```

### دلیل انتخاب

- `age` ستون عددی است و برای مقدارهای عددی، median در برابر outlier مقاوم تر از mean است.
- سن 145 خطای واضح داده است، اما بقیه ستون های همان ردیف قابل استفاده هستند؛ بنابراین حذف کل ردیف منطقی نیست.
- median فقط از سن های معتبر محاسبه شد تا مقدار جایگزین تحت تاثیر سن غیرمنطقی قرار نگیرد.

### لاگ تغییرات این مرحله

| step | excel_row_after_step3 | customer_id | old_age | new_age | median_rule | reason |
| --- | --- | --- | --- | --- | --- | --- |
| replace_invalid_age_with_valid_age_median | 11 | 1010 | 145 | 45.0 | median of valid ages between 13 and 100 | Age outside the valid human range was treated as a data-entry error and replaced with the valid-age median. |

### خلاصه خروجی نهایی

| مورد | مقدار |
| --- | --- |
| تعداد ردیف های ورودی مرحله چهارم | 60 |
| تعداد ردیف های خروجی نهایی | 60 |
| تعداد سن های غیرمنطقی اصلاح شده | 1 |
| فایل نهایی | `data/cleaned_dataset_FatemehDehghan224.xlsx` |
| فایل خام نگهداری شده | `data/raw_dataset_FatemehDehghan224.xlsx` |
