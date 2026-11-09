"""Reproducible descriptive analysis of the CPC353 review corpus (stdlib only)."""

import argparse
import csv
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

WORKSPACE_DIR = Path(__file__).resolve().parent
FIELDS = ["ReviewID", "DataOrigin", "Category", "ProductName", "SourcePlatform_Model",
          "SourceURL_Seed", "Rating", "ReviewDate", "ReviewText",
          "LanguageClassification", "CodeSwitchingType", "Notes_Prompt"]
REAL = "Self-Collected (Real)"
AI = "AI-Generated (LLM)"
LANGUAGES = ("English", "Malay", "Code-switched", "Other/uncertain")
SWITCHES = ("Intra-sentential", "Inter-sentential", "Tag Switching", "N/A")
KEYWORDS = ("sedap", "pedas", "kuah", "worth", "packaging", "repeat", "padu", "hancur")
BILINGUAL_STOPWORDS = set("""the and is in to of it for with on at by from this that my so all
 dan yang di ke ini itu untuk dengan pada dari oleh adalah iaitu dalam pun lah je kan tu dia ni
 dah ada tak tidak nak akan sangat amat""".split())
TOKEN = re.compile(r"(?:rm)?\d+\.\d+|[^\W_]+(?:[-'’][^\W_]+)*", re.UNICODE | re.IGNORECASE)
SENTENCE_BOUNDARY = re.compile(r"[!?…\r\n]+|(?<!\d)\.|\.(?!\d)")
KWIC_FIELDS = ["ReviewID", "DataOrigin", "Keyword", "LeftContext", "RightContext",
               "LanguageClassification", "CodeSwitchingType", "Rating", "FullText"]
ISSUE_FIELDS = ["ReviewID", "Severity", "Issue", "Detail"]
NGRAM_FIELDS = ["Group", "Reviews", "EligibleNgramPositions", "Ngram", "Frequency",
                "Per1000EligiblePositions", "DistinctReviews", "ReviewIDs"]


def clean_and_tokenize(text):
    """Lowercase Unicode words/numbers; retain hyphens and contractions."""
    return TOKEN.findall(text.lower())


