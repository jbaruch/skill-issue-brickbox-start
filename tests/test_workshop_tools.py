"""Exercise the workshop tools in disposable clones with no network calls."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'


class WorkshopToolTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='workshop clone ')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.tools = self.root / 'tools'
        self.tools.mkdir()

    def run_tool(self, name, *args):
        script = self.tools / name
        shutil.copyfile(TOOLS / name, script)
        return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)

    def test_codex_config_preserves_existing_hooks_and_can_be_rerun(self):
        config = self.root / '.codex/config.toml'
        config.parent.mkdir()
        existing = '[[hooks.PreToolUse]]\nmatcher = "Bash"\n'
        config.write_text(existing)
        result = self.run_tool('configure_hook_lab.py', '--agent', 'codex')
        self.assertEqual(result.returncode, 0, result.stderr)
        configured = config.read_text()
        self.assertTrue(configured.startswith(existing))
        server = tomllib.loads(configured)['mcp_servers']['workshop']
        self.assertEqual(server['args'][0], str(self.tools.resolve() / 'workshop_mcp.py'))
        result = self.run_tool('configure_hook_lab.py', '--agent', 'codex')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(config.read_text(), configured)

    def test_claude_config_preserves_other_servers(self):
        config = self.root / '.mcp.json'
        config.write_text('{"mcpServers": {"other": {"command": "echo"}}}')
        result = self.run_tool('configure_hook_lab.py', '--agent', 'claude-code')
        self.assertEqual(result.returncode, 0, result.stderr)
        servers = json.loads(config.read_text())['mcpServers']
        self.assertEqual(servers['other']['command'], 'echo')
        self.assertIn('workshop', servers)

    def test_missing_codex_helper_is_not_the_expected_timeout(self):
        result = self.run_tool('check_review_fixture.py', '--agent', 'codex', '--expect', 'timeout')
        self.assertEqual(result.returncode, 1)
        self.assertIn('Installed helper or fixture missing', result.stderr)
        self.assertIn('.codex/skills/', result.stderr)
        self.assertNotIn('PASS', result.stdout)


if __name__ == '__main__':
    unittest.main()
