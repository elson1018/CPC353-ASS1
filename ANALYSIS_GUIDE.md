# Annotation and interpretation guide

The active Google Sheet and synchronized CSV contain 142 reviews: 70 self-collected and 72 AI-generated. The 79 English–Malay mixed reviews have 70 intra-sentential, seven inter-sentential and two tag-switching primary labels. All active records received AI-assisted annotations; this is not a completed independent two-annotator study. Historical change logs and examples from the replaced corpus must not be treated as current review evidence.

## Research question

What are the common English–Malay code-switching patterns found in instant-noodle product reviews?

The complete review is the counting unit. A review can contain several switching instances and several switching types. Do not describe a review count as a count of language-switching boundaries.

## Proposed annotation procedure

1. Two team members independently read the original full review, including punctuation. Ideally, hide the existing classification and the other annotator's decisions during this pass.
2. Each records the language category, all observed switching types, exact supporting spans, and any uncertainty. Include primarily single-language and uncertain records in the review, not just the 79 currently labelled mixed.
3. Compare independent decisions, discuss disagreements and record a final resolution. If a third team member adjudicates, record their reason as well.
4. For the single `CodeSwitchingType` field, use this project counting convention: choose intra-sentential if present, otherwise inter-sentential if present, otherwise tag switching. Reserve tag switching for reviews whose only identified alternation is a discourse tag. This precedence is not a linguistic law. Record all observed types and exact spans in the separate annotation log so the primary label does not hide them. Apply the same borrowing rules throughout the corpus.
5. Preserve original labels in the log before changing the corpus. Never fill independent annotation columns with an automatic copy of existing labels. Do not claim two-annotator agreement until it has actually been measured.

Suggested log columns: ReviewID, OriginalLanguage, OriginalSwitchingType, AnnotatorALanguage, AnnotatorATypes, AnnotatorAEvidence, AnnotatorBLanguage, AnnotatorBTypes, AnnotatorBEvidence, FinalLanguage, FinalPrimaryType, AllObservedTypes, ResolutionReason.

## Working definitions and uncertainty

| Decision | Proposed rule |
| --- | --- |
| Intra-sentential | Identifiable English and Malay wording occurs within the same sentence beyond a discourse-tag insertion alone. Record the spans supporting that reading. |
| Inter-sentential | The language alternation occurs between sentences. Inspect the full review; a short KWIC window may not show the preceding sentence. |
| Tag switching | Otherwise English wording containing discourse tags such as `kan`, `lah`, or `meh` is classified as Code-switched with primary type Tag Switching when those tags are the only identified alternation. A tag insertion alone does not trigger the intra-sentential category. Inspect the words in context as discourse tags, rather than matching character sequences. Tags do not override other within-sentence mixing or alternation between English and Malay sentences. |
| Food names and brand names | Food names and brand names are treated as language-neutral for identifying switching. A code-switching label requires additional identifiable English and Malay wording. This is an annotation convention, not a claim about a name's language of origin. |
| Borrowed or ambiguous word | Apply a consistent team rule and record ambiguous cases. Do not automatically count every food name, brand, or familiar borrowed term as switching. |
| Missing punctuation | Do not assume that every language change is a sentence boundary. Mark sentence-type uncertainty where the structure cannot be established reliably. |
| Additional language | Record it explicitly in the notes and apply a consistent policy for Other/uncertain; do not force every multilingual review into a binary account. |

For illustration (not corpus quotations), “Tomyam ni memang sedap” is Malay wording with a food name, and “This tomyam tastes good” is English wording with a food name. Neither is mixed solely because of “tomyam.” In “Tomyam ni very spicy,” Malay “ni” and English “very spicy” provide additional switching evidence. Apply the convention to both origins when reviewing AI-assisted labels. In current annotations, seller, packaging, voucher and repeat count as English within Malay wording; servis and kurier count as Malay borrowings. Review borderline cases consistently.

Raw agreement can be calculated separately for language category and primary switching type as matching independent decisions divided by reviews annotated by both people. Report the number of shared reviews and disagreements. If calculating Cohen's kappa, use the original independent decisions, not the final agreed labels. No agreement statistic has been calculated in this project yet.

## Primary label priority and examples

Use **Intra-sentential → Inter-sentential → Tag switching** for one primary label per complete review. This is a manual project convention; the analysis script reads the saved labels and does not automatically assign them.

