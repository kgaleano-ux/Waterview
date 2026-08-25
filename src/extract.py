import zipfile, json, re
import xml.etree.ElementTree as ET

N = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
SRC = '/root/.claude/uploads/1fe5ef47-cb42-5f7e-818b-325b36c230a9/1a0a243e-DiMarino_Residence_Selections.xlsx'
z = zipfile.ZipFile(SRC)

ss = []
sst = ET.fromstring(z.read('xl/sharedStrings.xml'))
for si in sst:
    ss.append(''.join(t.text or '' for t in si.iter(N + 't')))

SHEETS = {'Summary': 'sheet1', 'Selections': 'sheet2', 'Room Finish Schedule': 'sheet3',
          'Decisions': 'sheet4', 'Trim & Millwork Scope': 'sheet5',
          'Plumbing & Appliances': 'sheet6', 'Lighting': 'sheet7',
          'Open Items': 'sheet8', 'Project Notes': 'sheet9'}


def colnum(ref):
    c = ''.join(ch for ch in ref if ch.isalpha())
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n


def rows(sheet):
    root = ET.fromstring(z.read('xl/worksheets/%s.xml' % SHEETS[sheet]))
    out = []
    for row in root.iter(N + 'row'):
        cells = {}
        for c in row.iter(N + 'c'):
            t = c.get('t')
            v = c.find(N + 'v')
            isv = c.find(N + 'is')
            if t == 's' and v is not None:
                val = ss[int(v.text)]
            elif t == 'inlineStr' and isv is not None:
                val = ''.join(x.text or '' for x in isv.iter(N + 't'))
            elif v is not None:
                val = v.text
            else:
                val = ''
            if val not in ('', None):
                cells[colnum(c.get('r'))] = str(val).strip()
        out.append((int(row.get('r')), cells))
    return out


def table(sheet, header_row):
    """Rows below header_row as lists indexed from col 1."""
    out = []
    for r, cells in rows(sheet):
        if r <= header_row or not cells:
            continue
        mx = max(cells)
        out.append([cells.get(i, '') for i in range(1, mx + 1)])
    return out


def g(row, i):
    return row[i] if i < len(row) else ''


def norm_floor(f):
    f = f.strip()
    if f.startswith('Third Floor'):
        return 'Third Floor'
    if f == 'Ground Floor':
        return 'Exterior'
    return f


rooms = {}   # key -> room dict
order = []

# Cross-room / legend labels folded into the real rooms a contractor looks for.
# A value of None drops the row (plan legends carry no spec).
ALIAS = {
    'First Floor|All - Legend': None,
    'Second Floor|All - Legend': None,
    'First Floor|Laundry / Bath': 'First Floor|Laundry (1st Fl)',
    'First Floor|Bathroom 1 / Hall': 'First Floor|Bathroom 1',
    'First Floor|All': 'Whole House|Interior Details',
    'Second Floor|Kitchen / Pantry / Hall': 'Second Floor|Kitchen',
    'Second Floor|Kitchen / Dining': 'Second Floor|Kitchen',
    'Second Floor|Kitchen Bar': 'Second Floor|Kitchen',
    'Second Floor|Living Room / Porch': 'Second Floor|Living Room',
    'Second Floor|Bedroom 4 / Laundry': 'Second Floor|Bedroom 4',
    'Second Floor|Sitting Room Balcony': 'Second Floor|Sitting Room (2nd Fl)',
    'Third Floor|Stair Landing': 'Third Floor|3rd Fl Stair Hall',
    'Third Floor|Primary Bath Niche': 'Third Floor|Primary Bath',
    'Third Floor|Primary Suite': 'Exterior|Outdoor Shower',
    'Third Floor|Exterior Balcony': 'Exterior|Decks',
    'Exterior|Exterior - Sides': 'Exterior|Front Exterior',
    'Exterior|Exterior - Garage': 'Exterior|Front Exterior',
    'Exterior|Exterior Walls': 'Exterior|Front Exterior',
    'Exterior|Deck / Patio': 'Exterior|Decks',
    'Exterior|Driveway': 'Whole House|Electrical',
    'Exterior|Away from house': 'Whole House|Electrical',
    'Whole House|Network room': 'Whole House|Electrical',
    'Whole House|Bedroom Doors': 'Whole House|Interior Details',
    'Whole House|Doors': 'Whole House|Interior Details',
    'Whole House|Millwork': 'Whole House|Interior Details',
    'Whole House|All': 'Whole House|Electrical',
}

# Rows tagged to several rooms at once get copied into each.
FANOUT = {'Second Floor|Kitchen / Dining / Living': [
    'Second Floor|Kitchen', 'Second Floor|Dining Room / Wine Bar', 'Second Floor|Living Room']}

