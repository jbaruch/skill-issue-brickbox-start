#!/usr/bin/env python3
"""Classify synthetic review comments and decide which need further reasoning."""
import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ENDPOINT = 'https://api.typesafe.ai/v1/systemone'
QUESTION_VERSION = 'review-intent-v1'
MIN_PROBABILITY = 0.80  # Classroom threshold. Only controls display and routing.
CRITERIA = {
    'required_change': 'The reviewer explicitly asks for a change before this PR proceeds.',
    'optional_suggestion': 'The reviewer explicitly presents a change as optional or suitable for later.',
    'not_enough_evidence': 'The comment leaves its intent unclear or needs information outside the supplied text.',
}
COMMENTS = {
    'required': 'Please reject zero-dollar payments before merging and add a test for that case.',
    'paraphrase': 'I am holding approval until a zero amount fails validation and has a regression test.',
    'optional': 'Optional follow-up: rename amount to total. Fine to do it later.',
    'unclear': 'Can you take another look at the payment edge cases?',
    'close_call': 'The amount check might be fine. I would double-check before we call this done.',
}
# Handwritten examples of the API response shape. These are not model predictions.
FIXTURE = {
    'required': ('required_change', 0.97),
    'paraphrase': ('required_change', 0.95),
    'optional': ('optional_suggestion', 0.98),
    'unclear': ('not_enough_evidence', 0.91),
    'close_call': ('required_change', 0.51),
}


def build_request(model):
    return {
        'model': model,
        'state': {'review_comments': COMMENTS},
        'questions': {
            case: {
                'type': 'choice',
                'instructions': (
                    f'Classify what the reviewer asks for in `review_comments.{case}`. '
                    'Use only that comment. A request to look again may need more context.'
                ),
                'criteria': CRITERIA,
            }
            for case in COMMENTS
        },
    }


def route(answer):
    if isinstance(answer, dict) and answer.get('type') == 'choice':
        label = answer.get('choice')
        probabilities = answer.get('probabilities')
        if isinstance(label, str) and label in CRITERIA and isinstance(probabilities, dict):
            probability = probabilities.get(label)
            if type(probability) in (int, float) and 0 <= probability <= 1:
                if label == 'not_enough_evidence':
                    return label, probability, 'reasoning', 'not_enough_evidence'
                if probability < MIN_PROBABILITY:
                    return label, probability, 'reasoning', 'below_demo_threshold'
                return label, probability, 'record_label', None
    return None, None, 'reasoning', 'missing_or_invalid_answer'


def request_jev(payload, key):
    request = Request(
        ENDPOINT, data=json.dumps(payload).encode('utf-8'), method='POST',
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
    )
    with urlopen(request, timeout=12) as response:
        data = json.load(response)
    if not isinstance(data, dict) or not isinstance(data.get('answers'), dict):
        raise ValueError('response is missing the answers object')
    return data.get('model'), data['answers']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--request', action='store_true', help='Print the request without sending it.')
    mode.add_argument('--live', action='store_true', help='Call the TypeSafe API using TYPESAFE_API_KEY.')
    parser.add_argument('--model', default='jev-latest')
    args = parser.parse_args()
    if args.request:
        print(json.dumps(build_request(args.model), indent=2))
        return 0

    source = 'classroom_fixture'
    model = None
    error = None
    if args.live:
        source = 'jev'
        answers = {}
        key = os.environ.get('TYPESAFE_API_KEY')
        if not key:
            error = 'TYPESAFE_API_KEY is unset'
        else:
            try:
                model, answers = request_jev(build_request(args.model), key)
            except HTTPError as exc:
                error = f'TypeSafe returned HTTP {exc.code}'
            except (URLError, OSError, ValueError) as exc:
                error = f'TypeSafe request failed ({type(exc).__name__})'
    else:
        answers = {
            case: {'type': 'choice', 'choice': label, 'probabilities': {label: probability}}
            for case, (label, probability) in FIXTURE.items()
        }

    for case in COMMENTS:
        label, probability, destination, reason = route(answers.get(case))
        print(json.dumps({
            'case': case, 'source': source, 'model': model, 'question_version': QUESTION_VERSION,
            'label': label, 'probability': probability, 'route': destination,
            'reason': 'classifier_unavailable' if error else reason,
        }))
    if error:
        print(f'{error}. All cases routed to reasoning.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
