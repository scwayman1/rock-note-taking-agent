import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from test_core import meeting, draft


class CLITests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-m', 'rocknote', *map(str, args)], capture_output=True, text=True)

    def test_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); src = root/'meeting.json'; src.write_text(json.dumps(meeting()))
            d = root/'draft.json'; d.write_text(json.dumps(draft()))
            for args in [('ingest', src, '--out', root/'canonical'), ('validate', src, d), ('prompt', src), ('render', src, d, '--out', root/'artifacts')]:
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root/'artifacts'/meeting()['meeting_id']/'edition-0001'/'recap.html').exists())
            denied = self.run_cli('render', src, d, '--out', root/'blocked', '--release')
            self.assertNotEqual(denied.returncode, 0)

    def test_setup_read_only(self):
        result = self.run_cli('setup', '--platform', 'copilot')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('NO EXTERNAL WRITES', result.stdout)

    def test_manual_tool_bridge(self):
        result = subprocess.run([sys.executable, 'adapters/openai/bridge.py', 'rock_ingest'], input=json.dumps({'evidence': meeting()}), text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('manifest', json.loads(result.stdout))


if __name__ == '__main__': unittest.main()
