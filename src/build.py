#!/usr/bin/env python3
"""Assemble build-book.html from the template, the brand logo defs and the spec data.

Run from the repo root:  python3 src/build.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    tpl = open(os.path.join(ROOT, 'src', 'build-book.template.html')).read()
    defs = open(os.path.join(ROOT, 'brand', 'logo-defs.svg')).read()
    raw = open(os.path.join(ROOT, 'data', 'specs.json')).read()

    json.loads(raw)  # fail loudly on malformed data rather than shipping it

    # keep the JSON safe inside a <script> block
    payload = raw.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')

    out = tpl.replace('__LOGO_DEFS__', defs).replace('__DATA__', payload)
    for token in ('__LOGO_DEFS__', '__DATA__'):
        assert token not in out, 'placeholder %s was not replaced' % token

    dest = os.path.join(ROOT, 'build-book.html')
    open(dest, 'w').write(out)
    print('wrote %s (%d bytes)' % (dest, len(out)))

    # GitHub Pages serves the same page at the site root. It carries a noindex
    # tag so a client's specifications don't turn up in search results.
    noindex = '<meta name="robots" content="noindex, nofollow">\n'
    viewport = '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    page = os.path.join(ROOT, 'index.html')
    open(page, 'w').write(noindex + viewport + out)
    print('wrote %s (%d bytes)' % (page, len(out)))


if __name__ == '__main__':
    main()
