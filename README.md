# The Outliers: first-basket variety and 90-day customer behaviour

CSE558 Data Science midterm project, IIIT-Delhi, Monsoon 2026.

**Report:** [report.pdf](report.pdf) | **Notebook:** [project.ipynb](project.ipynb) | **Script:** [analysis.py](analysis.py)

Repository: https://github.com/harshil-0/TheOutliers_DSC

## Research question

Is first-shopping-day basket variety associated with 90-day purchasing behaviour
among identified UK customers first observed in January-August 2011? We study
return occurrence and spending, plus basket composition, timing and frequency
among observed returners. This is observational inference, not a causal study or
an analysis of profit/net revenue.

## Team and assigned responsibilities

| Member | Roll number | Institute email | Assigned area |
|---|---|---|---|
| Aayush Gupta | 2023014 | aayush23014@iiitd.ac.in | Data provenance and cohort preparation; T1 repurchase inference |
| Harshil | 2023235 | harshil23235@iiitd.ac.in | Spending transformation and T2; notebook and repository |
| Raghav Mittal | 2023415 | raghav23415@iiitd.ac.in | Paired-customer analysis and T3; bootstrap and sensitivity checks |
| Utkarsh | 2023569 | utkarsh23569@iiitd.ac.in | Return-time derivation and T4; timing visualisation and assumptions |
| Jaideep Dahiya | 2023254 | jaideep23254@iiitd.ac.in | Frequency analysis and T5; report integration and limitations |

Generative AI assisted code, statistical analysis and report drafting. This table
allocates responsibilities; it does not claim independent, unaided authorship
or certify that individual member review has occurred.

## Data and preparation

