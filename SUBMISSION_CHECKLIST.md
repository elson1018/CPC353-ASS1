# Submission checklist

## Current dataset

- [x] Synchronize the active Google Sheet, workbook and CSV: 142 reviews (70 self-collected, 72 AI-generated).
- [x] Regenerate analysis exports: 79 mixed reviews, with 70 intra-sentential, seven inter-sentential and two tag-switching primary labels.
- [x] Confirm structural validation: zero rejected records, normalized duplicates or automated review flags.
- [x] Run all 13 automated tests.
- [ ] Retain identifiable source evidence for self-collected reviews and review AI-assisted annotations as a team.
- [ ] Complete independent annotation and adjudication before reporting annotator agreement.

The Google Sheet is the dataset authority. Structural validation does not authenticate source reviews or independently validate language labels. Generation records preserve seed dependence and distinguish user-assigned dates from actual session generation dates.

## Report

- [x] Align tables, examples and chart with current outputs.
- [x] Describe the review-level unit, methods, annotation conventions and limitations.
- [x] Keep Figure 1 and Table V readable without split content.
- [x] Confirm five report pages plus cover, within the 3–6-page requirement excluding cover.
- [ ] Complete the team's final source, reference and content review.
- [ ] Export Word and PDF from the original Google Doc and inspect the submission copies.
- [ ] Submit through eLearn by the deadline recorded on the report cover: **17 November 2026 at 12 noon**.

Report: https://docs.google.com/document/d/1OpfJmWQtox4oaWvXqSSHQtA-ZumVILknjAfxZOBs_Jg/edit

## Reproduction

```bash
.venv/bin/python nlp_text_analysis.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python plot_results.py
```

`SOURCE_VERIFICATION.md` and `annotation_changes.csv` document the previous corpus. Their review IDs and findings are historical and do not automatically apply to the rebuilt data.
