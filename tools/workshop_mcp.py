#!/usr/bin/env python3
"""Minimal stdio MCP fixture for the hook lab; synthetic publications only.

This teaching server exposes one structured tool. It does not contact production.
The tool deliberately permits both channels so a native PreToolUse hook can be
observed independently. Output is a local JSONL file supplied at startup.
This fixture is not a production MCP implementation or an isolation boundary.
"""
import argparse
import json
from pathlib import Path
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
for line in sys.stdin:
    request = {}
    try:
        request = json.loads(line)
        identity = request.get('id')
        if identity is None: continue
        method = request.get('method')
        if method == 'initialize':
            result = {'protocolVersion': request.get('params', {}).get('protocolVersion', '2024-11-05'),
                      'capabilities': {'tools': {}}, 'serverInfo': {'name': 'workshop', 'version': '1.0.0'}}
        elif method == 'ping': result = {}
        elif method == 'tools/list':
            result = {'tools': [{'name': 'publish', 'description': 'Write a SYNTHETIC workshop publication to the local fixture log.',
                      'inputSchema': {'type': 'object', 'properties': {'channel': {'type': 'string', 'enum': ['sandbox', 'production']},
                                      'summary': {'type': 'string'}}, 'required': ['channel', 'summary'], 'additionalProperties': False}}]}
        elif method == 'tools/call':
            params = request['params']
            data = params.get('arguments', {})
            if params.get('name') != 'publish' or data.get('channel') not in ('sandbox', 'production') or not isinstance(data.get('summary'), str):
                raise ValueError('invalid publish request')
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open('a') as stream: stream.write(json.dumps(data) + '\n')
            result = {'content': [{'type': 'text', 'text': 'Synthetic publication recorded locally.'}]}
        else:
            print(json.dumps({'jsonrpc': '2.0', 'id': identity, 'error': {'code': -32601, 'message': 'Method not found'}}), flush=True)
            continue
        print(json.dumps({'jsonrpc': '2.0', 'id': identity, 'result': result}), flush=True)
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        print(json.dumps({'jsonrpc': '2.0', 'id': request.get('id') if isinstance(request, dict) else None,
                          'error': {'code': -32602, 'message': str(exc)}}), flush=True)
