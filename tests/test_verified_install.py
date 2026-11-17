"""The signature gate must reject modified or unsafe content before installation."""
import importlib.util
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('verified_install', ROOT / 'tools/verified_install.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


@unittest.skipUnless(shutil.which('openssl'), 'signing lab requires OpenSSL')
class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.private, self.public = self.root / 'private.pem', self.root / 'public.pem'
        subprocess.run(['openssl', 'genrsa', '-out', str(self.private), '2048'], check=True, capture_output=True)
        subprocess.run(['openssl', 'rsa', '-in', str(self.private), '-pubout', '-out', str(self.public)], check=True, capture_output=True)

    def signed(self, entries):
        path = self.root / 'policy.tar.gz'
        with tarfile.open(path, 'w:gz') as archive:
            for name, data, kind in entries:
                entry = tarfile.TarInfo(name)
                entry.type = kind
                entry.size = len(data) if kind == tarfile.REGTYPE else 0
                if kind == tarfile.SYMTYPE: entry.linkname = '../outside'
                archive.addfile(entry, io.BytesIO(data) if kind == tarfile.REGTYPE else None)
        signature = self.root / 'signature'
        subprocess.run(['openssl', 'dgst', '-sha256', '-sign', str(self.private),
                        '-out', str(signature), str(path)], check=True, capture_output=True)
        return path, signature

    def test_valid_signature_preserves_exact_bytes(self):
        archive, signature = self.signed([('agent-plugin.yaml', b'teaching manifest', tarfile.REGTYPE)])
        output = self.root / 'unpacked'
        record = gate.verify_extract(archive, signature, self.public, output)
        self.assertEqual((output / 'agent-plugin.yaml').read_bytes(), b'teaching manifest')
        self.assertEqual(len(record['archive_sha256']), 64)

    def test_tampering_refuses_before_project_mutation(self):
        archive, signature = self.signed([('agent-plugin.yaml', b'teaching manifest', tarfile.REGTYPE)])
        archive.write_bytes(archive.read_bytes() + b'modified')
        project = self.root / 'consumer'; project.mkdir()
        result = subprocess.run([sys.executable, str(ROOT / 'tools/verified_install.py'),
            '--archive', str(archive), '--signature', str(signature), '--trusted-key', str(self.public),
            '--project', str(project)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('signature verification failed', result.stderr)
        self.assertEqual(list(project.iterdir()), [])

    def test_signed_parent_traversal_is_still_refused(self):
        archive, signature = self.signed([('../outside', b'bad', tarfile.REGTYPE)])
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            gate.verify_extract(archive, signature, self.public, self.root / 'unpacked')
        self.assertFalse((self.root / 'outside').exists())

    def test_signed_symlink_is_refused(self):
        archive, signature = self.signed([('linked', b'', tarfile.SYMTYPE)])
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            gate.verify_extract(archive, signature, self.public, self.root / 'unpacked')

    def test_signed_duplicate_paths_are_refused(self):
        archive, signature = self.signed([('agent-plugin.yaml', b'first', tarfile.REGTYPE),
                                          ('agent-plugin.yaml', b'second', tarfile.REGTYPE)])
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            gate.verify_extract(archive, signature, self.public, self.root / 'unpacked')
