"""Builds report/team-E-p4.pdf from report/team-E-p4.md: Markdown -> HTML -> PDF (headless Chromium).

  pip install markdown
  python report/build_report.py

Needs a `chromium` (or `google-chrome`) binary on the PATH. Images are read from ../out/.
"""
import os
import shutil
import subprocess
import sys

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'team-E-p4.md')
HTML = os.path.join(HERE, 'team-E-p4.html')      # intermediate, removed at the end
PDF = os.path.join(HERE, 'team-E-p4.pdf')

CSS = """
@page { size: A4; margin: 20mm 17mm 20mm 17mm;
        @bottom-center { content: counter(page); font: 9pt 'Liberation Serif', serif; color: #444; } }
@page :first { @bottom-center { content: none; } }
html { font: 10.5pt/1.42 'Liberation Serif', 'Times New Roman', serif; color: #111; }
body { margin: 0; }
h1 { font-size: 16pt; margin: 0 0 8pt; padding-bottom: 3pt; border-bottom: 1px solid #555;
     margin-top: 20pt; break-after: avoid; }
h2 { font-size: 12.5pt; margin: 14pt 0 5pt; break-after: avoid; }
p, li { text-align: justify; orphans: 3; widows: 3; }
p { margin: 0 0 7pt; }
ul, ol { margin: 0 0 7pt; padding-left: 18pt; }
li { margin-bottom: 2.5pt; }
code { font: 8.6pt 'Liberation Mono', monospace; overflow-wrap: anywhere; }
pre { background: #f5f5f5; border: 1px solid #ccc; padding: 5pt 6pt; margin: 0 0 8pt;
      white-space: pre-wrap; overflow-wrap: anywhere; }
pre code { font-size: 7.4pt; line-height: 1.3; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 9pt; font-size: 8.8pt; line-height: 1.28; }
th, td { border: 1px solid #666; padding: 2.5pt 4pt; vertical-align: top; text-align: left;
         overflow-wrap: break-word; }
th { background: #e6e6e6; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
table code { font-size: 7.4pt; }
.small table { font-size: 7.6pt; }
.small table code { font-size: 6.7pt; }
img { display: block; max-width: 100%; margin: 6pt auto 3pt; break-inside: avoid; }
p:has(> img) { break-inside: avoid; }
p > img + em { display: block; text-align: center; font-size: 9pt; }
.cover { text-align: center; padding-top: 38mm; break-after: page; }
.cover p { text-align: center; }
.cover-course { font-size: 12pt; letter-spacing: .5pt; }
.cover-title { font-size: 24pt; font-weight: bold; margin: 26mm 0 6mm; }
.cover-sub { font-size: 13pt; margin-bottom: 26mm; }
.cover-block { font-size: 11.5pt; margin-bottom: 14mm; line-height: 1.5; }
"""


def main():
    with open(SRC, encoding='utf-8') as f:
        body = markdown.markdown(f.read(), extensions=['tables', 'fenced_code', 'md_in_html', 'sane_lists'])
    with open(HTML, 'w', encoding='utf-8') as f:
        f.write(f'<!doctype html><html lang="es"><head><meta charset="utf-8">'
                f'<title>team-E-p4 – Verificación arquitectónica del SoS</title>'
                f'<style>{CSS}</style></head><body>{body}</body></html>')
    browser = next((b for b in ('chromium', 'chromium-browser', 'google-chrome') if shutil.which(b)), None)
    if not browser:
        sys.exit('chromium not found; the HTML is in ' + HTML)
    subprocess.run([browser, '--headless', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                    f'--print-to-pdf={PDF}', 'file://' + HTML], check=True, stderr=subprocess.DEVNULL)
    os.remove(HTML)
    print(PDF)


if __name__ == '__main__':
    main()
