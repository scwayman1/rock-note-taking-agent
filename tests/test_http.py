import json
import os
import threading
import unittest
from http.client import HTTPConnection

from test_core import meeting, draft


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from rocknote.server import make_server
        cls.server = make_server(port=0, token='synthetic-test-token-not-a-credential')
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True); cls.thread.start()

    @classmethod
    def tearDownClass(cls): cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def call(self, path, value=None, auth=True, method='POST'):
        conn = HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        headers = {'Content-Type': 'application/json'}
        if auth: headers['Authorization'] = 'Bearer synthetic-test-token-not-a-credential'
        conn.request(method, path, json.dumps(value) if value is not None else None, headers)
        result = conn.getresponse(); status = result.status; body = result.read(); conn.close()
        return status, json.loads(body)

    def test_auth_required(self): self.assertEqual(self.call('/ingest', {'evidence': meeting()}, auth=False)[0], 401)
    def test_health(self): self.assertEqual(self.call('/health', method='GET')[0], 200)
    def test_ingest(self): self.assertIn('manifest', self.call('/ingest', {'evidence': meeting()})[1])
    def test_validate(self): self.assertEqual(self.call('/validate', {'evidence': meeting(), 'draft': draft()})[1]['valid'], True)
    def test_render(self): self.assertIn('DRAFT', self.call('/render', {'evidence': meeting(), 'draft': draft()})[1]['html'])
    def test_unknown_route(self): self.assertEqual(self.call('/send', {})[0], 404)
    def test_extra_release_flag_rejected(self): self.assertEqual(self.call('/render', {'evidence': meeting(), 'draft': draft(), 'release': True})[0], 400)
    def test_invalid_evidence(self): self.assertEqual(self.call('/ingest', {'evidence': {}})[0], 400)
    def test_payload_bound(self):
        conn = HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        conn.putrequest('POST', '/ingest')
        conn.putheader('Authorization', 'Bearer synthetic-test-token-not-a-credential')
        conn.putheader('Content-Length', '1048577'); conn.endheaders()
        result = conn.getresponse(); self.assertEqual(result.status, 413); result.read(); conn.close()
    def test_public_bind_rejected(self):
        from rocknote.server import make_server
        with self.assertRaises(ValueError): make_server(host='0.0.0.0', token='synthetic-test-token-not-a-credential')
    def test_missing_token_rejected(self):
        from rocknote.server import make_server
        with self.assertRaises(ValueError): make_server(token='')


if __name__ == '__main__': unittest.main()
