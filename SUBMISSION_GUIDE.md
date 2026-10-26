# Submission and GitHub guide

## Google Classroom

Upload **report.pdf** and **project.ipynb**; `analysis.py` may also be included.
The six-page report uses the original professor template, includes five tests,
all supplied member details, assigned responsibilities and the repository link.
The deadline is **27 October 2026, 11:59 pm**. Presentation guidelines are separate.

## GitHub

Use the prepared `submission/github/` folder, or extract
`submission/TheOutliers_GitHub.zip`. Upload the **contents at the repository root**,
not the ZIP itself or an extra enclosing folder, to:
https://github.com/harshil-0/TheOutliers_DSC

It includes source, notebook, report, documentation, requirements, validation
tools, figures, results and complete source/processed data. It excludes caches,
old reports, compiler files, review drafts and unfilled course reference documents.

In the browser, select **uploading an existing file** (or **Add file > Upload files**),
add the prepared contents preserving folders, and commit. Confirm README,
notebook and PDF access while signed out. An empty repository does not satisfy
the required code link.

For an authenticated Git client and an empty repository, from the prepared folder:

```bash
git init
git branch -M main
git add .
git commit -m "Complete CSE558 five-test midterm project"
git remote add origin https://github.com/harshil-0/TheOutliers_DSC.git
git push -u origin main
```

If remote commits already exist, clone the repository and copy in the prepared
files instead. Do not force-push or overwrite unrelated work.

## Responsibilities and AI assistance

Each assigned area combines one test with a supporting component. These are
balanced allocations, not invented records of completed individual work.
Generative-AI assistance is disclosed. Members should validate their areas before
representing them as contributions; the package cannot certify that review has
occurred. The supplied documents contain no explicit AI policy, so they do not
themselves establish permission for that assistance.

## Requirements checked against the supplied documents

| Requirement | Evidence |
|---|---|
| Source, dimensions, encoded size >=3M | Report section 1; raw workbook and matrix |
| Feature meaning/types | Section 1; data dictionary |
| Preparation and reasons | Section 2; cleaning functions |
| Before/after reconciliation | Section 3; cleaning_flow.csv |
| EDA, questions, novelty | Section 4; figures |
| 3-5 tests | Five in section 5; guidelines govern over the template's illustrative 2-3 hint |
| H0/H1, alpha, side, method, meaningful effect | Each part (a); dated plan |
| Alternative comparisons | Each part (b); results.json |
| Statistic, df, p, decision, estimate, CI | Each part (c); hypothesis_tests.csv |
| Limitations | Section 6 and synthesis |
| Accessible code and README | Report header; repository must be populated |
| Original template and <=8-page PDF | report.tex and report.pdf |
| Notebook/script on Classroom | project.ipynb / analysis.py |

## Validation and remaining external actions

The original pipeline was reproduced before extension; the additions follow the
dated design. Holm covers all five tests. The final notebook was executed in
order. Independent checks are in `results/validation.json`; every report page was
rendered and inspected. The manifest identifies the packaged files.

Packaging does not submit Google Classroom work or publish GitHub content. Those
external actions must actually occur before submission is complete.

## Discussion preparation

- Invoice lines are the source; customers are the test units.
- First observed is not first-ever purchase. Same-day invoices form one basket.
- All cohort customers have 90 days of follow-up; the initial day is excluded.
- T2 tests mean log spending, not arithmetic revenue.
- T3 preserves customer pairs; T4 compares independent returner groups.
- T5 handles tied counts and bootstraps complete customer pairs.
- T4/T5 null results were retained, not replaced by significant tests.
- T3-T5 condition on returning; non-returners have no invented return date.
- Holm p-values, marginal CIs and diagnostic tests have different roles.
- Practical thresholds are declared analytical choices, not profit rules.
- Adjustment weakens the retention conclusion. Causation is not established.
