# Submission checks

The analysis runs, but source evidence and the final report still need review. Check boxes only after the work is completed. The source-verification log records a targeted earlier check; it does not authenticate the entire corpus.

## Source evidence

- [ ] REV-061: obtain an original review or screenshot supporting the complete text. The previous source check found the English and Malay portions in separate reviews. If necessary, replace this record with one verified complete review and re-annotate it. Do not treat the current combined text as verified human code-switching.
- [ ] REV-AI-016: confirm its actual generation date, model and prompt. Its recorded 2026-03-24 date precedes seed REV-018's 2026-07-04 publication. If history is unavailable, generate a replacement from the verified seed and record the actual new details.
- [ ] REV-AI-059: resolve seed REV-061 first, then verify generation history or regenerate. Its recorded 2026-05-06 date precedes the seed's 2026-05-29 date.
- [ ] Verify the seven records sharing the Google Maps URL: REV-004, REV-016, REV-028, REV-034, REV-040, REV-055, REV-068.
- [ ] Locate original reviews behind Lemon8 discovery links for REV-019, REV-029, REV-057.
- [ ] Verify remaining real-labelled records and AI model/prompt history. Shared URLs and discovery links are flags, not proof of invalidity.

For each real record, retain the full original text, URL, available metadata and screenshot/export reference. Never invent missing ratings or dates. The current validator requires both; revise its policy deliberately if verified sources lack metadata. For each AI record, retain the seed ID, exact prompt/output, model used and actual generation date. Do not describe existing text as newly generated without generating it.

## Annotation and regenerated results

- [x] Apply targeted primary-label corrections to REV-006, REV-011 and REV-057, preserving original labels and reasons in `annotation_changes.csv`.
- [ ] Apply the documented policy consistently to all reviews, including ambiguous borrowings and multiple switching types.
- [ ] Complete independent annotation and resolution if claiming two-annotator agreement. Targeted corrections alone do not establish agreement.
- [ ] After evidence or label changes, synchronize the CSV and main workbook, run the pipeline and tests, then regenerate the chart.

```powershell
python nlp_text_analysis.py
python -m unittest discover -s tests -v
python plot_results.py
```

## Final report

- [ ] Update counts, tables, chart and examples from the final regenerated outputs.
- [ ] Explain the review-level counting unit, cleaning, sampling, source evidence, AI generation and primary-label policy.
- [ ] Interpret KWIC examples in full context. Distinguish bigrams within mixed reviews from actual cross-language boundaries. Describe Table IV phrases as selected illustrations.
- [ ] Separate real-labelled and seed-dependent AI evidence. Do not infer reviewer motivations from counts alone or claim independent AI observations of human behaviour.
- [ ] Include title/abstract, motivation/question, dataset scenario, related methods/literature, text exploration, findings, conclusion and references.
- [ ] Connect relevant seminal and recent literature, cite methods/tools and support substantive claims with reliable sources.
- [ ] Inspect final IEEE formatting and 3–6 pages excluding the cover. Export both Word and PDF for eLearn submission on 13 November 2026.
- [ ] Confirm rubric weighting with the lecturer if a numerical self-score is needed; the supplied totals are inconsistent.

The report is linked from README but has not been edited or verified here. Evidence-dependent corrections remain open; generated outputs are provisional while those issues remain.
