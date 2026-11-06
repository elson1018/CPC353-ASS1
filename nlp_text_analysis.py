"""
CPC353 Natural Language Processing - Assignment 1
Topic: Code-Switching in English-Malay Food Product Reviews
Script: Text Analytics & NLP Pipeline (Concordance KWIC & N-gram Collocations)

Instructions to run:
    python nlp_text_analysis.py
"""

import csv
import re
from collections import Counter
from pathlib import Path

# Paths
WORKSPACE_DIR = Path(__file__).resolve().parent
CSV_PATH = WORKSPACE_DIR / "corpus_data.csv"
CONCORDANCE_OUT = WORKSPACE_DIR / "concordance_results.csv"
BIGRAM_OUT = WORKSPACE_DIR / "top_bigrams.csv"

# Bilingual Stopwords (English & Malay common grammatical particles/function words)
BILINGUAL_STOPWORDS = {
    "the", "and", "is", "in", "to", "of", "it", "for", "with", "on", "at", "by", "from", "this", "that", "my", "so", "all",
    "dan", "yang", "di", "ke", "ini", "itu", "untuk", "dengan", "pada", "dari", "oleh", "adalah", "iaitu", "dalam",
    "pun", "lah", "je", "kan", "tu", "dia", "ni", "dah", "ada", "tak", "tidak", "nak", "akan", "sangat", "amat"
}

KEYWORDS = ["sedap", "pedas", "kuah", "worth", "packaging", "repeat", "padu", "hancur"]

def clean_and_tokenize(text: str) -> list[str]:
    """Cleans text of punctuation and extracts lowercase word tokens."""
    clean = re.sub(r"[^\w\s-]", " ", text.lower())
    tokens = [w for w in clean.split() if len(w) > 1]
    return tokens

def extract_concordances(reviews: list[dict], window_size: int = 4) -> list[dict]:
    """Generates Key Word in Context (KWIC) concordance lines."""
    concordances = []
    for r in reviews:
        words = r["ReviewText"].split()
        for i, raw_w in enumerate(words):
            clean_w = re.sub(r"[^\w]", "", raw_w).lower()
            if clean_w in KEYWORDS:
                left_start = max(0, i - window_size)
                left_context = " ".join(words[left_start:i])
                right_end = min(len(words), i + 1 + window_size)
                right_context = " ".join(words[i + 1:right_end])
                
                concordances.append({
                    "ReviewID": r["ReviewID"],
                    "DataOrigin": r["DataOrigin"],
                    "Keyword": clean_w.upper(),
                    "LeftContext": left_context,
                    "RightContext": right_context,
                    "LanguageClassification": r["LanguageClassification"],
                    "CodeSwitchingType": r["CodeSwitchingType"],
                    "Rating": r["Rating"],
                    "FullText": r["ReviewText"]
                })
    return concordances

def extract_ngrams(reviews: list[dict], n: int = 2, filter_stopwords: bool = True) -> Counter:
    """Extracts n-grams from a list of review dictionaries."""
    ngram_counts = Counter()
    for r in reviews:
        tokens = clean_and_tokenize(r["ReviewText"])
        if len(tokens) < n:
            continue
        for i in range(len(tokens) - n + 1):
            gram = tuple(tokens[i:i + n])
            if filter_stopwords:
                # If all words in the tuple are stopwords, skip
                if all(w in BILINGUAL_STOPWORDS for w in gram):
                    continue
            ngram_counts[" ".join(gram)] += 1
    return ngram_counts

