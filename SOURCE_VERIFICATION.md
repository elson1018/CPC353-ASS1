# Source verification on 9 November 2026

This log records a targeted check of the four replacement real-labelled reviews and the two inconsistent AI dates in commit `7fea83a`. It does not verify the entire corpus. The corpus, workbooks, analysis outputs and Google Doc were not modified during this check.

## Replacement review evidence

| Record | Recorded date | Observed evidence | Status |
| --- | --- | --- | --- |
| REV-018 | 2026-07-04 | The Daebak Ghost Pepper review listing shows reviewer W****a on Jul 04, 2026. The supplied wording matches after flattening line breaks, including the price/flavour fields and the statement that the product has not yet been tried. | Text and publication date supported by the displayed source. Keep this source date. Individual rating was not separately verified. |
| REV-038 | 2026-01-04 | The MamaVege review listing shows reviewer r****5 on Jan 04, 2026, with the same preference, expiry, family and taste wording as the corpus. | Text and publication date supported by the displayed source. Individual rating was not separately verified. |
| REV-049 | 2026-01-10 | The Mi Sedaap listing shows reviewer 9****n on Jan 10, 2026, with the same informal Malay wording about waiting for an affordable price. | Text and publication date supported by the displayed source. Individual rating was not separately verified. |
| REV-061 | 2026-05-29 | The Maggi listing shows reviewer L****e on May 29, 2026 with an English delivery/service review. The Malay stock-movement wording occurs in a different review by a masked reviewer on Oct 03, 2025. | The corpus text was not verified as one original review. The displayed evidence is consistent with combining excerpts from separate reviews; collector evidence is needed before deciding how to correct it. |

Direct sources inspected:

- REV-018: https://www.lazada.com.my/product-reviews/?item_id=2397746354
- REV-038: https://www.lazada.com.my/product-reviews/?item_id=3996395403
- REV-049: https://www.lazada.com.my/product-reviews/?item_id=2264585348
- REV-061: https://www.lazada.com.my/product-reviews/?item_id=3850182395

The first source was readable through web retrieval; the other three were checked in the browser after web retrieval failed. The visible listings are the evidence, not a guarantee that every review in the corpus is authentic. Product aggregate ratings are not evidence of the individual review's rating.

## Generation date inconsistencies

| AI record | Recorded generation date | Referenced seed and date | Assessment |
| --- | --- | --- | --- |
| REV-AI-016 | 2026-03-24 | REV-018, 2026-07-04 | The source date is supported. The claimed generation date precedes publication of the specified seed. Confirm the replacement text's actual generation date from its AI conversation or export; do not move the real review date to make the chronology fit. |
| REV-AI-059 | 2026-05-06 | REV-061, 2026-05-29 | The claimed generation date precedes the dated English review, and the seed's combined text has not been verified. Resolve the seed first, then confirm actual generation history. |

No generation-chat exports, screenshots, or timestamped generation logs were found among the project files. Git commit dates establish when files were committed, not when the AI text was generated. Model names in the CSV have not been independently verified.

## Required corrections after evidence is supplied

1. For REV-061, provide a screenshot or original review reference showing its complete text and date. If it was assembled from multiple reviews, it must not remain labelled as one verbatim real review. Use a verified complete review and re-annotate it, or explicitly document an adapted/synthetic origin under a revised data policy. Retaining only the observed English review would require reconsidering its current code-switched classification.
2. Confirm the actual date, model and prompt for each replacement AI review from generation history. If history is unavailable, regenerate from a verified seed and record the actual new generation date and model. Do not present the current unverified text as newly generated without doing so.
3. Once verified changes are made, synchronize the workbook, rerun the pipeline and update the report. Replacement or reclassification can change counts and findings.

## Other source flags

The seven records sharing Google Maps CID `1084291827491024` and three Lemon8 discovery links remain unresolved. The web tool did not return usable content for those URLs in this check. This does not prove the sources or reviews are invalid.

- Shared Google Maps source: REV-004, REV-016, REV-028, REV-034, REV-040, REV-055, REV-068.
- Lemon8 discovery sources: REV-019, REV-029, REV-057.

Full verification requires an identifiable original review, its complete text and available metadata. Keep these records unresolved until that evidence is available. This log deliberately leaves `provenance_verified` unchanged.
