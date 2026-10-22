"""Render the editable worksheet as self-contained, printable HTML."""
import html
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def main():
    lines = (ROOT/'docs/implementation-worksheet.md').read_text().splitlines()
    parts = []; table = False
    for line in lines:
        if line.startswith('|'):
            if not table: parts.append('<table>'); table = True
            cells = line.strip('|').split('|')
            if all(set(c.strip()) <= set('-: ') for c in cells): continue
            parts.append('<tr>' + ''.join('<td>'+html.escape(c.strip())+'</td>' for c in cells)+'</tr>')
            continue
        if table: parts.append('</table>'); table = False
        if line.startswith('# '): parts.append('<h1>'+html.escape(line[2:])+'</h1>')
        elif line.startswith('## '): parts.append('<h2>'+html.escape(line[3:])+'</h2>')
        elif line: parts.append('<p>'+html.escape(line).replace('- [ ]', '&#x2610;')+'</p>')
    if table: parts.append('</table>')
    page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Group implementation worksheet</title><style>body{max-width:960px;margin:32px auto;padding:20px;font:16px/1.5 system-ui;color:#202932}h1{font-size:30px}h2{font-size:22px;margin-top:32px;border-bottom:2px solid #93744d}table{border-collapse:collapse;width:100%}td{border:1px solid #bbc0c4;padding:10px;vertical-align:top}td:last-child{min-width:35%}p{overflow-wrap:anywhere}tr{break-inside:avoid}h2{break-after:avoid}@media print{body{margin:0;font-size:10pt}h2{font-size:14pt}td{padding:7px}h1{font-size:20pt}}@page{size:A4;margin:16mm}</style><body>' + ''.join(parts) + '</body></html>'
    (ROOT/'docs/implementation-worksheet.html').write_text(page)
    print('Generated printable worksheet HTML')

if __name__ == '__main__': main()
