#!/usr/bin/env python3
"""Compare exact public GitHub endpoints with ACR-style and anonymous auth.

Never prints tokens, headers or response bodies. Does not change auth settings.
This is diagnostic evidence, not automatic fallback from authenticated failures.
"""
import argparse
import json
import os
import subprocess

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--repo', default='jbaruch/skill-issue-policy')
a = p.parse_args()
if len(a.repo.split('/')) != 2 or any(not part or not all(c.isalnum() or c in '_.-' for c in part) for part in a.repo.split('/')):
    p.error('use owner/repository')
token, source = None, 'none (Git credential-helper fallback not reproduced by this diagnostic)'
for name in ['GH_TOKEN', 'GITHUB_TOKEN']:
    if os.environ.get(name, '').strip():
        token, source = os.environ[name].strip(), name
        break
if not token:
    try:
        result = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip(): token, source = result.stdout.strip(), 'gh auth token'
    except (OSError, subprocess.SubprocessError): pass
rows = []
for mode, credential in [('discovered', token), ('anonymous', None)]:
    for suffix in ['', '/releases/latest']:
        # Use system curl's CA store, not an independently installed Python CA
        # bundle. Pass Authorization through stdin, never process arguments.
        config = ''
        if credential:
            if '\n' in credential or '\r' in credential: p.error('credential contains a line break')
            escaped = credential.replace('\\', '\\\\').replace('"', '\\"')
            config = 'header = "Authorization: Bearer ' + escaped + '"\n'
        try:
            result = subprocess.run(['curl', '--silent', '--max-time', '15', '--output', os.devnull,
                '--write-out', '%{http_code}', '--header', 'Accept: application/vnd.github+json',
                '--user-agent', 'qcon-workshop-access-check', '--config', '-',
                'https://api.github.com/repos/' + a.repo + suffix],
                input=config, capture_output=True, text=True, timeout=20)
            status = int(result.stdout) if result.returncode == 0 else 'network_error'
        except (OSError, ValueError, subprocess.SubprocessError): status = 'network_error'
        rows.append({'auth': mode, 'credential_source': source if mode == 'discovered' else 'none',
                     'endpoint': '/repos/' + a.repo + suffix, 'status': status})
print(json.dumps(rows, indent=2))
