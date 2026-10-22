"""Loopback-only development bridge. Never expose this server publicly."""
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer
from .core import MAX_BYTES, ValidationError, fields, ingest, packed, parse, render, validate_draft


def dispatch(operation, arguments):
    if operation == 'ingest':
        fields(arguments, 'evidence')
        return ingest(packed(arguments['evidence']))
    if operation in ('validate', 'render'):
        fields(arguments, 'evidence draft')
        validate_draft(arguments['evidence'], arguments['draft'])
        if operation == 'validate':
            return {'valid': True, 'semantic_review_required': True, 'publication_performed': False}
        return render(arguments['evidence'], arguments['draft'])
    raise ValidationError('Unsupported operation')


def make_server(host='127.0.0.1', port=8765, token=None):
    if host != '127.0.0.1': raise ValueError('Only 127.0.0.1 allowed. Use a separately secured production host.')
    if not isinstance(token, str) or len(token) < 24: raise ValueError('ROCKNOTE_TOKEN must contain at least 24 characters')
    class Handler(BaseHTTPRequestHandler):
        server_version = 'RocknoteLocal/0.1'
        def setup(self):
            super().setup(); self.connection.settimeout(10)
        def log_message(self, format, *args):
            pass  # Never log headers, credentials or meeting content.
        def reply(self, status, value):
            content = packed(value)
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers(); self.wfile.write(content)
        def authorized(self):
            value = self.headers.get('Authorization', '')
            return hmac.compare_digest(value.encode(), ('Bearer '+token).encode())
        def do_GET(self):
            if self.path != '/health': self.reply(404, {'error': 'Not found'}); return
            if not self.authorized(): self.reply(401, {'error': 'Unauthorized'}); return
            self.reply(200, {'status': 'local-only', 'version': '0.1'})
        def do_POST(self):
            if not self.authorized(): self.reply(401, {'error': 'Unauthorized'}); return
            if self.path not in ('/ingest', '/validate', '/render'): self.reply(404, {'error': 'Not found'}); return
            if self.headers.get('Transfer-Encoding'): self.reply(400, {'error': 'Transfer encoding unsupported'}); return
            if len(self.headers.get_all('Content-Length', [])) != 1: self.reply(400, {'error': 'Exactly one content length required'}); return
            try: size = int(self.headers['Content-Length'])
            except (ValueError, TypeError): self.reply(400, {'error': 'Invalid content length'}); return
            if size < 1 or size > MAX_BYTES: self.reply(413, {'error': 'Body must be 1 byte to 1 MiB'}); return
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json': self.reply(415, {'error': 'JSON required'}); return
            try:
                raw = self.rfile.read(size)
                if len(raw) != size: raise ValidationError('Truncated body')
                result = dispatch(self.path[1:], parse(raw))
            except (ValidationError, TypeError, KeyError, RecursionError):
                self.reply(400, {'error': 'Invalid request; check schemas and evidence anchors'}); return
            self.reply(200, result)
    return HTTPServer((host, port), Handler)
