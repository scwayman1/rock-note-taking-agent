"""Bounded static repository scan; not a secret detector or security audit."""
import re
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    'machine-local path': re.compile(r'/Us' r'ers/[^/\s]+|/ho' r'me/[^/\s]+|[A-Z]:\\Us' r'ers\\'),
    'private key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'GitHub credential': re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})'),
    'provider credential': re.compile(r'sk-(?:proj-)?[A-Za-z0-9_-]{32,}'),
    'AWS access key': re.compile(r'(?:AKIA|ASIA)[A-Z0-9]{16}'),
    'literal bearer credential': re.compile(r'Bearer [A-Za-z0-9_-]{24,}'),
}

def scan():
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
    names = sorted(set(filter(None, names)))
    findings = []; scanned = 0; binary = 0
    for name in names:
        path = ROOT/name
        if not path.is_file(): continue
        raw = path.read_bytes()
        try: value = raw.decode('utf-8')
        except UnicodeError: binary += 1; continue
        scanned += 1
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(value):
                if label == 'literal bearer credential' and match.group().startswith('Bearer synthetic-test-token-'):
                    continue
                findings.append((name, label, value.count('\n', 0, match.start())+1))
    print('Scope: %d repository files; %d UTF-8 text files scanned; %d binary files skipped' % (len(names), scanned, binary))
    for name, label, line in findings: print('%s:%d: %s (value omitted)' % (name,line,label))
    print('Findings: %d. Common formats only; no guarantee of secret/PII absence.' % len(findings))
    return len(findings)

if __name__ == '__main__': raise SystemExit(bool(scan()))
