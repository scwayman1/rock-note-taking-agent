"""Manual Responses function-call bridge. Reads JSON args on stdin. No inference."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from rocknote.core import MAX_BYTES, ValidationError, packed, parse
from rocknote.server import dispatch


def main():
    try:
        if len(sys.argv) != 2 or sys.argv[1] not in ('rock_ingest', 'rock_validate', 'rock_render'):
            raise ValidationError('Allowlisted function name required')
        value = dispatch(sys.argv[1][5:], parse(sys.stdin.buffer.read(MAX_BYTES + 1)))
        sys.stdout.buffer.write(packed(value))
    except (ValidationError, TypeError, KeyError):
        print('{"error":"Invalid tool request"}'); return 2
    return 0


if __name__ == '__main__': raise SystemExit(main())