DROPPED = object()


def room(floor, name):
    floor = norm_floor(floor)
    key = floor + '|' + name
    if key in ALIAS:
        if ALIAS[key] is None:
            return {'selections': [], 'plumbing': [], 'lighting': [], 'openItems': [],
                    'decisions': [], 'trim': [], 'schedule': []}
        key = ALIAS[key]
        floor, name = key.split('|')
    if key not in rooms:
        rooms[key] = {'key': key, 'floor': floor, 'name': name, 'selections': [],
                      'plumbing': [], 'lighting': [], 'openItems': [], 'decisions': [],
                      'trim': [], 'schedule': []}
        order.append(key)
    return rooms[key]


# ---- Selections: Ref | Floor | Room/Area | Category | Selection | Notes | Source | Flag
for row in table('Selections', 4):
    ref, floor, rm, cat, sel = (g(row, 0), g(row, 1), g(row, 2), g(row, 3), g(row, 4))
    if not rm or not cat:
        continue
    room(floor, rm)['selections'].append({
        'ref': ref, 'category': cat, 'selection': sel,
        'notes': g(row, 5), 'source': g(row, 6), 'flag': g(row, 7)})

# ---- Plumbing: Page | Room/Area | Type | Manufacturer/Model | Qty | Finish
for row in table('Plumbing & Appliances', 4):
    rm = g(row, 1)
    if not rm:
        continue
    fl = {'Laundry (1st Fl)': 'First Floor', 'Powder Room (1st Fl)': 'First Floor',
          'Family Room Bar': 'First Floor', 'Bathroom 1': 'First Floor',
          'Bathroom 2': 'First Floor', 'Bathroom 3': 'First Floor',
          'Kitchen': 'Second Floor', 'Pantry': 'Second Floor',
          'Powder Room (2nd Fl)': 'Second Floor', 'Laundry (2nd Fl)': 'Second Floor',
          'Bathroom 4': 'Second Floor', 'Primary Bath': 'Third Floor',
          'Outdoor Shower': 'Exterior'}.get(rm, 'Whole House')
    room(fl, rm)['plumbing'].append({
        'ref': g(row, 0), 'type': g(row, 2), 'model': g(row, 3),
        'qty': g(row, 4), 'finish': g(row, 5)})

# ---- Lighting: Ref | Floor | Room/Area | Fixture Type | Description | Qty | Notes | Flag
for row in table('Lighting', 4):
    floor, rm = g(row, 1), g(row, 2)
    if not rm:
        continue
    room(floor, rm)['lighting'].append({
        'ref': g(row, 0), 'type': g(row, 3), 'description': g(row, 4),
        'qty': g(row, 5), 'notes': g(row, 6), 'flag': g(row, 7)})

# ---- Open Items: Ref | Floor | Room/Area | Item | Type | Detail | Status | Closed By
open_items = []
for row in table('Open Items', 4):
    floor, rm = g(row, 1), g(row, 2)
    if not rm:
        continue
    it = {'ref': g(row, 0), 'floor': norm_floor(floor), 'room': rm, 'item': g(row, 3),
          'type': g(row, 4), 'detail': g(row, 5), 'status': g(row, 6).upper(),
          'closedBy': g(row, 7)}
    open_items.append(it)
    fan = FANOUT.get(norm_floor(floor) + '|' + rm)
    if fan:
        for k in fan:
            fl, nm = k.split('|')
            room(fl, nm)['openItems'].append(it)
    else:
        room(floor, rm)['openItems'].append(it)

