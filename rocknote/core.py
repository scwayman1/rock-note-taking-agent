"""Deterministic evidence and artifact controls. No inference or network access."""
import csv
import hashlib
import html
import io
import json
import re
from datetime import datetime
from pathlib import Path

KINDS = ('ratified_decision', 'apparent_agreement', 'aligned_direction', 'proposal', 'reported_current', 'context', 'committed_action', 'editorial_action', 'open_question')
VERSION = '0.1'
MAX_BYTES = 1048576


class ValidationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def parse(raw):
    require(len(raw) <= MAX_BYTES, 'Input exceeds 1 MiB')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'Duplicate JSON key')
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(ValidationError('Non-finite JSON')))
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ValidationError('Invalid JSON: ' + str(exc)) from exc


def packed(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2).encode('utf-8') + b'\n'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def fields(obj, names):
    require(isinstance(obj, dict) and set(obj) == set(names.split()), 'Unexpected or missing fields: ' + names)


def text(value):
    require(isinstance(value, str) and bool(value.strip()) and len(value) <= 20000, 'Expected nonempty bounded text')


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}', value), 'Invalid identifier')


def instant(value):
    text(value)
    try:
        t = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValidationError('Invalid ISO timestamp') from exc
    require(t.tzinfo is not None, 'Timezone required')
    return t


def strings(values):
    require(isinstance(values, list), 'Expected array')
    for value in values:
        text(value)


def ingest(raw):
    evidence = parse(raw)
    fields(evidence, 'schema_version meeting_id title start end boundary_reviewed adjacent_sources_checked exclusions gaps sources')
    require(evidence['schema_version'] == VERSION, 'Unsupported schema version')
    identifier(evidence['meeting_id']); text(evidence['title'])
    start, end = instant(evidence['start']), instant(evidence['end'])
    require(start < end, 'Empty or reversed meeting window')
    require(evidence['boundary_reviewed'] is True and evidence['adjacent_sources_checked'] is True, 'Human boundary and adjacent-source review required')
    strings(evidence['exclusions'])
    require(isinstance(evidence['gaps'], list), 'Expected gaps array')
    gaps = []
    for gap in evidence['gaps']:
        fields(gap, 'start end reason'); text(gap['reason'])
        a, b = instant(gap['start']), instant(gap['end'])
        require(start <= a < b <= end, 'Gap outside window')
        require(all(b <= c or a >= d for c, d in gaps), 'Overlapping gaps')
        gaps.append((a, b))
    require(isinstance(evidence['sources'], list) and 0 < len(evidence['sources']) <= 100, 'Expected 1-100 sources')
    seen, manifest = set(), []
    for source in evidence['sources']:
        fields(source, 'id label utterances'); identifier(source['id']); text(source['label'])
        require(source['id'] not in seen, 'Duplicate identifier'); seen.add(source['id'])
        require(isinstance(source['utterances'], list) and 0 < len(source['utterances']) <= 5000, 'Expected 1-5000 utterances')
        for utterance in source['utterances']:
            fields(utterance, 'id start end speaker text uncertainty')
            identifier(utterance['id']); text(utterance['text']); text(utterance['speaker']); strings(utterance['uncertainty'])
            require(utterance['id'] not in seen, 'Duplicate identifier'); seen.add(utterance['id'])
            a, b = instant(utterance['start']), instant(utterance['end'])
            require(start <= a < b <= end, 'Utterance outside asserted window')
            require(all(b <= c or a >= d for c, d in gaps), 'Utterance intersects declared gap')
            require(utterance['speaker'] != 'unknown' or utterance['uncertainty'], 'Unknown speaker needs uncertainty disclosure')
        manifest.append({'source_id': source['id'], 'canonical_sha256': digest(packed(source)), 'utterance_count': len(source['utterances'])})
    return {'evidence': evidence, 'manifest': {'schema_version': VERSION, 'input_sha256': digest(raw), 'canonical_sha256': digest(packed(evidence)), 'sources': manifest, 'limitations': 'Hashes prove byte integrity, not truth, completeness, consent, authority or confidentiality.'}}