def sentences(text):
    """Keep dots between digits; other . ! ? … and newlines are boundaries.

    Abbreviations and unpunctuated text still require contextual review.
    """
    return [s for s in SENTENCE_BOUNDARY.split(text) if s.strip()]


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def load_reviews(path):
    """Reject malformed records, then retain the first normalized text duplicate."""
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = set(FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
        raw = list(reader)
    retained, issues = [], []
    seen_ids, seen_texts = set(), set()
    rejected = duplicates = 0
    for line, row in enumerate(raw, 2):
        rid = (row.get("ReviewID") or "").strip()
        errors = []
        if None in row or any(row.get(k) is None for k in FIELDS):
            errors.append("Wrong number of CSV fields")
        for k in FIELDS:
            if not (row.get(k) or "").strip():
                errors.append("Missing " + k)
        if row.get("DataOrigin") not in (REAL, AI):
            errors.append("Invalid DataOrigin")
        if row.get("LanguageClassification") not in LANGUAGES:
            errors.append("Invalid LanguageClassification")
        if row.get("CodeSwitchingType") not in SWITCHES:
            errors.append("Invalid CodeSwitchingType")
        if row.get("Rating") not in ("1", "2", "3", "4", "5"):
            errors.append("Rating must be an integer from 1 to 5")
        try:
            date.fromisoformat(row.get("ReviewDate") or "")
        except ValueError:
            errors.append("Invalid ISO review date")
        if rid in seen_ids:
            errors.append("Duplicate ReviewID")
        if errors:
            rejected += 1
            issues.append(dict(zip(ISSUE_FIELDS, [rid, "error", "Rejected record",
                                                  f"CSV line {line}: " + "; ".join(errors)])))
            continue
        seen_ids.add(rid)
        normalized = " ".join(row["ReviewText"].casefold().split())
        if normalized in seen_texts:
            duplicates += 1
            issues.append(dict(zip(ISSUE_FIELDS, [rid, "warning", "Duplicate text",
                                                  "Removed case/whitespace-normalized duplicate"])))
            continue
        seen_texts.add(normalized)
        # Keep original review text and annotation values unchanged.
        retained.append({k: row[k] for k in FIELDS})
    counts = {"collected": len(raw), "rejected_invalid": rejected,
              "removed_duplicate_texts": duplicates, "retained": len(retained)}
    return retained, issues, counts


def review_warnings(reviews):
    issues = []
    real_ids = {r["ReviewID"] for r in reviews if r["DataOrigin"] == REAL}
    urls = {}
    for r in reviews:
        def warn(kind, detail):
            issues.append(dict(zip(ISSUE_FIELDS, [r["ReviewID"], "review", kind, detail])))
        if r["DataOrigin"] == AI:
            if r["SourceURL_Seed"] not in real_ids:
                warn("Missing seed", "Seed does not identify a retained real-labelled review")
        else:
            source = r["SourceURL_Seed"]
            parsed = urlparse(source)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                warn("Invalid source URL", source)
            if "/discover/" in parsed.path:
                warn("Discovery URL", "Confirm the original review permalink and verbatim text")
            urls.setdefault(source, []).append(r)
        mixed = r["LanguageClassification"] == "Code-switched"
        if mixed == (r["CodeSwitchingType"] == "N/A"):
            warn("Annotation mismatch", "Check language classification against switching type")
        if "snack" in r["ProductName"].lower() and r["Category"] == "Instant Noodles":
            warn("Category scope", "Noodle snack included in instant-noodle category; justify or revise manually")
    for url, group in urls.items():
        if len({r["ProductName"] for r in group}) > 1:
            for r in group:
                issues.append(dict(zip(ISSUE_FIELDS, [r["ReviewID"], "review", "Shared source across products",
                    "Check that the source supports this product and review: " + url])))
    return issues


def extract_concordances(reviews, window_size=4):
    if window_size < 0:
        raise ValueError("window_size must be nonnegative")
    out = []
    for r in reviews:
        for sentence in sentences(r["ReviewText"]):
            matches = list(TOKEN.finditer(sentence))
            for i, match in enumerate(matches):
                if match.group().lower() not in KEYWORDS:
                    continue
                left = sentence[matches[max(0, i-window_size)].start():match.start()].strip() if i else ""
                right = sentence[match.end():matches[min(len(matches)-1, i+window_size)].end()].strip() if window_size and i+1 < len(matches) else ""
                if window_size == 0:
                    left = ""
                out.append({"ReviewID": r["ReviewID"], "DataOrigin": r["DataOrigin"],
                    "Keyword": match.group().upper(), "LeftContext": left, "RightContext": right,
                    "LanguageClassification": r["LanguageClassification"],
                    "CodeSwitchingType": r["CodeSwitchingType"], "Rating": r["Rating"],
                    "FullText": r["ReviewText"]})
    return out


def ngram_evidence(reviews, n=2, filter_stopwords=True):
    if n < 1:
        raise ValueError("n must be positive")
    counts = Counter()
    review_ids = {}
    for r in reviews:
        for sentence in sentences(r["ReviewText"]):
            tokens = clean_and_tokenize(sentence)
            for i in range(len(tokens)-n+1):
                gram = tokens[i:i+n]
                # Skip all-stopword spans without deleting tokens or creating adjacency.
                if filter_stopwords and all(w in BILINGUAL_STOPWORDS for w in gram):
                    continue
                phrase = " ".join(gram)
                counts[phrase] += 1
                review_ids.setdefault(phrase, set()).add(r["ReviewID"])
    return counts, review_ids, sum(counts.values())


def ngram_statistics(reviews, n=2, filter_stopwords=True):
    counts, _, denominator = ngram_evidence(reviews, n, filter_stopwords)
    return counts, denominator


def extract_ngrams(reviews, n=2, filter_stopwords=True):
    return ngram_statistics(reviews, n, filter_stopwords)[0]


def ranked_ngrams(reviews, label, limit=25):
    counts, ids, denominator = ngram_evidence(reviews)
    return [{"Group": label, "Reviews": len(reviews), "EligibleNgramPositions": denominator,
             "Ngram": gram, "Frequency": count,
             "Per1000EligiblePositions": round(count / denominator * 1000, 4),
             "DistinctReviews": len(ids[gram]), "ReviewIDs": "; ".join(sorted(ids[gram]))}
            for gram, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]


REPORT_BIGRAMS = ("dia memang", "repeat order", "rasa cheese")
REPORT_COMPARISON_FIELDS = ["Ngram", "RealReviews", "RealEligiblePositions", "RealCount",
                            "RealPer1000", "AIReviews", "AIEligiblePositions", "AICount", "AIPer1000",
                            "RealDistinctReviews", "RealReviewIDs", "AIDistinctReviews", "AIReviewIDs"]


def report_origin_comparison(reviews):
    """Reproduce the report's selected phrases using only mixed reviews per origin.

    These fixed illustrative phrases are not an automatic top-three ranking.
    Include absent phrases as zero counts; leave rates blank for empty denominators.
    """
    groups = {}
    for origin in (REAL, AI):
        subset = [r for r in reviews if r["DataOrigin"] == origin
                  and r["LanguageClassification"] == "Code-switched"]
        counts, ids, denominator = ngram_evidence(subset)
        groups[origin] = (len(subset), counts, ids, denominator)
    rows = []
    for phrase in REPORT_BIGRAMS:
        row = {"Ngram": phrase}
        for origin, prefix in ((REAL, "Real"), (AI, "AI")):
            size, counts, ids, denominator = groups[origin]
            row.update({prefix + "Reviews": size, prefix + "EligiblePositions": denominator,
                        prefix + "Count": counts[phrase],
                        prefix + "Per1000": round(counts[phrase] / denominator * 1000, 2)
                        if denominator else "", prefix + "DistinctReviews": len(ids.get(phrase, set())),
                        prefix + "ReviewIDs": "; ".join(sorted(ids.get(phrase, set())))})
        rows.append(row)
    return rows


SPELLING_FIELDS = ["DataOrigin", "Family", "ObservedForm", "Occurrences", "DistinctReviews", "ReviewIDs"]
SPELLING_PATTERNS = {"gila/giler": re.compile(r"(?:gila|giler)"),
                     "sedap repeated-final-p": re.compile(r"sedap+")}


def spelling_variants(reviews):
    """Supplementary exact-token comparison in mixed reviews; no normalization.

    The gila/giler grouping is a manual lexical choice. The sedap pattern covers
    only repeated final p, not every spelling or morphological variant.
    """
    rows = []
    for origin in (REAL, AI):
        for family, pattern in SPELLING_PATTERNS.items():
            counts, ids = Counter(), {}
            for r in reviews:
                if r["DataOrigin"] != origin or r["LanguageClassification"] != "Code-switched":
                    continue
                for token in clean_and_tokenize(r["ReviewText"]):
                    if pattern.fullmatch(token):
                        counts[token] += 1
                        ids.setdefault(token, set()).add(r["ReviewID"])
            for form, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
                rows.append({"DataOrigin": origin, "Family": family, "ObservedForm": form,
                             "Occurrences": count, "DistinctReviews": len(ids[form]),
                             "ReviewIDs": "; ".join(sorted(ids[form]))})
    return rows


LEXICON_ENTRIES = [
        {"Term": "Sedap giler / gila", "StandardMalay": "Sangat lazat", "EnglishEquivalent": "Crazy delicious", "POS": "Adj + Intensifier", "Function": "Emotional emphasis on flavor", "Polarity": "Positive"},
        {"Term": "Padu / Padu giler", "StandardMalay": "Mantap / berkualiti tinggi", "EnglishEquivalent": "Solid / Top-notch", "POS": "Adjective", "Function": "Expressing rich texture/taste", "Polarity": "Positive"},
        {"Term": "Repeat order", "StandardMalay": "Membeli semula", "EnglishEquivalent": "Repurchase intent", "POS": "Verb phrase", "Function": "E-commerce satisfaction marker", "Polarity": "Positive"},
        {"Term": "Kaw / Pekat kaw", "StandardMalay": "Pekat dan berperisa", "EnglishEquivalent": "Rich and robust", "POS": "Adjective", "Function": "Describing soup viscosity/depth", "Polarity": "Positive"},
        {"Term": "Layan habis", "StandardMalay": "Amat dinikmati", "EnglishEquivalent": "Thoroughly enjoyable", "POS": "Verb phrase", "Function": "Leisure consumption pleasure", "Polarity": "Positive"},
        {"Term": "Ngam / Ngam-ngam", "StandardMalay": "Sesuai / tepat", "EnglishEquivalent": "Just right / perfect fit", "POS": "Adjective", "Function": "Suitability of taste or timing", "Polarity": "Positive"},
        {"Term": "Kriuk-kriuk", "StandardMalay": "Rangup", "EnglishEquivalent": "Extra crispy / crunchy", "POS": "Onomatopoeia", "Function": "Sensory texture descriptor", "Polarity": "Positive"},
        {"Term": "Lembik", "StandardMalay": "Lembek / terlalu lembut", "EnglishEquivalent": "Soggy / mushy", "POS": "Adjective", "Function": "Criticism of overboiled noodles", "Polarity": "Negative"},
        {"Term": "Pedas berapi / nak mampus", "StandardMalay": "Sangat pedas", "EnglishEquivalent": "Burning / lethal spice", "POS": "Adj + Hyperbole", "Function": "Extreme spicy reaction", "Polarity": "Negative"},
        {"Term": "Hancur lebur", "StandardMalay": "Pecah dan berkecai", "EnglishEquivalent": "Completely crushed", "POS": "Verb phrase", "Function": "Logistics damage complaint", "Polarity": "Negative"},
        {"Term": "Lah / Kan / Wehh", "StandardMalay": "Partikel wacana", "EnglishEquivalent": "Pragmatic discourse tags", "POS": "Pragmatic Particle", "Function": "In-group solidarity, affirmation", "Polarity": "Neutral"},
        {"Term": "Bubble wrap tebal", "StandardMalay": "Balutan gelembung tebal", "EnglishEquivalent": "Thick bubble wrap", "POS": "Noun phrase", "Function": "Delivery safety evaluation", "Polarity": "Positive"},
    ]

LEXICON_VARIANTS = [
    ["sedap giler", "sedap gila"], ["padu", "padu giler"], ["repeat order"],
    ["kaw", "pekat kaw"], ["layan habis"], ["ngam", "ngam-ngam"],
    ["kriuk-kriuk"], ["lembik"], ["pedas berapi", "nak mampus"],
    ["hancur lebur"], ["lah", "kan", "wehh"], ["bubble wrap tebal"],
]

def curated_lexicon(reviews):
    """Manual glosses with exact contiguous token matches as corpus evidence."""
    out = []
    for entry, variants in zip(LEXICON_ENTRIES, LEXICON_VARIANTS):
        ids, observed = [], set()
        for review in reviews:
            hit = False
            for sentence in sentences(review["ReviewText"]):
                tokens = clean_and_tokenize(sentence)
                for variant in variants:
                    phrase = clean_and_tokenize(variant)
                    if any(tokens[i:i+len(phrase)] == phrase for i in range(len(tokens)-len(phrase)+1)):
                        observed.add(variant)
                        hit = True
            if hit:
                ids.append(review["ReviewID"])
        out.append({**entry, "Method": "Manually curated; gloss and polarity require contextual review",
                    "ObservedVariants": "; ".join(sorted(observed)),
                    "UnobservedVariants": "; ".join(v for v in variants if v not in observed),
                    "ReviewCount": len(ids), "ReviewIDs": "; ".join(ids)})
    return out


def run(input_path, output_dir):
    reviews, issues, cleaning = load_reviews(input_path)
    issues.extend(review_warnings(reviews))
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "data_quality_issues.csv", ISSUE_FIELDS, issues)
    real = [r for r in reviews if r["DataOrigin"] == REAL]
    ai = [r for r in reviews if r["DataOrigin"] == AI]
    summary = {"cleaning": cleaning, "language_distribution": dict(Counter(r["LanguageClassification"] for r in reviews)),
        "origins": dict(Counter(r["DataOrigin"] for r in reviews)),
        "rating_distribution": dict(sorted(Counter(r["Rating"] for r in reviews).items())),
        "manual_review_flags": sum(i["Severity"] == "review" for i in issues),
        "provenance_verified": False,
        "method": {"unit": "complete review; n-grams and KWIC bounded by heuristic sentences",
            "sentence_boundaries": ". ! ? … and newlines, except dots between digits", "normalization": "lowercase; retain decimal numbers/prices, hyphens, apostrophes and single-character tokens",
            "stopwords": "discard only n-grams whose tokens are all stopwords",
            "frequency_denominator": "all eligible bigram occurrences in the group before top-25 selection",
            "labels": "original annotations; not automatically validated linguistically",
            "sentiment": "rating proxy: 4–5 positive, 3 neutral, 1–2 negative",
            "synthetic_dependence": "AI reviews derive from real-labelled seeds and are not independent observations"}}
    (output_dir / "dataset_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    write_csv(output_dir / "cleaned_corpus.csv", FIELDS, reviews)
    write_csv(output_dir / "concordance_results.csv", KWIC_FIELDS, extract_concordances(reviews))
    language_rows = [{"LanguageClassification": lang, "RealLabelled": sum(r["LanguageClassification"] == lang for r in real),
        "AIGenerated": sum(r["LanguageClassification"] == lang for r in ai),
        "Total": sum(r["LanguageClassification"] == lang for r in reviews),
        "Percent": round(sum(r["LanguageClassification"] == lang for r in reviews)/len(reviews)*100, 2) if reviews else 0}
        for lang in LANGUAGES]
    write_csv(output_dir / "language_distribution.csv", ["LanguageClassification", "RealLabelled", "AIGenerated", "Total", "Percent"], language_rows)
    switch_rows = []
    for label, subset in [("All", reviews), (REAL, real), (AI, ai)]:
        mixed = [r for r in subset if r["LanguageClassification"] == "Code-switched"]
        for switch in SWITCHES:
            count = sum(r["CodeSwitchingType"] == switch for r in mixed)
            switch_rows.append({"Group": label, "SwitchingType": switch, "Count": count,
                                "CodeSwitchedReviews": len(mixed), "Percent": round(count/len(mixed)*100, 2) if mixed else 0})
    write_csv(output_dir / "switching_distribution.csv", ["Group", "SwitchingType", "Count", "CodeSwitchedReviews", "Percent"], switch_rows)
    groups = [("All", reviews), ("Code-switched reviews", [r for r in reviews if r["LanguageClassification"] == "Code-switched"]),
              (REAL, real), (AI, ai)]
    for origin, subset in ((REAL, real), (AI, ai)):
        groups.append((origin + ": Code-switched", [r for r in subset
                       if r["LanguageClassification"] == "Code-switched"]))
    for label, subset in [("All", reviews), (REAL, real), (AI, ai)]:
        for sentiment, ratings in [("Positive", {"4", "5"}), ("Neutral", {"3"}), ("Negative", {"1", "2"})]:
            groups.append((label + ": " + sentiment, [r for r in subset if r["Rating"] in ratings]))
    write_csv(output_dir / "top_bigrams.csv", NGRAM_FIELDS, [row for label, subset in groups for row in ranked_ngrams(subset, label)])
    write_csv(output_dir / "report_table_iv.csv", REPORT_COMPARISON_FIELDS,
              report_origin_comparison(reviews))
    write_csv(output_dir / "spelling_variants.csv", SPELLING_FIELDS, spelling_variants(reviews))
    lexicon = curated_lexicon(reviews)
    write_csv(output_dir / "bilingual_lexicon.csv", list(lexicon[0]), lexicon)
    print(f"Collected {cleaning['collected']}; retained {len(reviews)}; invalid {cleaning['rejected_invalid']}; duplicates {cleaning['removed_duplicate_texts']}.")
    print(f"Analysis written to {output_dir}. Source provenance and linguistic labels require manual verification.")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=WORKSPACE_DIR / "corpus_data.csv")
    parser.add_argument("--output-dir", type=Path, default=WORKSPACE_DIR / "outputs")
    args = parser.parse_args()
    try:
        summary = run(args.input, args.output_dir)
    except (ValueError, OSError, csv.Error) as exc:
        parser.exit(2, f"Error: {exc}\n")
    if summary["cleaning"]["rejected_invalid"]:
        parser.exit(1, "Invalid records excluded; inspect data_quality_issues.csv before using findings.\n")


if __name__ == "__main__":
    main()
