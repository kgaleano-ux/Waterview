# Waterview Build Book

Room-by-room build specifications for the DiMarino Residence,
3704 Waterview Boulevard, Ocean City, NJ. Built by Achristavest.

A contractor scans the QR code at the front door, picks a floor, taps a room,
and sees every selection, fixture, model number and plan note for that room.

## What's here

| File | Purpose |
|---|---|
| `build-book.html` | The build book itself — **generated, do not edit by hand** |
| `site-sign.html` | Printable front-door sign — **generated** |
| `src/build-book.template.html` | Template the build book is generated from |
| `src/build.py` | Injects the logo and spec data into the template |
| `src/build_sign.py` | Builds the printable sign |
| `src/extract.py` | Reads the selections workbook into `data/specs.json` |
| `brand/` | Achristavest lockup and dove, lifted from achristavest.com |
| `qr/build-book-qr.png` | 2000px QR code for print and signage |
| `qr/build-book-qr.svg` | Vector QR code for any print size |
| `data/specs.json` | Structured specs extracted from the selections workbook |

## Brand

The build book follows the Achristavest website: the dove and wordmark are the
site's own SVG, and the palette and typography are taken from its stylesheet.

| Token | Value | Used for |
|---|---|---|
| Dove blue | `#7cb2ca` / `#7eb7d0` | Logo, hairline borders, rules |
| Deep teal | `#003b49` | Headings, room names, decisions |
| Heading blue | `#6c93a6` | Section labels, eyebrows |
| Wordmark grey | `#58595b` | Wordmark, footer band |
| Tints | `#e9f0f3` `#dcedf4` `#cee3eb` | Panels and callouts |
| Type | Cinzel + Open Sans | Headings + body |

IBM Plex Mono is added for model numbers, so strings like `T535916-4G-2MB`
are read correctly on a phone.

## Hosting

The QR code points at GitHub Pages, not at a Claude artifact - a contractor
scanning a sign must not be asked to log in to anything.

    https://kgaleano-ux.github.io/Waterview/

To turn it on: repository **Settings -> Pages -> Source: Deploy from a branch**,
pick this repository's default branch and the `/ (root)` folder, then Save.
The first build takes a minute or two.

`index.html` is the copy Pages serves. It carries `noindex, nofollow` so the
specifications do not turn up in search results. Note the repository itself is
public, so anything committed here is publicly readable.

## Rebuilding

```
python3 src/extract.py     # workbook   -> data/specs.json
python3 src/build.py       # template   -> build-book.html + index.html
node     src/build_qr.js   # target URL -> qr/  (needs: npm install qrcode)
python3 src/build_sign.py  # QR + logo  -> site-sign.html
```

The QR target lives in `src/build_qr.js`. Changing it means reprinting every
sign already hung, so leave it alone unless the book genuinely moves.

## Where the data comes from

Extracted from `DiMarino_Residence_Selections.xlsx`, which consolidates:

- the design selection booklet (64 pp)
- the OSK permit set, sheets CS-1 through M-2
- the trim & millwork bid scope

No pricing appears anywhere in the build book. Personal client notes from the
workbook's Project Notes tab are deliberately excluded, since the page is
intended for contractors on site.

## Governing rule

The design booklet supersedes any conflict within the plans. Where the permit
set adds detail the booklet is silent on, the permit set applies.

## Updating

Re-run the three build steps above, then republish to the same artifact URL so
the printed QR codes keep working.
