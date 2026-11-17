#!/usr/bin/env python3
"""Create ephemeral teaching key and signed distribution; never a production key.

Trust the generated public key separately before using verified_install.py.
Private key remains local at mode 0600. No upload or network operations.
"""
import argparse
from pathlib import Path
import subprocess
import tarfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--policy', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
private = a.output / 'teaching-private.pem'
public = a.output / 'trusted-public.pem'
private.touch(mode=0o600)
subprocess.run(['openssl', 'genrsa', '-out', str(private), '2048'], check=True, capture_output=True)
private.chmod(0o600)
subprocess.run(['openssl', 'rsa', '-in', str(private), '-pubout', '-out', str(public)], check=True, capture_output=True)
archive_path = a.output / 'policy.tar.gz'
with tarfile.open(archive_path, 'w:gz') as archive:
    for name in ['agent-plugin.yaml', 'LICENSE', 'rules', 'skills', 'hooks']:
        base = a.policy / name
        paths = sorted(base.rglob('*')) if base.is_dir() else [base]
        for path in paths:
            if path.is_file() and not path.is_symlink() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                archive.add(path, arcname=str(path.relative_to(a.policy)), recursive=False)
subprocess.run(['openssl', 'dgst', '-sha256', '-sign', str(private),
                '-out', str(archive_path) + '.sig', str(archive_path)], check=True, capture_output=True)
print('Created a teaching archive and signature; distribute the trusted public key separately.')
