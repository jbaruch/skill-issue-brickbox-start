#!/usr/bin/env python3
"""Read-only workshop checks. Does not print credentials or edit configuration."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--require-acr', action='store_true')
p.add_argument('--require-claude', action='store_true')
p.add_argument('--require-signing', action='store_true')
a = p.parse_args()
errors = []
print('Python:', sys.version.split()[0])
if sys.version_info < (3, 11): errors.append('Python 3.11 or newer is required.')
for tool, required in [('git', True), ('acr', a.require_acr), ('claude', a.require_claude)]:
    exe = shutil.which(tool)
    if exe:
        r = subprocess.run([exe, '--version'], capture_output=True, text=True, timeout=15)
        print(tool + ':', (r.stdout or r.stderr).splitlines()[0] if (r.stdout or r.stderr) else 'installed')
        if r.returncode: errors.append(tool + ' version check failed.')
    elif required: errors.append(tool + ' is missing.')
    else: print(tool + ': optional for local Python labs; not found')
if sys.platform == 'win32' and a.require_acr:
    errors.append('ACR 0.4.3 has no native Windows support. Run the workshop in WSL.')
root = Path(__file__).resolve().parents[1]
skills = root / '.claude/skills'
if (skills / 'fix-the-ticket').exists() and any(skills.glob('acr__jbaruch__skill-issue-policy__*')):
    errors.append('Both starter and packaged skills are discoverable. Use tools/use_packaged_context.py in the packaging clone.')
for key in ['GH_TOKEN', 'GITHUB_TOKEN']:
    print(key + ':', 'set (value hidden)' if os.environ.get(key) else 'unset')
if os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN'):
    print('For GitHub errors, compare authenticated and anonymous access; do not display tokens.')
if a.require_signing:
    openssl = shutil.which('openssl')
    if not openssl:
        errors.append('OpenSSL is required for the signature lab.')
    else:
        r = subprocess.run([openssl, 'version'], capture_output=True, text=True, timeout=15)
        print('OpenSSL:', r.stdout.strip())
        if r.returncode: errors.append('OpenSSL version check failed.')
for error in errors: print('FAIL:', error, file=sys.stderr)
print('Preflight:', 'FAIL' if errors else 'PASS')
sys.exit(bool(errors))
