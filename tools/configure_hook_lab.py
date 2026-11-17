#!/usr/bin/env python3
"""Create project-only MCP config for the synthetic hook lab; refuse overwrite."""
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
target = root / '.mcp.json'
if target.exists(): sys.exit('.mcp.json already exists; inspect it rather than overwriting.')
target.write_text(json.dumps({'mcpServers': {'workshop': {'command': sys.executable,
    'args': [str(root / 'tools/workshop_mcp.py'), '--output', str(root / '.workshop/publications.jsonl')]}}}, indent=2) + '\n')
print('Created project MCP config. Start a new Claude session and approve the workshop server when prompted.')
