# Data dictionary and provenance

## Source
Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33
Dataset page: https://archive.ics.uci.edu/dataset/352/online+retail
Download: https://archive.ics.uci.edu/static/public/352/online+retail.zip
License: Creative Commons Attribution 4.0, https://creativecommons.org/licenses/by/4.0/
Retrieved: 2026-10-13. The original workbook is supplied, unchanged in content, as data/raw/Online_Retail.xlsx. UCI's metadata describes 6 features plus two IDs; the workbook has 8 columns. The measured file has missing values despite the catalogue's no-missing label.

## Original workbook / cleaned transactions
| Column | Type | Meaning |
|---|---|---|
| InvoiceNo | nominal ID | Invoice identifier; C prefix indicates cancellation |
| StockCode | nominal ID | Product identifier; rule used for merchandise is explicitly recorded |
| Description | text | Product description |
| Quantity | integer | Item count on this line |
| InvoiceDate | timestamp | Invoice creation time, used without inferred timezone conversion |
| UnitPrice | numeric | GBP per item |
| CustomerID | nominal ID | Linkage key, never a quantitative predictor |
| Country | nominal | Customer country |
| LineValue | derived numeric | Quantity x UnitPrice, gross GBP |
| Day | derived calendar date | Date component of InvoiceDate |

Cleaned rows are sequentially deduplicated, positive-price/quantity non-C purchases, identified customers, then product codes matching five digits plus zero to two letters. Original workbook is preserved; removed rows are not irrecoverably deleted from the package.

## uk_shopping_days.csv
One row per CustomerID and Day, restricted to Country == United Kingdom.
- breadth: number of distinct eligible StockCodes across all invoices that day.
- spend: sum of LineValue, GBP.
- units: sum of Quantity.
- invoices: number of distinct InvoiceNo values.

## customer_cohort.csv
One row per eligible customer (first observed UK shopping day 2011-01-01 through 2011-08-31).
- CustomerID: source linkage key.
- index_day: earliest eligible UK shopping day anywhere in the observed source.
- first_breadth, first_spend, first_units, first_invoices: basket attributes on index_day.
- spend90: total eligible UK gross merchandise spend on calendar days 1-90 after index_day; zero for no observed purchase.
- days90: number of distinct later UK shopping days in that window.
- second_day, second_breadth: earliest later UK shopping day within the window and its variety; missing for non-returners, never imputed.
- repeat90: 1 if days90 > 0, otherwise 0.
- broad: 1 if first_breadth >= 10, otherwise 0.
- log_spend90: natural log of (1 + numerical spend90 in GBP).
- month: calendar month of index_day.
- return_gap_days: calendar days from index_day to second_day; 1-90 for
  returners, missing for non-returners. Used only for the conditional T4 test.

T5 uses first_breadth and days90 among repeat90 == 1. days90 includes the first
return and any later shopping days within days 1-90 of the original index date;
it never includes the index day and is not a rate per day after the first return.

## Statistical output fields
- T1: estimate is broad-minus-narrow return probability, stored as a proportion.
- T2: estimate is the broad-minus-narrow mean of natural log(1 + spend90 in GBP).
- T3: estimate is mean second-minus-first breadth in SKUs among returners.
- T4: estimate is broad-minus-narrow mean return_gap_days among returners.
- T5: statistic and estimate are Spearman rho among returners. approx_t is the
  large-sample reference statistic; df = 876 belongs to that t approximation,
  not an exact rank distribution.
- p: unadjusted, two-sided p-value. holm_p: adjustment across the five main tests.
- ci_low and ci_high in hypothesis_tests.csv: marginal 95% limits. T5 uses a
  paired-customer percentile bootstrap; T1 uses Newcombe-Wilson, T2/T4 Welch,
  and T3 paired t. JSON stores intervals as two-element arrays.
- The T5 CI is null in diagnostic sensitivity records because those variants do
  not rerun its bootstrap; the main T5 CI is populated. This is not a missing
  main analysis result.

## encoded_transactions.npz and encoded_columns.json
CSR sparse matrix, 391,150 rows x 60 columns. Row order equals clean_transactions.csv.gz. The JSON gives exact column order.
- Four numerical columns: Quantity, UnitPrice, LineValue, Hour.
- 37 Country indicators.
- 13 YearMonth indicators.
- 6 observed Weekday indicators (no artificial Saturday column).
Full one-hot groups are an encoding/size artifact, not a regression design with an intercept. Do not fit a full-rank linear model on all dummy columns plus an intercept without dropping reference levels.
Identifiers and Description remain in the separate cleaned file. No SKU/Invoice/Customer dummy expansion is used.
