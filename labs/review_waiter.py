"""Exercise: this selector accepts reviews it should ignore. Fix the contract."""


def select_review(reviews, *, head, reviewer, previous_ids):
    return reviews[-1] if reviews else None