| Review text | Primary label | Reason |
| --- | --- | --- |
| This tastes great lah! | Tag Switching | English wording with only the discourse tag `lah`. Language Classification is Code-switched. |
| Worth buying, kan? | Tag Switching | English wording with only the discourse tag `kan`. |
| Is it really spicy meh? | Tag Switching | English wording with only the discourse tag `meh`. |
| Kuah dia creamy lah! | Intra-sentential | Malay wording mixes with English `creamy` beyond the tag. |
| Sedap sangat. I will buy again lah! | Inter-sentential | Malay and English alternate between sentences; the additional tag does not override this. |

These tags are operationally counted as switching for this project; their use alone does not establish a speaker's identity or the historical language origin of the particle. Apply the same convention to both recorded origins. Existing corpus labels still require manual review under this clarified policy.

## KWIC evidence table preview

These contexts come from the current KWIC export. Interpretations below are worked examples for discussion, not new adjudicated labels. Empty context indicates a sentence edge.

| Review | Keyword | Left context | Right context | Interpretation to discuss |
| --- | --- | --- | --- | --- |
| REV-004 | SEDAP | ini | (empty) | The local window is Malay. FullText includes `beli pada sale 12.12 murah gila`, supporting intra-sentential mixing. |
| REV-009 | REPEAT | meriah next time boleh | order | English `repeat order` occurs within Malay wording; the English pair alone is not a language boundary. |
| REV-015 | SEDAP | (empty) | di masak dgn telur | FullText begins with an English packing sentence before the Malay sentences, supporting inter-sentential switching. |
| REV-033 | PACKAGING | (empty) | baik | English `packaging` directly precedes Malay `baik`. |

For a tag-only example inspect the complete synthetic REV-AI-016: “Good flavour with a noticeable spicy kick lah!” Its primary label is Tag Switching. It has no selected KWIC keyword and must not be presented as a KWIC hit.

For a report table, use a small selection with a clear reason (within-sentence, between-sentence, tag/multiple types, and a contextual pitfall). These are illustrative cases, not a random sample or an exhaustive functional analysis. Keep the discussion grounded in the exact spans rather than guessing a reviewer's motivation.

## Linking bigrams to the question

The current Table IV phrases are `terima kasih`, `boleh repeat` and `repeat order`. The first is Malay, the last English, and `boleh repeat` joins Malay `boleh` to English `repeat` under the project convention. A phrase is not a cross-language boundary merely because its review is mixed. Frequency measures occurrences; distinct-review counts and IDs provide separate supporting evidence.

## Reproducing Table IV

Run `python3 nlp_text_analysis.py`. The new `outputs/report_table_iv.csv` directly exports counts, group sizes, eligible-position denominators and rates for the report's three selected phrases. These are fixed illustrative phrases, not an automatically selected top three.

The current mixed subsets contain 40 self-collected reviews with 767 eligible positions and 39 AI reviews with 611. `terima kasih` occurs six versus three times (7.82 versus 4.91 per 1,000); `boleh repeat` three versus five times (3.91 versus 8.18); `repeat order` four times in each group (5.22 versus 6.55). The same raw count can have different normalized rates. Empty-denominator groups have a blank rate rather than an invented zero. These selected phrases match Table IV in the report, not an automatic ranking procedure.

The `top_bigrams.csv` export also includes each origin's code-switched subset, allowing exploration beyond the three selected phrases. Neither export changes the original labels or the keyword selection policy.

## New supporting outputs

Bigram exports now include distinct-review counts and supporting IDs alongside occurrences. Repetition inside a review increases frequency but not the distinct-review count. The comparison file includes this evidence separately for each origin.

`spelling_variants.csv` compares exact `gila`/`giler` tokens and repeated-final-p forms of `sedap` in code-switched reviews only. These are supplementary manual families; primary counts and original text remain separate and unchanged. Do not claim that an unobserved spelling occurred. Decimal punctuation between digits is now protected during segmentation and tokenization.

Run `.venv/bin/python nlp_text_analysis.py` and `.venv/bin/python plot_results.py` to regenerate outputs. ReportLab is required; Poppler or pypdfium2 additionally creates the PNG. The chart describes supplied labels, not independently validated switching events. The Google Sheet remains the data authority; synchronize input records before regenerating results.
