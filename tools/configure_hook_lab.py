#!/usr/bin/env python3
"""Add the local workshop MCP server to the selected agent's project config."""
import argparse
import json
from pathlib import Path
import sys
import tomllib


def add_server(target, server, *, codex):
    original = target.read_text(encoding='utf-8') if target.exists() else ''
    if codex:
        config = tomllib.loads(original)
        key = 'mcp_servers'
    else:
        config = json.loads(original) if original else {}
        key = 'mcpServers'

    servers = config.setdefault(key, {})
    if 'workshop' in servers:
        if servers['workshop'] == server:
            return False
        raise ValueError(f'{target} already configures a different workshop server.')
    if codex:
        lines = [
            '[mcp_servers.workshop]',
            f'command = {json.dumps(server["command"], ensure_ascii=False)}',
            f'args = {json.dumps(server["args"], ensure_ascii=False)}',
        ]
        updated = '\n\n'.join(part for part in (original.rstrip(), '\n'.join(lines)) if part) + '\n'
        tomllib.loads(updated)
    else:
        servers['workshop'] = server
        updated = json.dumps(config, indent=2) + '\n'

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(updated, encoding='utf-8')
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', choices=('codex', 'claude-code', 'cursor'), default='claude-code')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    relative_config = {
        'codex': '.codex/config.toml',
        'claude-code': '.mcp.json',
        'cursor': '.cursor/mcp.json',
    }[args.agent]
    server = {
        'command': sys.executable,
        'args': [str(root / 'tools/workshop_mcp.py'), '--output', str(root / '.workshop/publications.jsonl')],
    }
    try:
        added = add_server(root / relative_config, server, codex=args.agent == 'codex')
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        parser.exit(1, f'Unable to configure the MCP lab: {exc}\n')
    verb = 'Added' if added else 'Found'
    print(f'{verb} workshop MCP server in {relative_config}. Open a fresh agent session from this clone.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
