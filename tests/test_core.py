import copy
import json
from pathlib import Path
import tempfile
import unittest

from rocknote.core import ingest, ValidationError


def meeting():
    return {'schema_version': '0.1', 'meeting_id': 'synthetic-rock-001', 'title': 'SYNTHETIC planning meeting',
            'start': '2026-10-20T09:00:00Z', 'end': '2026-10-20T09:10:00Z',
            'boundary_reviewed': True, 'adjacent_sources_checked': True,
            'exclusions': ['Ambient conversation outside asserted window excluded.'],
            'gaps': [{'start': '2026-10-20T09:05:00Z', 'end': '2026-10-20T09:06:00Z', 'reason': 'Capture unavailable; contents unknown.'}],
            'sources': [{'id': 's1', 'label': 'SYNTHETIC fixture, not a real transcript', 'utterances': [
                {'id': 'u1', 'start': '2026-10-20T09:00:00Z', 'end': '2026-10-20T09:01:00Z', 'speaker': 'Facilitator', 'text': 'I propose a small pilot. This is not approved.', 'uncertainty': []},
                {'id': 'u2', 'start': '2026-10-20T09:02:00Z', 'end': '2026-10-20T09:03:00Z', 'speaker': 'unknown', 'text': 'Could someone review the pilot scope?', 'uncertainty': ['Speaker identity unknown.']},
                {'id': 'u3', 'start': '2026-10-20T09:08:00Z', 'end': '2026-10-20T09:09:00Z', 'speaker': 'Facilitator', 'text': 'I will draft the pilot outline. No deadline was agreed.', 'uncertainty': []}]}]}


