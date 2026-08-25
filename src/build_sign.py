#!/usr/bin/env python3
"""Assemble the printable front-door sign from the brand lockup and the QR code.

Run from the repo root:  python3 src/build_sign.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATE = '''<title>Waterview Site Sign</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600&family=Open+Sans:ital,wght@0,400;0,600;1,400&display=swap">
<style>
  /* Achristavest brand colors, taken from achristavest.com */
  :root{
    --dove:#7cb2ca; --blue:#7eb7d0; --deep:#003b49; --head:#6c93a6;
    --grey:#58595b; --band:#e9f0f3; --line:#dbe5ea;
    --ink:#3c3d3f; --ink-2:#6b6c6f;
  }
  *{box-sizing:border-box}
  body{
    margin:0; background:var(--band); color:var(--ink);
    font-family:"Open Sans",-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
    display:grid; place-items:center; min-height:100vh; padding:26px;
  }
  .sign{background:#fff; width:100%; max-width:660px; border:1px solid var(--dove); text-align:center; padding:40px 42px 0; overflow:hidden}
  .lockup{width:230px; height:auto; margin:0 auto; display:block}
  .lockup .bird{fill:var(--dove)}
  .lockup .logoType{fill:var(--grey)}

  .doverule{display:flex; align-items:center; gap:15px; margin:26px 0 24px}
  .doverule::before,.doverule::after{content:""; height:1px; background:var(--line); flex:1}
  .doverule svg{width:28px; height:32px; flex:none; fill:var(--dove)}

  .eyebrow{font-family:Cinzel,Georgia,serif; font-size:12px; font-weight:600; letter-spacing:.19em; text-transform:uppercase; color:var(--head)}
  h1{font-family:Cinzel,Georgia,serif; font-weight:500; font-size:40px; line-height:1.12; letter-spacing:.02em; text-transform:uppercase; color:var(--deep); margin:14px 0 0}
  .addr{margin:12px 0 0; font-size:16px; color:var(--ink-2); font-style:italic}

  .qr{margin:26px auto 0; width:320px; max-width:100%; display:block; border:1px solid var(--dove); padding:15px; background:#fff}

  .cta{font-family:Cinzel,Georgia,serif; font-size:21px; font-weight:600; letter-spacing:.07em; text-transform:uppercase; color:var(--deep); margin:24px 0 0}
  .sub{margin:11px auto 0; font-size:15px; color:var(--ink-2); line-height:1.6; max-width:46ch}

  .what{margin:26px 0 32px; padding-top:24px; border-top:1px solid var(--line); display:grid; grid-template-columns:repeat(2,1fr); gap:15px 30px; text-align:left}
  .what b{display:block; font-family:Cinzel,Georgia,serif; font-size:12px; font-weight:600; letter-spacing:.1em; text-transform:uppercase; color:var(--head); margin-bottom:3px}
  .what div{font-size:13.5px; color:var(--ink-2); line-height:1.45}

  .foot{background:var(--grey); border-top:4px solid var(--blue); margin:0 -42px; padding:18px 30px 20px}
  .foot p{margin:0; color:rgba(255,255,255,.85); font-size:12.5px; line-height:1.6}
  .foot .rule-note{font-family:Cinzel,Georgia,serif; font-size:11.5px; letter-spacing:.13em; text-transform:uppercase; color:#fff; margin-bottom:6px}

  @media (max-width:560px){ .what{grid-template-columns:1fr} h1{font-size:30px} .sign{padding:30px 24px 0} .foot{margin:0 -24px} }
  @media print{
    body{background:#fff; padding:0; min-height:auto; display:block}
    .sign{border:none; max-width:none; margin:0 auto}
    @page{margin:12mm}
  }
</style>

<div class="sign">
  __LOCKUP__

  <div class="doverule">__DOVE__</div>

  <div class="eyebrow">Build Specifications</div>
  <h1>DiMarino Residence</h1>
  <p class="addr">3704 Waterview Boulevard, Ocean City, NJ</p>

  <img class="qr" src="__URI__" alt="QR code linking to the room-by-room build specifications">

  <p class="cta">Scan for room-by-room specs</p>
  <p class="sub">Every finish, fixture, model number and plan note, organized by floor and room. Tap a room to see its selections.</p>

  <div class="what">
    <div><b>Finishes &amp; paint</b>Walls, ceilings, trim, cabinetry, tile</div>
    <div><b>Plumbing &amp; appliances</b>Manufacturer and model numbers</div>
    <div><b>Lighting</b>Decorative fixtures and the E-1 schedule</div>
    <div><b>Trim &amp; millwork</b>What is in the trim contract</div>
    <div><b>Finish schedule</b>The architect&rsquo;s A-2 / A-3 / A-4 schedule</div>
    <div><b>Open items</b>What is still unselected</div>
  </div>

  <div class="foot">
    <p class="rule-note">Built by Achristavest</p>
    <p>If the booklet and the plans disagree, the design booklet governs.<br>
    Verify all model numbers against the cut sheets before ordering.</p>
  </div>
</div>
'''


def main():
    lockup = open(os.path.join(ROOT, 'brand', 'achristavest-lockup.svg')).read().strip()
    # the sign inlines the SVG directly, so CSS classes drive the fills
    lockup = lockup.replace(' fill="#7cb2ca"', '').replace(' fill="#58595B"', '')
    lockup = lockup.replace('<svg ', '<svg class="lockup" ', 1)

    dove = open(os.path.join(ROOT, 'brand', 'dove.svg')).read().strip()
    uri = open(os.path.join(ROOT, 'qr', 'qr-datauri.txt')).read().strip()

    out = (TEMPLATE.replace('__LOCKUP__', lockup)
                   .replace('__DOVE__', dove)
                   .replace('__URI__', uri))
    for token in ('__LOCKUP__', '__DOVE__', '__URI__'):
        assert token not in out, 'placeholder %s was not replaced' % token

    dest = os.path.join(ROOT, 'site-sign.html')
    open(dest, 'w').write(out)
    print('wrote %s (%d bytes)' % (dest, len(out)))


if __name__ == '__main__':
    main()
