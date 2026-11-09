import csv
import tempfile
import unittest
from pathlib import Path
import nlp_text_analysis as pipeline


def record(**changes):
    row = dict(zip(pipeline.FIELDS, ['REV-001', pipeline.REAL, 'Instant Noodles', 'Noodles',
        'Example', 'https://example.com/review', '5', '2026-01-01', 'Sedap taste!',
        'Code-switched', 'Intra-sentential', 'Original annotation']))
    row.update(changes)
    return row


class PipelineTests(unittest.TestCase):
    def test_bom_duplicates_and_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'input.csv'
            with path.open('w', encoding='utf-8-sig', newline='') as f:
                w = csv.DictWriter(f, fieldnames=pipeline.FIELDS)
                w.writeheader()
                w.writerows([record(), record(ReviewID='REV-002', ReviewText=' SEDAP   taste! '),
                             record(ReviewID='REV-003', Rating='6'), record()])
            rows, issues, counts = pipeline.load_reviews(path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(counts, dict(collected=4, rejected_invalid=2, removed_duplicate_texts=1, retained=1))
            self.assertEqual(rows[0]['ReviewText'], 'Sedap taste!')
            self.assertEqual(len(issues), 3)

    def test_sentence_boundaries_and_stopword_adjacency(self):
        counts = pipeline.extract_ngrams([record(ReviewText='Sedap. Good! Rasa dan taste.')])
        self.assertNotIn('sedap good', counts)
        self.assertNotIn('rasa taste', counts)
        self.assertEqual(counts['rasa dan'], 1)
        self.assertEqual(counts['dan taste'], 1)

    def test_kwic_boundaries(self):
        hits = pipeline.extract_concordances([record(ReviewText='Sedap taste! Good kuah.')])
        self.assertEqual(hits[0]['LeftContext'], '')
        self.assertEqual(hits[0]['RightContext'], 'taste')
        self.assertEqual(hits[1]['LeftContext'], 'Good')
        self.assertEqual(hits[1]['RightContext'], '')
        zero = pipeline.extract_concordances([record()], window_size=0)[0]
        self.assertEqual((zero['LeftContext'], zero['RightContext']), ('', ''))

    def test_normalization_and_ties(self):
        rows = pipeline.ranked_ngrams([record(ReviewText='B c. A c.')], 'Test')
        self.assertEqual([r['Ngram'] for r in rows], ['a c', 'b c'])
        self.assertEqual(sum(r['Per1000EligiblePositions'] for r in rows), 1000)
        self.assertEqual(pipeline.clean_and_tokenize("Kriuk-kriuk don't"), ['kriuk-kriuk', "don't"])

    def test_empty_and_no_keyword_exports(self):
        for data in ([], [record(ReviewText='Good noodles.')]):
            with self.subTest(data=data), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'input.csv'
                pipeline.write_csv(path, pipeline.FIELDS, data)
                summary = pipeline.run(path, Path(tmp) / 'out')
                self.assertEqual(summary['cleaning']['retained'], len(data))
                with (Path(tmp) / 'out/concordance_results.csv').open() as f:
                    self.assertEqual(list(csv.DictReader(f)), [])

    def test_seed_and_annotation_flags(self):
        issues = pipeline.review_warnings([record(DataOrigin=pipeline.AI, SourceURL_Seed='missing', CodeSwitchingType='N/A')])
        self.assertEqual({i['Issue'] for i in issues}, {'Missing seed', 'Annotation mismatch'})

    def test_lexicon_evidence_is_token_bounded(self):
        entries = pipeline.curated_lexicon([record(ReviewText='Kan! bukan pedaskan.')])
        particles = next(e for e in entries if e['Term'] == 'Lah / Kan / Wehh')
        self.assertEqual(particles['ObservedVariants'], 'kan')
        self.assertEqual(particles['ReviewCount'], 1)

    def test_report_comparison_uses_mixed_reviews_and_full_denominators(self):
        reviews = [record(ReviewText='Repeat order. Nice taste.'),
                   record(ReviewID='REV-002', ReviewText='Repeat order. Repeat order.',
                          LanguageClassification='English', CodeSwitchingType='N/A'),
                   record(ReviewID='REV-AI-001', DataOrigin=pipeline.AI,
                          ReviewText='Repeat order. Nice taste. Great noodles.')]
        row = next(r for r in pipeline.report_origin_comparison(reviews)
                   if r['Ngram'] == 'repeat order')
        self.assertEqual((row['RealReviews'], row['RealEligiblePositions'], row['RealCount']), (1, 2, 1))
        self.assertEqual((row['AIReviews'], row['AIEligiblePositions'], row['AICount']), (1, 3, 1))
        self.assertEqual(row['RealPer1000'], 500)
        self.assertEqual(row['AIPer1000'], 333.33)
        absent = next(r for r in pipeline.report_origin_comparison(reviews) if r['Ngram'] == 'rasa cheese')
        self.assertEqual((absent['RealCount'], absent['RealPer1000']), (0, 0))

    def test_report_comparison_empty_group_rate_is_undefined(self):
        for row in pipeline.report_origin_comparison([]):
            self.assertEqual((row['RealCount'], row['AICount']), (0, 0))
            self.assertEqual((row['RealPer1000'], row['AIPer1000']), ('', ''))


if __name__ == '__main__':
    unittest.main()
