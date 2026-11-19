#!/usr/bin/env python3
"""Check review behavior in the realized ACR workshop package."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

NATIVE_ROOTS = {'codex': '.codex', 'claude-code': '.claude', 'cursor': '.cursor'}
TIMEOUT = 'timeout waiting for a new review on the current head'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', choices=NATIVE_ROOTS, default='claude-code')
    parser.add_argument('--expect', choices=('received', 'timeout'), default='received')
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    skill = root / NATIVE_ROOTS[args.agent] / 'skills' / 'acr__jbaruch__skill-issue-policy__fix-the-ticket'
    helper = skill / 'scripts/await_review.py'
    fixture = skill / 'fixtures/review.json'
    try:
        if not helper.is_file() or not fixture.is_file():
            raise ValueError(f'Installed helper or fixture missing under {skill}. Check the adapter and run acr realize.')
        result = subprocess.run(
            [sys.executable, str(helper), '7', '--repo', 'workshop/brickbox',
             '--fixture', str(fixture), '--interval', '0.01', '--timeout', '1'],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode:
            if args.expect == 'timeout':
                failure = json.loads(result.stderr)
                if failure.get('received') is False and failure.get('error') == TIMEOUT:
                    print(f'PASS: {TIMEOUT}.')
                    return 0
            raise ValueError(result.stderr.strip() or f'Helper exited {result.returncode}.')
        if args.expect == 'timeout':
            raise ValueError('Expected the COMMENTED fixture to time out, but it returned a review.')
        record = json.loads(result.stdout)
        if (record.get('review_id') != 12 or record.get('state') != 'COMMENTED'
                or record.get('received') is not True or record.get('merge_authorized') is not False):
            raise ValueError(f'Unexpected fixture result: {record}')
        print('PASS: received COMMENTED review 12. Merge authorization is false.')
        return 0
    except (OSError, ValueError, TypeError, AttributeError, subprocess.SubprocessError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
