# Waterview Build Book

Room-by-room build specifications for the DiMarino Residence,
3704 Waterview Boulevard, Ocean City, NJ.

A contractor scans the QR code at the front door, picks a floor, taps a room,
and sees every selection, fixture, model number and plan note for that room.

## What's here

| File | Purpose |
|---|---|
| `build-book.html` | The build book itself — published as a Claude Artifact |
| `site-sign.html` | Printable front-door sign with the QR code embedded |
| `qr/build-book-qr.png` | 2000px QR code for print and signage |
| `qr/build-book-qr.svg` | Vector QR code for any print size |
| `data/specs.json` | Structured specs extracted from the selections workbook |

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

Re-run the extractor against an updated workbook, re-inject the JSON into
`build-book.html`, and republish to the same artifact URL so the printed QR
codes keep working.
