"""These failures are intentional at the start of lab 2."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('waiter', Path(__file__).resolve().parents[1] / 'labs/review_waiter.py')
waiter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(waiter)


def review(identity=2, reviewer='review-bot', head='head-2', state='COMMENTED'):
    return {'id': identity, 'user': {'login': reviewer}, 'commit_id': head,
            'state': state, 'submitted_at': '2026-11-17T12:00:00Z', 'body': 'Read the threads.'}


def choose(reviews, previous_ids=None):
    return waiter.select_review(reviews, head='head-2', reviewer='review-bot', previous_ids=previous_ids or set())


def test_existing_review_does_not_satisfy_a_new_request():
    assert choose([review(1)], {1}) is None


def test_other_reviewers_do_not_satisfy_the_request():
    assert choose([review(reviewer='another-reviewer')]) is None


def test_previous_commit_does_not_satisfy_the_request():
    assert choose([review(head='head-1')]) is None


def test_pending_review_is_not_received_yet():
    assert choose([review(state='PENDING')]) is None


def test_commented_review_is_received_even_without_approval():
    assert choose([review()])['state'] == 'COMMENTED'


def test_newest_eligible_review_wins_even_when_response_order_changes():
    assert choose([review(9), review(2)])['id'] == 9
