"""Render the editable worksheet as a four-sheet, self-contained HTML."""
import html
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def inline(text):
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html.escape(text)).replace('- [ ]', '&#x2610;')

def main(source_name='implementation-worksheet.md', output_name='implementation-worksheet.html', title='PRC Group implementation worksheet'):
    lines = (ROOT/'docs'/source_name).read_text().splitlines()
    parts = ['<section class="sheet">']; table = False; count = 0
    for line in lines:
        if line.startswith('|'):
            if not table: parts.append('<table>'); table = True
            cells = line.strip('|').split('|')
            if all(set(c.strip()) <= set('-: ') for c in cells): continue
            parts.append('<tr>' + ''.join('<td>'+inline(c.strip())+'</td>' for c in cells)+'</tr>')
            continue
        if table: parts.append('</table>'); table = False
        if line.startswith('# '): parts.append('<div class="brand">PRC · NOTE TAKING AGENT · IMPLEMENTATION</div><h1>'+inline(line[2:])+'</h1>')
        elif line.startswith('## '):
            count += 1
            break_sections = (4,) if source_name == 'sales-pilot-worksheet.md' else (3,5,7)
            if count in break_sections: parts.append('</section><section class="sheet"><div class="brand">PRC · IMPLEMENTATION WORKSHEET · CONTINUED</div>')
            parts.append('<h2>'+inline(line[3:])+'</h2>')
        elif line: parts.append('<p>'+inline(line)+'</p>')
    if table: parts.append('</table>')
    parts.append('</section>')
    css='''body{max-width:960px;margin:24px auto;padding:20px;font:16px/1.45 "Avenir Next","Segoe UI",Arial,sans-serif;color:#12212b}.brand{font-size:11px;font-weight:750;letter-spacing:.12em;color:#0967b1;border-bottom:2px solid #062840;padding-bottom:9px}h1{font-size:28px;color:#062840;margin:12px 0}h2{font-size:21px;margin:24px 0 12px;border-bottom:1px solid #b8cfdf;color:#062840}table{border-collapse:collapse;width:100%;table-layout:fixed}td{border:1px solid #ccdae3;padding:8px;vertical-align:top}td:first-child{width:64%}td:last-child{width:36%;color:#506a7b}tr:first-child{font-weight:700;background:#eaf5fb}p{overflow-wrap:anywhere}tr{break-inside:avoid}h2{break-after:avoid}.sheet{margin-bottom:32px}@media print{body{max-width:none;margin:0;padding:0;font-size:10.5pt;line-height:1.3}h1{font-size:20pt;margin:9px 0}h2{font-size:13pt;margin:17px 0 9px}td{padding:6px}p{margin:8px 0}.brand{font-size:8pt}.sheet{margin:0}.sheet+.sheet{break-before:page}*{print-color-adjust:exact;-webkit-print-color-adjust:exact}}@page{size:Letter;margin:.45in}'''
    if source_name == 'sales-pilot-worksheet.md':
        css += 'td:first-child{width:26%}td:nth-child(2){width:51%}td:last-child{width:23%}'
    page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+html.escape(title)+'</title><style>'+css+'</style><body>' + ''.join(parts) + '</body></html>'
    (ROOT/'docs'/output_name).write_text(page)
    print('Generated four-sheet printable worksheet HTML')

if __name__ == '__main__': main()
