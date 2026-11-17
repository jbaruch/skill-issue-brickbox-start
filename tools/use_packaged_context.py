#!/usr/bin/env python3
"""Move the deliberately broad local skill out of discovery before ACR install.

Run in a separate packaging clone. Preserves edits in .workshop/local-skill/;
refuses to overwrite a previous backup. No network, no package installation.
"""
from pathlib import Path
import shutil
import sys

root = Path(__file__).resolve().parents[1]
source = root / '.claude/skills/fix-the-ticket'
backup = root / '.workshop/local-skill'
if not source.exists():
    print('No local fix-the-ticket skill to remove from discovery.')
elif backup.exists():
    sys.exit('Backup already exists; inspect .workshop/local-skill before proceeding.')
else:
    backup.parent.mkdir(exist_ok=True)
    shutil.move(str(source), str(backup))
    print('Preserved local skill in .workshop/local-skill; start a fresh agent session after install.')
