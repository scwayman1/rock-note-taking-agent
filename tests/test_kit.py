import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from rocknote.core import ingest, parse, render

ROOT = Path(__file__).resolve().parents[1]

class KitTests(unittest.TestCase):
    def test_fixtures(self):
        evidence = ingest((ROOT/'fixtures/meeting.json').read_bytes())['evidence']
        draft = parse((ROOT/'fixtures/draft.json').read_bytes())
        self.assertIn('DRAFT', render(evidence,draft)['status'])
        request = parse((ROOT/'fixtures/render-request.json').read_bytes())
        self.assertEqual(request, {'evidence': evidence, 'draft': draft})

    def test_demo_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            cmd = [sys.executable, '-m', 'rocknote', 'demo', '--out', tmp]
            first = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertIn('no inference', first.stdout)
            self.assertTrue((Path(tmp)/'synthetic-rock-001/edition-0001/recap.html').exists())
            self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)

    def test_tool_contracts_align(self):
        swagger = json.loads((ROOT/'adapters/copilot/openapi-v2.json').read_text())
        tools = json.loads((ROOT/'adapters/openai/tools.json').read_text())
        self.assertEqual(swagger['swagger'], '2.0')
        self.assertEqual(swagger['host'], '127.0.0.1:8765')
        self.assertEqual(swagger['securityDefinitions']['BearerToken']['name'], 'Authorization')
        self.assertEqual({t['name'] for t in tools}, {'rock_ingest','rock_validate','rock_render'})
        for t in tools:
            operation = swagger['paths']['/'+t['name'][5:]]['post']
            self.assertEqual(operation['operationId'],t['name'])
            self.assertEqual(operation['parameters'][0]['schema'], t['parameters'])
            self.assertTrue(t['strict'])

    def test_all_manual_bridges(self):
        evidence = json.loads((ROOT/'fixtures/meeting.json').read_text())
        request = (ROOT/'fixtures/render-request.json').read_text()
        for operation in ('ingest','validate','render'):
            value = json.dumps({'evidence':evidence}) if operation=='ingest' else request
            result = subprocess.run([sys.executable,'adapters/openai/bridge.py','rock_'+operation],input=value,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIsInstance(json.loads(result.stdout),dict)
        result = subprocess.run([sys.executable,'adapters/openai/bridge.py','rock_release'],input='{}',text=True,capture_output=True)
        self.assertEqual(result.returncode,2)

    def test_skills_have_boundaries(self):
        for platform in ('hermes','openclaw'):
            content = (ROOT/f'adapters/{platform}/rock-note-taking/SKILL.md').read_text()
            self.assertTrue(content.startswith('---\n'))
            self.assertIn('name: rock-note-taking',content)
            self.assertIn('Stop before release.',content)
            self.assertIn('python3 -m rocknote validate',content)
            self.assertNotIn('/Us'+'ers/',content)

    def test_companion_integrity(self):
        manifest = json.loads((ROOT/'docs/companion/manifest.json').read_text())
        self.assertEqual(set(manifest['files']), {'PRC-Rock-Note-Taking-Agent.html','PRC-Rock-Note-Taking-Agent.pdf'})
        for name,sha in manifest['files'].items():
            self.assertEqual(hashlib.sha256((ROOT/'docs/companion'/name).read_bytes()).hexdigest(),sha)
        content = (ROOT/'docs/companion/PRC-Rock-Note-Taking-Agent.html').read_text()
        self.assertIn('Note Taking Agent',content)
        self.assertIn('not deployed',content)

if __name__ == '__main__': unittest.main()