def main():
    print("=" * 65)
    print(" CPC353 NLP ASSIGNMENT 1: TEXT ANALYTICS PIPELINE")
    print("=" * 65)

    if not CSV_PATH.exists():
        print(f"Error: Could not find dataset at {CSV_PATH}")
        return

    # 1. Load Data
    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        reviews = list(reader)

    print(f"Loaded {len(reviews)} reviews from {CSV_PATH.name}\n")

    # 2. Technique 1: Concordance Analysis (KWIC)
    print("--> Technique 1: Generating Concordance Lines (KWIC)...")
    concordances = extract_concordances(reviews, window_size=4)
    print(f"    Total Concordance Hits: {len(concordances)}")

    with open(CONCORDANCE_OUT, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=concordances[0].keys())
        writer.writeheader()
        writer.writerows(concordances)
    print(f"    Exported concordance lines to: {CONCORDANCE_OUT.name}\n")

    # 3. Technique 2: N-gram Extraction
    print("--> Technique 2: Extracting N-gram Collocations...")
    overall_bigrams = extract_ngrams(reviews, n=2, filter_stopwords=True)
    code_switched_reviews = [r for r in reviews if r["LanguageClassification"] == "Code-switched"]
    code_bigrams = extract_ngrams(code_switched_reviews, n=2, filter_stopwords=True)

    real_reviews = [r for r in reviews if r["DataOrigin"] == "Self-Collected (Real)"]
    ai_reviews = [r for r in reviews if r["DataOrigin"] == "AI-Generated (LLM)"]
    real_bigrams = extract_ngrams(real_reviews, n=2, filter_stopwords=True)
    ai_bigrams = extract_ngrams(ai_reviews, n=2, filter_stopwords=True)

    pos_reviews = [r for r in reviews if int(r["Rating"]) >= 4]
    neg_reviews = [r for r in reviews if int(r["Rating"]) <= 2]
    pos_bigrams = extract_ngrams(pos_reviews, n=2, filter_stopwords=True)
    neg_bigrams = extract_ngrams(neg_reviews, n=2, filter_stopwords=True)

    # Export Top Bigrams to CSV
    with open(BIGRAM_OUT, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Ngram", "Frequency"])
        for gram, count in overall_bigrams.most_common(25):
            writer.writerow([gram, count])
    print(f"    Exported top bigrams to: {BIGRAM_OUT.name}\n")

    # 4. Technique 3: Bilingual Micro-Lexicon Export
    print("--> Technique 3: Exporting Bilingual Micro-Lexicon...")
    lexicon_entries = [
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
    LEXICON_OUT = WORKSPACE_DIR / "bilingual_lexicon.csv"
    with open(LEXICON_OUT, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=lexicon_entries[0].keys())
        writer.writeheader()
        writer.writerows(lexicon_entries)
    print(f"    Exported {len(lexicon_entries)} lexicon entries to: {LEXICON_OUT.name}\n")

    # 5. Display Summary Tables
    print("=" * 65)
    print("   TOP 10 CODE-SWITCHED BIGRAMS (MIXED ENGLISH-MALAY)")
    print("=" * 65)
    for rank, (gram, freq) in enumerate(code_bigrams.most_common(10), 1):
        print(f" {rank:2d}. {gram:<25} (Freq: {freq})")

    print("\n" + "=" * 65)
    print("   HUMAN REVIEWS VS. AI-GENERATED REVIEWS (TOP BIGRAMS)")
    print("=" * 65)
    print(f" {'Real Human (N=70)':<30} | {'AI Generated (N=70)':<30}")
    print("-" * 65)
    real_top = real_bigrams.most_common(6)
    ai_top = ai_bigrams.most_common(6)
    for (r_gram, r_cnt), (a_gram, a_cnt) in zip(real_top, ai_top):
        print(f" {r_gram:<20} ({r_cnt})    |  {a_gram:<20} ({a_cnt})")

    print("\n" + "=" * 65)
    print("   SENTIMENT POLARITY BIGRAM COMPARISON")
    print("=" * 65)
    print(f" {'Positive 4-5 Stars':<30} | {'Negative 1-2 Stars':<30}")
    print("-" * 65)
    pos_top = pos_bigrams.most_common(6)
    neg_top = neg_bigrams.most_common(6)
    for (p_gram, p_cnt), (n_gram, n_cnt) in zip(pos_top, neg_top):
        print(f" {p_gram:<20} ({p_cnt})    |  {n_gram:<20} ({n_cnt})")

    print("\n" + "=" * 65)
    print("   SAMPLE KWIC CONCORDANCE LINES")
    print("=" * 65)
    sample_keywords = ["SEDAP", "PEDAS", "REPEAT", "WORTH", "KUAH"]
    sample_hits = [c for c in concordances if c["Keyword"] in sample_keywords][:8]
    for hit in sample_hits:
        print(f" {hit['ReviewID']:<10} | {hit['LeftContext']:>20} | [{hit['Keyword']}] | {hit['RightContext']:<25} ({hit['CodeSwitchingType']})")

    print("\nPipeline execution completed successfully!")

if __name__ == "__main__":
    main()