def validate_draft(evidence, draft):
    evidence = ingest(packed(evidence))['evidence']
    fields(draft, 'schema_version meeting_id edition summary items caveats review')
    require(draft['schema_version'] == VERSION and draft['meeting_id'] == evidence['meeting_id'], 'Draft identity mismatch')
    require(type(draft['edition']) is int and 1 <= draft['edition'] <= 999999, 'Edition must be positive integer')
    strings(draft['caveats'])
    review = draft['review']
    fields(review, 'evidence_reviewed release_approved reviewer approved_at')
    require(type(review['evidence_reviewed']) is bool and type(review['release_approved']) is bool, 'Review flags must be booleans')
    text(review['reviewer']); text(review['approved_at'])
    if review['evidence_reviewed'] or review['release_approved']:
        require(review['reviewer'] != 'unknown', 'Named human reviewer required')
        instant(review['approved_at'])
    require(not review['release_approved'] or review['evidence_reviewed'], 'Release requires evidence review')
    anchors = {(s['id'], u['id']): u for s in evidence['sources'] for u in s['utterances']}
    def refs(values, required=True):
        require(isinstance(values, list) and (bool(values) or not required), 'Evidence refs required')
        for ref in values:
            fields(ref, 'source_id utterance_id quote'); text(ref['quote'])
            identifier(ref['source_id']); identifier(ref['utterance_id'])
            key = (ref['source_id'], ref['utterance_id'])
            require(key in anchors, 'Unknown source/utterance reference')
            require(ref['quote'] in anchors[key]['text'], 'Quote is not an exact evidence substring')
    seen = set()
    require(isinstance(draft['summary'], list) and isinstance(draft['items'], list), 'Expected summary and item arrays')
    for item in draft['summary'] + draft['items']:
        require(isinstance(item, dict), 'Expected item object')
        identifier(item.get('id')); require(item['id'] not in seen, 'Duplicate draft identifier'); seen.add(item['id'])
        text(item.get('text')); refs(item.get('refs'))
    for item in draft['summary']:
        fields(item, 'id text refs')
    for item in draft['items']:
        fields(item, 'id kind text owner deadline refs owner_refs deadline_refs')
        require(item['kind'] in KINDS, 'Unsupported evidence class')
        text(item['owner']); text(item['deadline'])
        refs(item['owner_refs'], item['owner'] != 'unknown')
        refs(item['deadline_refs'], item['deadline'] != 'unknown')
        require(item['owner'] != 'unknown' or not item['owner_refs'], 'Unknown owner must not have owner refs')
        require(item['deadline'] != 'unknown' or not item['deadline_refs'], 'Unknown deadline must not have deadline refs')
        if item['kind'] == 'ratified_decision':
            require(review['evidence_reviewed'], 'Ratification requires named human evidence review, not transcript agreement')
    return draft


