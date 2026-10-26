# Analysis plan fixed before inferential results
Date: 2026-10-13. This is a prospective specification within this analysis, not an externally registered study.

Problem: Does variety in a customer's first observed UK shopping-day basket indicate subsequent 90-day repurchase and spending? Among customers who repurchase, does variety change at their second shopping day?

- Primary unit: customer; transactional source unit: invoice line. Combine a customer's invoices on the same calendar day into a shopping-day basket to avoid counting split invoices as return visits.
- Retain positive-price, positive-quantity, non-cancellation merchandise records with known CustomerID. Product-code eligibility: five digits followed by zero to two letters (case insensitive). Deduplicate exact source rows in main analysis; retain them in a sensitivity run.
- No imputation of customer identities, monetary outcomes or nonpurchase outcomes. Zero subsequent spend means no observed eligible purchase in the window, not a missing value.
- All cleaned transactions are retained for the encoded-size calculation, including non-UK records. Inference uses UK shopping activity only.
- Cohort: first observed eligible UK shopping day in 2011-01-01 through 2011-08-31. The December 2010 portion provides an observed washout, not proof of genuinely new customers. Follow up for 90 calendar days after index date; exclude index day. There is complete follow-up through 2011-11-29.
- Broad: at least 10 distinct StockCodes on index day; narrow: 1-9. Threshold is a simple operational segmentation choice, not claimed as an industry standard or chosen by p-value. Sensitivity: thresholds 5 and 15, reported regardless of outcome.
- T1 primary: Pearson 2x2 independence test, without continuity correction; H0 p_broad-p_narrow=0, H1 !=0. Estimate risk difference with Newcombe-Wilson 95% CI. Smallest important difference: 5 percentage points (50 additional returning customers per 1,000); analyst-proposed, not validated business economics.
- T2 secondary: Welch t-test of log(1 + subsequent gross merchandise spend measured in GBP), broad minus narrow; H0 mean difference=0, H1 !=0. 95% Welch CI and exponentiation to geometric-mean ratio of (1+spend). Important ratio: >=1.20 or <=1/1.20. This is not a ratio of arithmetic mean revenue. Also report raw pound means.
- T3 secondary: paired t-test of second-day minus first-day distinct SKUs, only customers with a later shopping day within 90 days. H0 mean paired change=0, H1 !=0; 95% paired CI. Important absolute change: 2 SKUs. Do not extend this conditional result to non-returners.
- Alpha .05; all tests two-sided. Holm correction across three primary/secondary p-values. Report raw and adjusted values. 95% CIs are marginal, not simultaneous.
- Sensitivities: duplicate retention; alternative breadth cutoffs; customer bootstrap CIs (5,000 resamples, seed 558); pooled t, raw-spend Welch, Fisher exact, paired rank/sign comparisons; HC3 linear-probability adjustment of repurchase on breadth, log(1+initial spend), log(1+initial units), index-month indicators. Sensitivity p-values are diagnostic, not extra confirmatory discoveries.
- Real large orders are retained. IQR flags describe tails, not automatic evidence of errors. No arbitrary revenue clipping in main tests.
- Interpret association, never causation. This historical single-retailer sample cannot establish current-market effectiveness of a retention intervention.

## Extension fixed on 25 October 2026, before running T4 and T5

The original three-test specification above is retained as historical context.
The following two secondary questions were designed after reviewing T1-T3, not
before the whole dataset was examined. They are not an external preregistration.
The final report uses five main tests, as permitted by the professor's guidelines.

- Preserve the original cleaning, cohort, 90-day follow-up and breadth definition.
- T4: among the 878 observed returners, compare mean calendar days from index_day
  to second_day between broad and narrow first baskets. H0: mean_B - mean_N = 0;
  H1: not equal to 0. Use two-sided Welch t, a marginal 95% Welch CI, and an
  analyst-proposed practically important absolute gap of 7 days. Missing return
  dates for non-returners remain missing; never assign a fictitious return time.
- T5: among the same returners, test Spearman rank correlation between numeric
  first_breadth and days90. H0: rho_s = 0; H1: rho_s != 0. Use average ranks for
  ties, a two-sided large-sample p-value, and a marginal percentile bootstrap
  95% CI. Report rho, n, and the approximate t statistic with df = n - 2. A
  proposed magnitude of interest is |rho_s| >= 0.10, an analytical threshold,
  not a validated commercial standard or a percentage increase in visits.
- Correct the five main p-values together using Holm, at family alpha 0.05.
  Report marginal CIs separately from the multiplicity-adjusted decisions.
  Diagnostic tests do not become extra confirmatory discoveries.
- T4 robustness: Mann-Whitney ordering comparison; 5,000 customer bootstrap
  resamples separately within broad/narrow groups, seed 5584; cutoffs 5 and 15.
- T5 robustness: Kendall tau-b, accounting for ties; 5,000 bootstrap resamples
  of complete customer pairs with reranking each time, seed 5585. Keep the
  original T1-T3 bootstrap stream (seed 558) unchanged.
- Include all five tests in duplicate-retention and cutoff sensitivity outputs.
  T5 does not use the broad/narrow cutoff, so it should be unchanged across those
  cutoff checks. Sensitivity Holm values use five-test families and remain
  descriptive. Only the main T5 analysis receives a bootstrap CI.
- Both additions condition on return. Selection effects and seasonal/customer
  confounding remain. Earlier first returns leave more time for additional visits;
  T4 and T5 are related descriptions, not independent causal mechanisms.
- Report the specified analyses even if they are nonsignificant. Do not change
  direction, cutoffs, effect thresholds or primary methods after seeing results.