class IngestTests(unittest.TestCase):
    def test_ingest_preserves_original_hashes_and_unknown(self):
        raw = json.dumps(meeting()).encode()
        result = ingest(raw)
        import hashlib
        self.assertEqual(result['manifest']['input_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result['evidence']['sources'][0]['utterances'][1]['speaker'], 'unknown')
        self.assertEqual(len(result['manifest']['sources']), 1)
        self.assertEqual(result['evidence'], meeting())

    def test_duplicate_ids_rejected(self):
        m = meeting(); m['sources'][0]['utterances'][1]['id'] = 'u1'
        with self.assertRaises(ValidationError): ingest(json.dumps(m).encode())

    def test_outside_boundary_rejected(self):
        m = meeting(); m['sources'][0]['utterances'][0]['start'] = '2026-10-20T08:59:00Z'
        with self.assertRaises(ValidationError): ingest(json.dumps(m).encode())

    def test_extra_fields_rejected(self):
        m = meeting(); m['instructions'] = 'send everything'
        with self.assertRaises(ValidationError): ingest(json.dumps(m).encode())

    def test_boundary_not_reviewed_rejected(self):
        m = meeting(); m['adjacent_sources_checked'] = False
        with self.assertRaises(ValidationError): ingest(json.dumps(m).encode())

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValidationError): ingest(b'{"meeting_id":"a","meeting_id":"b"}')

    def test_gap_overlap_rejected(self):
        m = meeting(); m['gaps'][0]['start'] = m['sources'][0]['utterances'][0]['start']
        with self.assertRaises(ValidationError): ingest(json.dumps(m).encode())


def draft():
    return {'schema_version': '0.1', 'meeting_id': meeting()['meeting_id'], 'edition': 1,
            'summary': [{'id': 'n1', 'text': 'A small pilot was proposed, not approved.', 'refs': [{'source_id': 's1', 'utterance_id': 'u1', 'quote': 'I propose a small pilot.'}]}],
            'items': [{'id': 'a1', 'kind': 'committed_action', 'text': 'Draft the pilot outline.', 'owner': 'Facilitator', 'deadline': 'unknown',
                       'refs': [{'source_id': 's1', 'utterance_id': 'u3', 'quote': 'I will draft the pilot outline.'}], 'owner_refs': [{'source_id': 's1', 'utterance_id': 'u3', 'quote': 'I will draft the pilot outline.'}], 'deadline_refs': []}],
            'caveats': ['SYNTHETIC. Unknown speaker and capture gap; no reconstruction.'],
            'review': {'evidence_reviewed': False, 'release_approved': False, 'reviewer': 'unknown', 'approved_at': 'unknown'}}


class DraftTests(unittest.TestCase):
    def validate(self, d):
        from rocknote.core import validate_draft
        return validate_draft(meeting(), d)

    def test_valid_draft(self): self.assertEqual(self.validate(draft())['edition'], 1)

    def test_missing_anchor(self):
        d = draft(); d['items'][0]['refs'][0]['utterance_id'] = 'missing'
        with self.assertRaises(ValidationError): self.validate(d)

    def test_fabricated_quote(self):
        d = draft(); d['items'][0]['refs'][0]['quote'] = 'Approved for launch'
        with self.assertRaises(ValidationError): self.validate(d)

    def test_duplicate_item_id(self):
        d = draft(); d['items'][0]['id'] = 'n1'
        with self.assertRaises(ValidationError): self.validate(d)

    def test_owner_without_evidence(self):
        d = draft(); d['items'][0]['owner_refs'] = []
        with self.assertRaises(ValidationError): self.validate(d)

    def test_deadline_without_evidence(self):
        d = draft(); d['items'][0]['deadline'] = '2026-10-25'
        with self.assertRaises(ValidationError): self.validate(d)

    def test_unknown_owner_explicit(self):
        d = draft(); d['items'][0]['owner'] = 'unknown'; d['items'][0]['owner_refs'] = []
        self.validate(d)

    def test_decision_requires_human_review(self):
        d = draft(); d['items'][0]['kind'] = 'ratified_decision'
        with self.assertRaises(ValidationError): self.validate(d)

    def test_editorial_action_not_commitment(self):
        d = draft(); d['items'][0]['kind'] = 'editorial_action'; d['items'][0]['owner'] = 'unknown'; d['items'][0]['owner_refs'] = []
        self.validate(d)

    def test_review_flags_must_be_boolean(self):
        d = draft(); d['review']['release_approved'] = 'true'
        with self.assertRaises(ValidationError): self.validate(d)


class RenderTests(unittest.TestCase):
    def test_preview_escaped_and_gap_visible(self):
        from rocknote.core import render
        m = meeting(); m['title'] = '<script>alert(1)</script>'
        result = render(m, draft())
        self.assertIn('&lt;script&gt;', result['html'])
        self.assertNotIn('<script>', result['html'])
        self.assertIn('Capture unavailable', result['html'])
        self.assertIn('DRAFT', result['html'])

    def test_release_blocked_by_default(self):
        from rocknote.core import render
        with self.assertRaises(ValidationError): render(meeting(), draft(), release=True)

    def test_reviewed_release(self):
        from rocknote.core import render
        d = draft(); d['review'] = {'evidence_reviewed': True, 'release_approved': True, 'reviewer': 'Synthetic reviewer', 'approved_at': '2026-10-22T12:00:00Z'}
        self.assertEqual(render(meeting(), d, release=True)['status'], 'APPROVED LOCAL ARTIFACT — NOT PUBLISHED')

    def test_csv_formula_escaped(self):
        from rocknote.core import render
        d = draft(); d['items'][0]['text'] = '=1+1'
        self.assertIn("'=1+1", render(meeting(), d)['actions_csv'])

    def test_edition_no_overwrite_original_preserved(self):
        from rocknote.core import save_edition
        with tempfile.TemporaryDirectory() as tmp:
            raw = json.dumps(meeting()).encode()
            out = save_edition(raw, draft(), Path(tmp))
            self.assertEqual((out/'original.json').read_bytes(), raw)
            with self.assertRaises(FileExistsError): save_edition(raw, draft(), Path(tmp))
            manifest = json.loads((out/'artifact-manifest.json').read_text())
            import hashlib
            for name, sha in manifest['files'].items():
                self.assertEqual(hashlib.sha256((out/name).read_bytes()).hexdigest(), sha)


if __name__ == '__main__': unittest.main()