Chen, D. (2015), **Online Retail**, UCI Machine Learning Repository.
[Dataset](https://archive.ics.uci.edu/dataset/352/online%2Bretail) |
[DOI](https://doi.org/10.24432/C5BW33) |
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The original project records retrieval on 13 October 2026. The source contains
541,909 invoice lines and eight columns, from December 2010-December 2011.

Cleaning removes exact repeats, cancellation/nonpositive sales, missing customer
IDs and product codes outside the declared merchandise rule. Large positive
purchases remain; duplicate retention is a sensitivity analysis. There are
**391,150 eligible lines** and a saved **391,150 x 60 encoded matrix** (23,469,000
logical cells). Encoding is distinct from the independent-customer test sample.

UK aggregation yields 15,044 shopping days. We find the earliest eligible day
before restricting entry dates, yielding **2,172 customers**: 1,562 broad first
baskets (10+ SKUs), 610 narrow (1-9). There are **878 returners** (679 broad, 199
narrow), with complete 90-day follow-up. See [DATA_DICTIONARY.md](DATA_DICTIONARY.md).

## Five main tests

All tests are two-sided. Holm correction covers all five main p-values at alpha
0.05. Confidence intervals are marginal 95% intervals.

| Test | Estimate | 95% CI | Raw p | Five-test Holm p | Decision |
|---|---:|---|---:|---:|---|
| T1: Chi-square, return probability | +10.85 pp | +6.32 to +15.22 pp | 3.666e-6 | 1.100e-5 | Reject H0 |
| T2: Welch, mean log(1 + future GBP spend) | +0.7210 | 0.4548 to 0.9872 | 1.280e-7 | 5.120e-7 | Reject H0 |
| T3: Paired t, second-minus-first breadth | -6.092 SKUs | -7.432 to -4.752 | 2.632e-18 | 1.316e-17 | Reject H0 |
| T4: Welch, return gap among returners | +0.770 days | -3.076 to +4.617 | 0.6938 | 0.9692 | Do not reject H0 |
| T5: Spearman, breadth vs frequency among returners | rho=0.0236 | -0.0413 to +0.0890 | 0.4846 | 0.9692 | Do not reject H0 |

T1/T2/T4 contrasts are broad minus narrow. T3 preserves customer pairs. T5 uses
numeric breadth and a customer-pair bootstrap CI; df=876 belongs to its approximate
t reference, not an exact rank-test distribution.

Broader baskets indicate higher unadjusted return probability and mean log
spending, but **not demonstrated higher average pound revenue** (GBP 248.97 vs
264.45; raw-mean p=0.8481). Adjustment for initial spend, units and month leaves
the incremental retention association uncertain (+4.98 pp; CI -0.19 to +10.15;
p=0.0588). Returners' second baskets contain fewer SKUs. T4/T5 do not show faster
return or a meaningful monotonic frequency association among returners.
Non-rejection is not proof of equality; no formal equivalence tests were specified.

[ANALYSIS_PLAN.md](ANALYSIS_PLAN.md) preserves the original T1-T3 plan and a dated
25 October addendum for T4/T5, written after reviewing the earlier work but before
running the additions. This is not external preregistration. Alternative tests
and cutoff/duplicate analyses are diagnostic, not extra confirmatory discoveries.

## Reproduce locally

Use Python 3.10+ in the repository root:

```bash
python -m pip install -r requirements.txt
python analysis.py
python tools/validate_project.py
```

The original workbook is included. If absent, the script downloads the official
UCI ZIP without credentials. A run takes several minutes and regenerates processed
data, encoding, six plots, results, report macros and environment versions.
Importing the script also executes the pipeline; use the command above.

`requirements.txt` gives minimum versions; `requirements-lock.txt` records the
core versions used for this delivery. `environment_versions.json` records the
latest run. Original results were reproduced across the original and updated
environments. An analysis rerun does not rewrite report prose or compile its PDF.

## Google Colab and notebook synchronization

Upload/open `project.ipynb` and select **Runtime > Run all**. The first cell checks
versions, not merely package presence. A fresh runtime downloads the source and
writes to `retail_project/`; download needed outputs before closing the runtime.
All analysis is visible. No unseen remote Python script is executed. Six charts
and computed numerical output are embedded. The notebook does not publish GitHub
content or compile LaTeX.

To synchronize and execute the notebook after changing the script:

```bash
python -m pip install -r requirements-notebook.txt
python tools/sync_notebook.py --execute
```

## Report compilation

The report uses the professor's original two-column template, fonts, geometry,
six sections and parts (a)-(c). The PDF is six pages. Upload `report.tex`,
`results/report_values.tex` and `figures/` into Overleaf and choose **pdfLaTeX**,
or use a local LaTeX distribution:

```bash
pdflatex -interaction=nonstopmode -halt-on-error report.tex
pdflatex -interaction=nonstopmode -halt-on-error report.tex
```

The template also supports XeLaTeX with Carlito fonts. This delivery was built
with Tectonic 0.17.0 (XeTeX), then rendered and inspected page by page. Numerical
macros are generated by the analysis; include them with the report source.

## Repository contents

```text
analysis.py                  Full five-test analysis
project.ipynb                Executed notebook
report.pdf / report.tex      Report and editable source
ANALYSIS_PLAN.md             Original plan and dated extension
DATA_DICTIONARY.md           Variable definitions
SUBMISSION_GUIDE.md          Classroom and GitHub instructions
requirements*.txt            Analysis and optional authoring dependencies
environment_versions.json    Executed versions
MANIFEST_SHA256.txt          Packaged file hashes
DATA_LICENSE.md              UCI attribution
data/raw/                    Original workbook
data/processed/              Clean data, cohort and encoding
results/                     Tests, cleaning flow, run log and validation
figures/                     Six plots as PNG and PDF
tools/                       Notebook synchronization and validation
```

Raw-workbook SHA-256:
`43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d`

Bootstrap resamples: 5,000 each. Seeds: 558 (T1-T3), 5584 (T4), 5585 (T5).
Duplicate and 5/15-SKU cutoff sensitivities also use five-test Holm families.

## Submission

The guidelines require a PDF of at most eight pages by **27 October 2026,
11:59 pm**, plus an accessible code/README link. The template also requests the
notebook or script on Classroom. Submit `report.pdf` and `project.ipynb`, ensuring
the repository is populated and accessible while signed out. See the submission guide.
