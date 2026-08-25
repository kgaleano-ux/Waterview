/* Generates the QR codes that point at the published build book.
 *
 *   npm install qrcode
 *   node src/build_qr.js
 *
 * Change TARGET if the book ever moves, then re-run this and build_sign.py
 * and reprint the sign - the old printed codes will not follow it.
 */
const QR = require('qrcode');
const fs = require('fs');
const path = require('path');

const TARGET = 'https://kgaleano-ux.github.io/Waterview/';

const ROOT = path.dirname(__dirname);
const OUT = path.join(ROOT, 'qr');

// Level Q tolerates ~25% damage, which a sign on a job site will collect.
const OPTS = { errorCorrectionLevel: 'Q', color: { dark: '#003b49', light: '#FFFFFF' } };

(async () => {
  fs.mkdirSync(OUT, { recursive: true });

  await QR.toFile(path.join(OUT, 'build-book-qr.png'), TARGET,
    Object.assign({ margin: 2, width: 2000 }, OPTS));

  const svg = await QR.toString(TARGET, Object.assign({ margin: 2, type: 'svg' }, OPTS));
  fs.writeFileSync(path.join(OUT, 'build-book-qr.svg'), svg);

  // data URI keeps the printable sign a single self-contained file
  const uri = await QR.toDataURL(TARGET, Object.assign({ margin: 1, width: 900 }, OPTS));
  fs.writeFileSync(path.join(OUT, 'qr-datauri.txt'), uri);

  fs.writeFileSync(path.join(OUT, 'TARGET.txt'), TARGET + '\n');
  console.log('QR codes point at: ' + TARGET);
})();