def render(evidence, draft, release=False):
    validate_draft(evidence, draft)
    require(type(release) is bool, 'release must be boolean')
    require(not release or draft['review']['release_approved'], 'Human release approval required')
    status = 'APPROVED LOCAL ARTIFACT — NOT PUBLISHED' if release else 'DRAFT — RESTRICTED REVIEW ONLY'
    esc = lambda x: html.escape(str(x), quote=True)
    def references(refs):
        return '; '.join(esc(r['source_id'] + '/' + r['utterance_id']) + ': “' + esc(r['quote']) + '”' for r in refs)
    body = [f'<h1>{esc(evidence["title"])}</h1><p class="stamp">{status}</p>',
            f'<p>Meeting {esc(evidence["meeting_id"])} · Edition {draft["edition"]} · {esc(evidence["start"])} — {esc(evidence["end"])}</p>',
            '<h2>Messaging spine</h2>']
    for note in draft['summary']:
        body.append(f'<p>{esc(note["text"])}</p><small>{references(note["refs"])}</small>')
    for kind in KINDS:
        items = [i for i in draft['items'] if i['kind'] == kind]
        if not items: continue
        body.append('<h2>' + esc(kind.replace('_', ' ').title()) + '</h2>')
        for i in items:
            body.append(f'<article><h3>{esc(i["id"])} · {esc(i["text"])}</h3><p>Owner: {esc(i["owner"])} · Deadline: {esc(i["deadline"])}</p><small>{references(i["refs"])}</small></article>')
    body.append('<h2>Source boundaries, gaps and uncertainty</h2>')
    for gap in evidence['gaps']:
        body.append(f'<p>GAP {esc(gap["start"])} — {esc(gap["end"])}: {esc(gap["reason"])}</p>')
    for value in evidence['exclusions'] + draft['caveats']:
        body.append('<p>' + esc(value) + '</p>')
    for source in evidence['sources']:
        body.append('<p>Source: ' + esc(source['id']) + ' · ' + esc(source['label']) + '</p>')
        for u in source['utterances']:
            if u['speaker'] == 'unknown' or u['uncertainty']:
                body.append('<p>' + esc(source['id']+'/'+u['id']) + ' · Speaker: ' + esc(u['speaker']) + ' · ' + esc('; '.join(u['uncertainty'])) + '</p>')
    body.append('<footer>Exact quote checks are not semantic or legal validation. Human review remains required. Raw evidence is private and is not embedded in this recap.</footer>')
    document = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Rock meeting record</title><style>body{max-width:850px;margin:40px auto;padding:24px;background:#f6f1e7;color:#262a2d;font:17px/1.6 Georgia,serif}h1,h2,h3,.stamp{font-family:system-ui,sans-serif}h1{font-size:38px}h2{border-bottom:2px solid #92744b;margin-top:36px}.stamp{border:2px solid #92744b;padding:12px}small,footer{color:#51504b}article{break-inside:avoid}small{overflow-wrap:anywhere}@media print{body{margin:0;padding:0;background:white;font-size:11pt}h2,h3{break-after:avoid}}@page{size:A4;margin:18mm}</style><body>' + ''.join(body) + '</body></html>'
    stream = io.StringIO(newline=''); writer = csv.writer(stream)
    writer.writerow(['id', 'kind', 'text', 'owner', 'deadline', 'source_refs', 'activation'])
    def safe(value):
        return "'" + value if value.lstrip().startswith(('=', '+', '-', '@', '\t', '\r', '\n')) else value
    for i in draft['items']:
        if i['kind'] not in ('committed_action', 'editorial_action'): continue
        writer.writerow([safe(str(v)) for v in (i['id'], i['kind'], i['text'], i['owner'], i['deadline'], ';'.join(r['source_id']+'/'+r['utterance_id'] for r in i['refs']), 'NOT ACTIVATED')])
    return {'status': status, 'html': document, 'actions_csv': stream.getvalue()}


def save_edition(raw, draft, root, release=False):
    bundle = ingest(raw)
    result = render(bundle['evidence'], draft, release)
    target = Path(root) / bundle['evidence']['meeting_id'] / ('edition-%04d' % draft['edition'])
    target.mkdir(mode=0o700, parents=True, exist_ok=False)
    files = {'original.json': raw, 'canonical.json': packed(bundle['evidence']), 'source-manifest.json': packed(bundle['manifest']), 'draft.json': packed(draft), 'recap.html': result['html'].encode(), 'actions.csv': result['actions_csv'].encode()}
    for name, content in files.items():
        (target/name).write_bytes(content)
    manifest = {'schema_version': VERSION, 'meeting_id': draft['meeting_id'], 'edition': draft['edition'], 'status': result['status'], 'files': {name: digest(content) for name, content in files.items()}}
    (target/'artifact-manifest.json').write_bytes(packed(manifest))
    return target

