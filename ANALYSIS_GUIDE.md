# Annotation and interpretation guide

The primary-label policy below is now used for targeted corrections to REV-006, REV-011 and REV-057, recorded in `annotation_changes.csv`. The rest of the corpus still needs consistent review. This is not a completed independent two-annotator study.

## Research question

What are the common English–Malay code-switching patterns found in instant-noodle product reviews?

The complete review is the counting unit. A review can contain several switching instances and several switching types. Do not describe a review count as a count of language-switching boundaries.

## Proposed annotation procedure

1. Two team members independently read the original full review, including punctuation. Ideally, hide the existing classification and the other annotator's decisions during this pass.
2. Each records the language category, all observed switching types, exact supporting spans, and any uncertainty. Include primarily single-language and uncertain records in the review, not just the 90 currently labelled mixed.
3. Compare independent decisions, discuss disagreements and record a final resolution. If a third team member adjudicates, record their reason as well.
4. For the single `CodeSwitchingType` field, use this project counting convention: choose intra-sentential if present, otherwise inter-sentential if present, otherwise tag switching. Reserve tag switching for reviews whose only identified alternation is a discourse tag. This precedence is not a linguistic law. Record all observed types and exact spans in the separate annotation log so the primary label does not hide them. Apply the same borrowing rules throughout the corpus.
5. Preserve original labels in the log before changing the corpus. Never fill independent annotation columns with an automatic copy of existing labels. Do not claim two-annotator agreement until it has actually been measured.

Suggested log columns: ReviewID, OriginalLanguage, OriginalSwitchingType, AnnotatorALanguage, AnnotatorATypes, AnnotatorAEvidence, AnnotatorBLanguage, AnnotatorBTypes, AnnotatorBEvidence, FinalLanguage, FinalPrimaryType, AllObservedTypes, ResolutionReason.

## Working definitions and uncertainty

| Decision | Proposed rule |
| --- | --- |
| Intra-sentential | Identifiable English and Malay wording occurs within the same sentence. Record the spans supporting that reading. |
| Inter-sentential | The language alternation occurs between sentences. Inspect the full review; a short KWIC window may not show the preceding sentence. |
| Tag switching | A short discourse item is inserted into surrounding wording. Inspect the full context; the presence of `lah` alone should not override other mixing. |
| Borrowed or ambiguous word | Apply a consistent team rule and record ambiguous cases. Do not automatically count every food name, brand, or familiar borrowed term as switching. |
| Missing punctuation | Do not assume that every language change is a sentence boundary. Mark sentence-type uncertainty where the structure cannot be established reliably. |
| Additional language | Record it explicitly in the notes and apply a consistent policy for Other/uncertain; do not force every multilingual review into a binary account. |

Raw agreement can be calculated separately for language category and primary switching type as matching independent decisions divided by reviews annotated by both people. Report the number of shared reviews and disagreements. If calculating Cohen's kappa, use the original independent decisions, not the final agreed labels. No agreement statistic has been calculated in this project yet.

## KWIC evidence table preview

These contexts come from the current KWIC export. Interpretations below are worked examples for discussion, not new adjudicated labels. Empty context indicates a sentence edge.

| Review | Keyword | Left context | Right context | Interpretation to discuss |
| --- | --- | --- | --- | --- |
| REV-001 | SEDAP | (empty) | giler taste carbonara dia | English `taste` occurs within the same sentence as Malay evaluative wording. |
| REV-010 | KUAH | Hirup | panas-panas waktu hujan memang | The KWIC window is Malay; the preceding English sentence in FullText establishes the between-sentence alternation. |
| REV-057 | SEDAP | Murah and | gila compared to Samyang | The sentence mixes English and Malay. The full review also contains `lah`; a single tag label does not capture every pattern. |
| REV-023 | HANCUR | dalam keadaan elok tanpa | (empty) | `tanpa` negates damage. The full review switches between English and Malay sentences; the damage word alone is not negative sentiment. |
| REV-006 | SEDAP | Pedas gila tapi | (empty) | FullText contains a Malay exclamation followed by English sentences. Its primary label has been corrected to inter-sentential. |

For a report table, use a small selection with a clear reason (within-sentence, between-sentence, tag/multiple types, and a contextual pitfall). These are illustrative cases, not a random sample or an exhaustive functional analysis. Keep the discussion grounded in the exact spans rather than guessing a reviewer's motivation.

## Linking bigrams to the question

`repeat order` is an English pair inside mixed reviews; `dia memang` is Malay wording. Neither is a cross-language boundary just because the review is mixed. `rasa cheese` is a candidate Malay–English adjacency that still requires contextual interpretation and the team's borrowing rules. Frequency measures recurrence, not grammatical significance or the number of reviewers.

## Reproducing Table IV

Run `python3 nlp_text_analysis.py`. The new `outputs/report_table_iv.csv` directly exports counts, group sizes, eligible-position denominators and rates for the report's three selected phrases. These are fixed illustrative phrases, not an automatically selected top three.

The current mixed subsets contain 44 real-labelled reviews with 559 eligible positions and 46 AI reviews with 627. `repeat order` occurs three times in each group: 3 / 559 * 1000 = 5.37 and 3 / 627 * 1000 = 4.78. The same raw count can therefore have different normalized rates. Empty-denominator groups have a blank rate rather than an invented zero.

The `top_bigrams.csv` export also includes each origin's code-switched subset, allowing exploration beyond the three selected phrases. Neither export changes the original labels or the keyword selection policy.

## New supporting outputs

Bigram exports now include distinct-review counts and supporting IDs alongside occurrences. Repetition inside a review increases frequency but not the distinct-review count. The comparison file includes this evidence separately for each origin.

`spelling_variants.csv` compares exact `gila`/`giler` tokens and repeated-final-p forms of `sedap` in code-switched reviews only. These are supplementary manual families; primary counts and original text remain separate and unchanged. Do not claim that an unobserved spelling occurred. Decimal punctuation between digits is now protected during segmentation and tokenization.

Run `python3 plot_results.py` after the pipeline for the optional switching-type chart. ReportLab is required; Poppler additionally creates its PNG version. The chart describes supplied labels, not independently validated switching events.
