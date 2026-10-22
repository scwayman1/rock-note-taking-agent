"""Offline fixture demonstration, deliberately no generated synthesis."""
from pathlib import Path
from .core import ingest, packed, parse, save_edition

def run(root):
    repo = Path(__file__).resolve().parents[1]
    raw = (repo/'fixtures/meeting.json').read_bytes()
    draft = parse((repo/'fixtures/draft.json').read_bytes())
    target = save_edition(raw, draft, root)
    manifest = parse((target/'artifact-manifest.json').read_bytes())
    print('SYNTHETIC authored expected draft; no inference, external requests or publication')
    print('Validated evidence and exact quote anchors; human review remains required')
    print('Edition: ' + str(target))
    print('Artifact manifest: ' + str(target/'artifact-manifest.json'))
    print('Verified file hashes: ' + str(len(manifest['files'])))
    import hashlib
    for name, sha in manifest['files'].items():
        if hashlib.sha256((target/name).read_bytes()).hexdigest() != sha:
            raise ValueError('Artifact hash mismatch')
    return target