# ---- Room Finish Schedule
SCHED_MAP = {
    '101': 'First Floor|Foyer', '102': 'First Floor|Hall 102',
    '103': 'First Floor|Laundry (1st Fl)', '104': 'First Floor|Powder Room (1st Fl)',
    '105': 'First Floor|Bedroom 1', '106': 'First Floor|Bathroom 1',
    '106a': 'First Floor|Bathroom 1', '107': 'First Floor|Family Room',
    '108': 'First Floor|Dining / Bar (1st Fl)', '109': 'First Floor|Vestibule 109',
    '110': 'First Floor|Bunk Bedroom 2', '111': 'First Floor|Bathroom 2',
    '111b': 'First Floor|Bathroom 2', '111c': 'First Floor|Bathroom 2',
    '112': 'First Floor|Bedroom 3', '113': 'First Floor|Bathroom 3',
    '201': 'Second Floor|2nd Fl Stair', '202': 'Second Floor|Sitting Room (2nd Fl)',
    '203': 'Second Floor|Hall (2nd Fl)', '204': 'Second Floor|Vestibule 204',
    '205': 'Second Floor|Powder Room (2nd Fl)', '206': 'Second Floor|Laundry (2nd Fl)',
    '207': 'Second Floor|Mech Closet 207', '208': 'Second Floor|Bedroom 4',
    '209': 'Second Floor|Bathroom 4', '209a': 'Second Floor|Bathroom 4',
    '210': 'Second Floor|Living Room', '211': 'Second Floor|Dining Room / Wine Bar',
    '212': 'Second Floor|Pantry', '213': 'Second Floor|Kitchen',
    '301': 'Third Floor|3rd Fl Stair Hall', '302': 'Third Floor|Office / Sitting Room',
    '303': 'Third Floor|Primary Hall / Exercise', '304': 'Third Floor|Primary Hall / Exercise',
    '305': 'Third Floor|Primary Suite Closets', '306': 'Third Floor|Primary Suite Closets',
    '307': 'Third Floor|Dressing Room', '308': 'Third Floor|Primary Bedroom',
    '309': 'Third Floor|Primary Bath', '309a': 'Third Floor|Primary Bath',
}

legend, remarks = [], []
mode = 'rows'
for r, cells in rows('Room Finish Schedule'):
    if not cells:
        continue
    first = cells.get(1, '')
    if first == 'LEGEND':
        mode = 'legend'
        continue
    if first == 'REMARKS':
        mode = 'remarks'
        continue
    if r <= 4:
        continue
    if mode == 'legend':
        legend.append({'code': first, 'meaning': cells.get(2, '')})
    elif mode == 'remarks':
        remarks.append({'code': first, 'text': cells.get(2, '')})
    else:
        no = cells.get(3, '')
        entry = {'sheet': first, 'floor': norm_floor(cells.get(2, '')), 'no': no,
                 'roomName': cells.get(4, ''), 'floorFin': cells.get(5, ''),
                 'base': cells.get(6, ''), 'walls': cells.get(7, ''),
                 'ceiling': cells.get(8, ''), 'clgHt': cells.get(9, ''),
                 'remarks': cells.get(10, ''), 'override': cells.get(11, '')}
        tgt = SCHED_MAP.get(no)
        if tgt:
            fl, nm = tgt.split('|')
            room(fl, nm)['schedule'].append(entry)

# ---- Decisions
DEC_MAP = {
    '1': ['Second Floor|Bathroom 4'], '2': ['Third Floor|Primary Bath'],
    '3': ['Second Floor|Kitchen'], '4': ['First Floor|Bunk Bedroom 2'],
    '5': ['Second Floor|Kitchen', 'Second Floor|Dining Room / Wine Bar'],
    '6': ['Third Floor|Primary Bedroom'], '7': ['Third Floor|Primary Bath'],
    '8': ['Second Floor|Living Room'],
}
decisions = []
for row in table('Decisions', 4):
    num = g(row, 0)
    if not num or not num.isdigit():
        continue
    d = {'n': num, 'item': g(row, 1), 'said': g(row, 2), 'decision': g(row, 3),
         'basis': g(row, 4), 'status': g(row, 5)}
    # some rows carry an extra column (3 source variants) -> decision shifts right
    if len(row) > 6 and g(row, 6):
        d = {'n': num, 'item': g(row, 1), 'said': g(row, 2) + ' / ' + g(row, 3),
             'decision': g(row, 4), 'basis': g(row, 5), 'status': g(row, 6)}
    decisions.append(d)
    for k in DEC_MAP.get(num, []):
        fl, nm = k.split('|')
        room(fl, nm)['decisions'].append(d)

