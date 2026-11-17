#!/usr/bin/env python3
"""Verify an externally trusted RSA/SHA-256 signature before local ACR install.

The supplied public key is the trust root; never take it from the same untrusted
archive. This workshop wrapper is separate from ACR's content-hash checking.
Archive bytes are snapshotted before verification and only that snapshot is
extracted. Refuse traversal, links, duplicate paths, special files and oversized
payloads. Only after verification/extraction/validation can ACR mutate the project.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile

LIMIT = 20 * 1024 * 1024


def bounded_read(path):
    with Path(path).open('rb') as stream:
        data = stream.read(LIMIT + 1)
    if len(data) > LIMIT: raise ValueError('input exceeds the workshop size limit')
    return data


def verify_extract(archive, signature, trusted_key, output):
    archive_bytes = bounded_read(archive)
    signature_bytes = bounded_read(signature)
    key_bytes = bounded_read(trusted_key)
    output = Path(output)
    with tempfile.TemporaryDirectory(prefix='qcon-signature-') as temporary:
        snapshot = Path(temporary)
        for name, data in [('package.tar.gz', archive_bytes), ('signature', signature_bytes), ('public.pem', key_bytes)]:
            (snapshot / name).write_bytes(data)
        result = subprocess.run(['openssl', 'dgst', '-sha256', '-verify', str(snapshot / 'public.pem'),
                                 '-signature', str(snapshot / 'signature'), str(snapshot / 'package.tar.gz')],
                                capture_output=True, text=True, timeout=15)
        if result.returncode: raise ValueError('signature verification failed; installation refused')
    total, count, seen = 0, 0, set()
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode='r:gz') as archive_file:
        for member in archive_file:
            count += 1
            parts = PurePosixPath(member.name).parts
            if (count > 5000 or not parts or member.name.startswith('/') or '\\' in member.name
                    or any(part in ('.', '..') for part in parts)
                    or PurePosixPath(member.name).as_posix() != member.name
                    or member.name in seen or not member.isfile()):
                raise ValueError('unsafe or non-file archive entry')
            seen.add(member.name)
            total += member.size
            if total > LIMIT: raise ValueError('unpacked archive exceeds size limit')
            target = output.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            stream = archive_file.extractfile(member)
            if stream is None: raise ValueError('archive entry has no content')
            with target.open('wb') as destination:
                shutil.copyfileobj(stream, destination)
            target.chmod(0o755 if member.mode & 0o111 else 0o644)
    if not (output / 'agent-plugin.yaml').is_file():
        raise ValueError('archive must contain agent-plugin.yaml at its root')
    return {'archive_sha256': hashlib.sha256(archive_bytes).hexdigest(),
            'trusted_key_sha256': hashlib.sha256(key_bytes).hexdigest()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--signature', type=Path, required=True)
    p.add_argument('--trusted-key', type=Path, required=True)
    p.add_argument('--project', type=Path, default=Path.cwd())
    p.add_argument('--verify-only', action='store_true')
    args = p.parse_args()
    try:
        with tempfile.TemporaryDirectory(prefix='qcon-verified-') as temporary:
            source = Path(temporary) / 'package'
            source.mkdir()
            evidence = verify_extract(args.archive, args.signature, args.trusted_key, source)
            subprocess.run(['acr', 'validate', str(source)], check=True, timeout=30)
            if not args.verify_only:
                project = args.project.resolve(strict=True)
                store = project / '.workshop'
                store.mkdir(exist_ok=True)
                retained = Path(tempfile.mkdtemp(prefix='verified-policy-', dir=store))
                shutil.copytree(source, retained, dirs_exist_ok=True)
                subprocess.run(['acr', 'install', str(retained), '--project', str(project),
                                '--agent', 'claude-code', '--freshness', 'none', '--non-interactive'], check=True, timeout=30)
                subprocess.run(['acr', 'realize', '--project', str(project)], check=True, timeout=30)
                evidence['retained_source'] = str(retained)
            print(json.dumps({'signature_valid': True, 'installed': not args.verify_only, **evidence}))
        return 0
    except (OSError, ValueError, tarfile.TarError, subprocess.SubprocessError) as exc:
        print(json.dumps({'installed': False, 'error': str(exc)}), file=sys.stderr)
        return 1


if __name__ == '__main__': sys.exit(main())
