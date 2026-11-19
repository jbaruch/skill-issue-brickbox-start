import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    'jev_review', Path(__file__).resolve().parents[1] / 'tools/jev_review.py',
)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class JevReviewTests(unittest.TestCase):
    def test_each_question_references_its_own_input_and_can_abstain(self):
        request = demo.build_request('jev-latest')
        for case, question in request['questions'].items():
            self.assertIn(case, request['state']['review_comments'])
            self.assertIn(f'`review_comments.{case}`', question['instructions'])
            self.assertIn('not_enough_evidence', question['criteria'])

    def test_labels_and_reasoning_fallback(self):
        cases = [
            ('required_change', 0.97, 'record_label', None),
            ('optional_suggestion', 0.98, 'record_label', None),
            ('not_enough_evidence', 0.91, 'reasoning', 'not_enough_evidence'),
            ('required_change', 0.51, 'reasoning', 'below_demo_threshold'),
            ('unrecognized', 1.0, 'reasoning', 'missing_or_invalid_answer'),
            ('required_change', 1.5, 'reasoning', 'missing_or_invalid_answer'),
        ]
        for label, probability, destination, reason in cases:
            with self.subTest(label=label, probability=probability):
                answer = {'type': 'choice', 'choice': label, 'probabilities': {label: probability}}
                self.assertEqual(demo.route(answer)[2:], (destination, reason))
        self.assertEqual(demo.route(None)[2:], ('reasoning', 'missing_or_invalid_answer'))
