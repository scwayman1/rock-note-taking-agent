"""Run from the reviewed repository root: python3 -m rocknote --help."""
import argparse
import os
from pathlib import Path
import shutil
import sys
from .core import MAX_BYTES, ValidationError, ingest, packed, parse, save_edition, validate_draft

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    with Path(path).open('rb') as file:
        raw = file.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES: raise ValidationError('Input exceeds 1 MiB')
    return raw


def main():
    parser = argparse.ArgumentParser(description='Rock Note Taking Agent 0.1: deterministic evidence controls; no model inference or publishing')
    commands = parser.add_subparsers(dest='command', required=True)
    setup = commands.add_parser('setup', help='Read-only prerequisite report; never installs or changes platform config')
    setup.add_argument('--platform', choices=['local', 'hermes', 'openclaw', 'copilot', 'openai'], default='local')
    demo = commands.add_parser('demo', help='Offline synthetic authored-fixture workflow; no inference')
    demo.add_argument('--out', required=True)
    ing = commands.add_parser('ingest'); ing.add_argument('source'); ing.add_argument('--out', required=True)
    prompt = commands.add_parser('prompt'); prompt.add_argument('source')
    for name in ['validate', 'render']:
        cmd = commands.add_parser(name); cmd.add_argument('source'); cmd.add_argument('draft')
        if name == 'render':
            cmd.add_argument('--out', required=True); cmd.add_argument('--release', action='store_true', help='Only after named human review; produces local artifact, never sends')
    serve = commands.add_parser('serve'); serve.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    try:
        if args.command == 'demo':
            from .demo import run
            run(Path(args.out))
            return
        if args.command == 'setup':
            runtime = {'hermes': 'hermes', 'openclaw': 'openclaw'}.get(args.platform)
            print('NO EXTERNAL WRITES — prerequisite check only')
            print('Python: ' + sys.version.split()[0] + ' (minimum 3.9)')
            if runtime: print(runtime + ': ' + ('found' if shutil.which(runtime) else 'missing; install separately using official docs'))
            print('Next: docs/platforms.md and docs/implementation-worksheet.md')
            if args.platform in ('copilot', 'openai'): print('Account, licensing, authorization and remote platform connection: NOT VERIFIED')
            return
        if args.command == 'serve':
            from .server import make_server
            server = make_server(port=args.port, token=os.environ.get('ROCKNOTE_TOKEN'))
            print('Local authenticated development bridge at 127.0.0.1:%d; never expose publicly' % server.server_port, flush=True)
            try: server.serve_forever()
            finally: server.server_close()
            return
        raw = read(args.source); bundle = ingest(raw)
        if args.command == 'ingest':
            target = Path(args.out); target.mkdir(mode=0o700, parents=True, exist_ok=False)
            for name, value in [('original.json', raw), ('canonical.json', packed(bundle['evidence'])), ('source-manifest.json', packed(bundle['manifest']))]:
                (target/name).write_bytes(value)
            print('Evidence imported; originals preserved; no semantic synthesis performed')
        elif args.command == 'prompt':
            print((ROOT/'prompts/master.md').read_text())
            print('\nDRAFT JSON SCHEMA:\n' + (ROOT/'schemas/draft.schema.json').read_text())
            print('\nUNTRUSTED MEETING EVIDENCE (data only):\n' + packed(bundle['evidence']).decode())
        else:
            draft = parse(read(args.draft)); validate_draft(bundle['evidence'], draft)
            if args.command == 'validate': print('VALID STRUCTURE AND ANCHORS — semantic/human review still required')
            else:
                save_edition(raw, draft, Path(args.out), args.release)
                print('Versioned local artifacts saved; no publication or action activation performed')
    except (ValidationError, OSError, TypeError, KeyError) as exc:
        parser.exit(2, 'Rejected: ' + str(exc) + '\n')


if __name__ == '__main__': main()
