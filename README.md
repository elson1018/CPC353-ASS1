# CPC353 English–Malay review analysis

This project studies code-switching in food reviews using KWIC concordances and bigram frequencies. The corpus currently contains 140 reviews: 70 labelled self-collected and 70 labelled AI-generated. Source provenance and linguistic annotations still require manual verification.

Research question: **What are the common English–Malay code-switching patterns found in instant-noodle product reviews?**

## Run

Python 3.10 or later; no third-party packages required.

```bash
python3 nlp_text_analysis.py
python3 -m unittest discover -s tests -v
```

Custom input/output:

```bash
python3 nlp_text_analysis.py --input corpus_data.csv --output-dir outputs
```

The script reads the CSV with UTF-8 BOM support. Input files and original annotation values are preserved. Generated files in the chosen output directory are overwritten on each run. The two CSV results at repository root are legacy teammate outputs; use `outputs/` for current findings.

## Outputs

| File in outputs | Purpose |
| --- | --- |
| cleaned_corpus.csv | Retained original records after structural validation and duplicate removal |
| dataset_summary.json | Cleaning counts, language/rating/origin counts, definitions and limitations |
| data_quality_issues.csv | Rejected records, removed duplicates and flags for manual review |
| language_distribution.csv | Language counts by origin and percentage of all retained reviews |
| switching_distribution.csv | Original switching labels among code-switched reviews, separated by origin |
| concordance_results.csv | Selected keyword hits with up to four tokens of context on each side |
| top_bigrams.csv | Top 25 bigrams per group, including each origin’s code-switched subset, with counts and normalized frequencies |
| report_table_iv.csv | Direct reproduction of the report’s selected mixed-review phrases, with counts, denominators and rates by origin |
| bilingual_lexicon.csv | Manually curated glosses with matching review IDs and unobserved variants |

## Method

The complete review is the dataset unit. Heuristic sentence boundaries are `. ! ? …` and newlines. KWIC and bigrams do not cross these boundaries. This simple splitter may mishandle decimals and abbreviations; inspect examples before quoting them.

Tokens are lowercase Unicode words/numbers; hyphens, apostrophes and single-character tokens are retained. Original review text is preserved. All-stopword bigrams are excluded; stopwords are never deleted to create artificial adjacency. Discourse particles and negation remain available for KWIC and manual interpretation. These are descriptive frequency counts, not statistically scored collocations.

Ties sort alphabetically. Each normalized frequency is occurrences per 1,000 eligible bigram positions within that group, calculated before top-25 selection. Empty groups produce no bigram rows. Zero-count groups remain visible in distribution tables.

Ratings are a sentiment proxy: 4–5 positive, 3 neutral, 1–2 negative. Bigram comparisons are exported overall, by origin, by code-switched subset within each origin, and by rating group within each origin. Table IV uses only code-switched reviews in both origin groups; its fixed illustrative phrases are not an automatic top-three selection. AI examples depend on real-labelled seeds, so they cannot be treated as independent evidence of human behaviour. Bigrams from code-switched reviews are not necessarily cross-language bigrams; token-level language annotation would be needed to make that claim.

Validation rejects missing required fields, invalid categories/ratings/dates, malformed CSV rows, and duplicate IDs. Case/whitespace-normalized duplicate texts retain the first valid record. Invalid records trigger a nonzero exit after diagnostic exports; missing columns stop analysis. The current schema treats metadata fields as required; genuinely unavailable metadata should be documented and the validation policy deliberately revised rather than invented.

## Manual checks before reporting

- Verify the real-labelled texts verbatim against the original sources; preserve collection evidence. Shared source URLs and discovery links are flagged but do not prove fabrication or invalidity.
- Agree on borrowing versus switching rules, treatment of multilingual reviews, and whether a review can have several switching types. Recheck REV-005, REV-006, REV-011 and similar cases. Two annotators should review disagreements and record resolutions.
- The latest CSV replaces the earlier noodle-snack records and their AI counterparts. The main workbook still contains the old versions of those eight records.
- Verify model names, dates, generation prompts and seed provenance. Automatic checks only confirm that seed IDs exist.
- The Excel workbook has worksheet XML whose encoding declaration disagrees with its bytes; some readers reject it. The pipeline uses the current CSV instead; the workbook and CSV are no longer synchronized. Original workbooks are unchanged.
- Manually curated lexicon glosses, POS and polarity are interpretations, not automatic predictions. Inspect their corpus examples; spicy wording can express praise or criticism.

## Report and interpretation

The lecturer clarified that at least one NLP technique is required. This project implements KWIC and bigrams. The report is maintained in [Google Docs](https://docs.google.com/document/d/1OpfJmWQtox4oaWvXqSSHQtA-ZumVILknjAfxZOBs_Jg/edit); the submission requires Word and PDF in IEEE format, 3–6 pages excluding the cover, due 13 November 2026.

See [ANALYSIS_GUIDE.md](ANALYSIS_GUIDE.md) for a proposed independent annotation workflow and a KWIC evidence-table preview. These are worked examples and proposed rules, not a completed two-annotator study. Existing corpus labels are unchanged. After any agreed annotation corrections, regenerate all outputs and update report counts. The supplied rubric's weights are inconsistent and need lecturer clarification.
