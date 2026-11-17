#!/usr/bin/env python3
"""Behavior check for the realized release. Does not read a version string.

Exit 0 only when the installed helper receives the new COMMENTED review and
does not authorize merge. v0.1.7 intentionally fails this check.
"""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
skill = root / '.claude/skills/acr__jbaruch__skill-issue-policy__fix-the-ticket'
try:
    result = subprocess.run([sys.executable, str(skill / 'scripts/await_review.py'),
        '7', '--repo', 'workshop/brickbox', '--fixture', str(skill / 'fixtures/review.json'),
        '--interval', '0.01', '--timeout', '0.2'], capture_output=True, text=True, timeout=5)
    if result.returncode:
        print('FAIL: installed helper did not receive the completed COMMENTED review.', file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(1)
    record = json.loads(result.stdout)
    assert record['review_id'] == 12 and record['state'] == 'COMMENTED'
    assert record['received'] is True and record['merge_authorized'] is False
    print('PASS: received review 12; merge is not authorized.')
except (OSError, ValueError, KeyError, AssertionError, subprocess.SubprocessError) as exc:
    print('FAIL:', str(exc), file=sys.stderr)
    sys.exit(1)