# ---- Trim & Millwork
TRIM_KEYS = [
    ('laundry 103', 'First Floor|Laundry (1st Fl)'),
    ('laundry 206', 'Second Floor|Laundry (2nd Fl)'),
    ('foyer/stairhall', 'First Floor|Foyer'),
    ('bunkroom', 'First Floor|Bunk Bedroom 2'),
    ('bunk', 'First Floor|Bunk Bedroom 2'),
    ('family room', 'First Floor|Family Room'),
    ('living room', 'Second Floor|Living Room'),
    ('kitchen/dining', 'Second Floor|Kitchen'),
    ('dining room/kitchen', 'Second Floor|Kitchen'),
    ('kitchen pantry', 'Second Floor|Pantry'),
    ('pantry', 'Second Floor|Pantry'),
    ('master bedroom', 'Third Floor|Primary Bedroom'),
    ('master bathroom', 'Third Floor|Primary Bath'),
    ('hall 303', 'Third Floor|Primary Hall / Exercise'),
    ('stair landing 301', 'Third Floor|3rd Fl Stair Hall'),
    ('cupola', 'Third Floor|3rd Fl Stair Hall'),
    ('sitting room 302', 'Third Floor|Office / Sitting Room'),
    ('hall 102', 'First Floor|Hall 102'),
]
trim = []
for row in table('Trim & Millwork Scope', 4):
    sec, line = g(row, 0), g(row, 1)
    if not line:
        continue
    t = {'section': sec, 'line': line, 'material': g(row, 2), 'qty': g(row, 3),
         'note': g(row, 4)}
    trim.append(t)
    low = line.lower()
    hit = set()
    for kw, key in TRIM_KEYS:
        if kw in low and key not in hit:
            hit.add(key)
            fl, nm = key.split('|')
            room(fl, nm)['trim'].append(t)
    # kitchen/dining ceiling lines belong to both rooms
    if 'kitchen' in low and 'dining' in low:
        for key in ('Second Floor|Dining Room / Wine Bar',):
            if key not in hit:
                fl, nm = key.split('|')
                room(fl, nm)['trim'].append(t)

# ---- Summary sheet: house-wide standards + status
standards, status = [], []
mode = None
for r, cells in rows('Summary'):
    first = cells.get(1, '')
    if first == 'HOUSE-WIDE STANDARDS':
        mode = 'std'
        continue
    if first == 'WHERE THINGS STAND':
        mode = 'status'
        continue
    if first in ('WORKBOOK CONTENTS', 'GOVERNING RULE'):
        mode = None
        continue
    if not first:
        continue
    if mode == 'std':
        standards.append({'item': first, 'spec': cells.get(2, ''), 'ref': cells.get(3, '')})
    elif mode == 'status':
        status.append({'label': first, 'value': cells.get(2, ''), 'note': cells.get(3, '')})

# ---- Project notes: allowances only (client personal notes intentionally excluded)
allowances = []
grab = False
for r, cells in rows('Project Notes'):
    first = cells.get(1, '')
    if first.startswith('Allowance categories'):
        grab = True
        continue
    if first == 'Client Notes':
        grab = False
        continue
    if grab and first:
        allowances.append(first)

FLOOR_ORDER = ['Exterior', 'First Floor', 'Second Floor', 'Third Floor', 'Whole House']


def count(rm):
    return (len(rm['selections']) + len(rm['plumbing']) + len(rm['lighting']) +
            len(rm['trim']) + len(rm['schedule']))


room_list = [rooms[k] for k in order]
for rm in room_list:
    rm['openCount'] = sum(1 for i in rm['openItems'] if i['status'] == 'OPEN')
    rm['itemCount'] = count(rm)
room_list = [r for r in room_list if r['itemCount'] or r['openItems']]
room_list.sort(key=lambda r: (FLOOR_ORDER.index(r['floor']) if r['floor'] in FLOOR_ORDER else 9,
                              r['name']))

data = {
    'project': {
        'name': 'DiMarino Residence',
        'address': '3704 Waterview Boulevard, Ocean City, NJ',
        'architect': 'OSK Design Partners, PA',
        'builder': 'Achristavest',
        'interiors': 'Stephanie Kraus Designs',
        'sources': 'Design selection booklet (64 pp), OSK permit set CS-1 through M-2, and the trim & millwork bid scope. No pricing in this document.',
        'rule': 'The design booklet supersedes any conflict within the plans. Where the permit set adds detail the booklet is silent on, the permit set applies.',
    },
    'floors': FLOOR_ORDER,
    'rooms': room_list,
    'standards': standards,
    'status': status,
    'decisions': decisions,
    'trim': trim,
    'openItems': open_items,
    'legend': legend,
    'remarks': remarks,
    'allowances': allowances,
}

out = '/tmp/claude-0/-home-user-Waterview/1fe5ef47-cb42-5f7e-818b-325b36c230a9/scratchpad/data.json'
with open(out, 'w') as f:
    json.dump(data, f, separators=(",",":"))

print('rooms:', len(room_list))
for fl in FLOOR_ORDER:
    rs = [r for r in room_list if r['floor'] == fl]
    print(' ', fl, len(rs), '|', ', '.join('%s(%d/%d)' % (r['name'], r['itemCount'], r['openCount']) for r in rs))
print('open OPEN:', sum(1 for i in open_items if i['status'] == 'OPEN'), 'of', len(open_items))
print('decisions:', len(decisions), 'trim:', len(trim), 'standards:', len(standards), 'legend:', len(legend), 'remarks:', len(remarks))
import os
print('bytes:', os.path.getsize(out))
