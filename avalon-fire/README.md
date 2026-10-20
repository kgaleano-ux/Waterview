# Avalon Volunteer Fire Department: website rebuild

A rebuild of https://avalonfiredept.com as a plain static site, with no build
step and no site builder. Every page works as-is on any static host (GitHub
Pages, Netlify, or regular web hosting) and on phones.

## Pages

| File | Replaces |
|---|---|
| `index.html` | `/index.html` (home: raffle results, officers, safety, preparedness, join) |
| `apparatus.html` | `/apparatus.html` |
| `water-rescue.html` | `/water-rescue.html` (blank on the old site; now a "coming soon" page) |
| `photos.html` | `/photos.html` |
| `store-and-raffles.html` | `/store-and-raffles.html` (donate, 9-11 print, raffle, 2020 ticket list) |
| `links.html` | `/links.html` |

The file names match the old site, so existing links and bookmarks still work
after the switch.

Shared files: `assets/site.css` (all styling), `assets/site.js` (mobile menu,
photo viewer, ticket search), `assets/favicon.svg`. The header and footer are
repeated in each page, so a change to them has to be made in all six files.

## What changed from the old site

- Responsive layout with a mobile menu, a sticky header and a "Call 911" strip.
- Photos are resized and compressed (all images together come to about 6.5 MB).
  Tap any photo to open it full size.
- The main gallery on the old Photos page was titled "100th Anniversary", but
  the photos actually show the **February 12, 2015 fire on 5th Avenue**, so it
  is now labelled that way. The other incident galleries were empty on the old
  site and appear as a timeline until their photos are found.
- Dropped: hit counters, the web-host ad banner, and clip-art images.
- Dead federal links (citizencorps.gov, old NJOEM pages) now point to
  Ready.gov, ready.nj.gov and FEMA. The local links are unchanged.
- The PayPal Donate button uses the same hosted button ID as before
  (`Q3FXSQZZNUKZW`).

## To update each year

- **Officers:** the "Command staff" card in `index.html`.
- **Raffle results:** the `prize-list` block appears in both `index.html` and
  `store-and-raffles.html`. Update both, including the license number.
