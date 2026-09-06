"""List every shipped DHGR image, including combat images, in disk order."""
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--game', type=Path, default=Path('SCOSWAMP'))
args = parser.parse_args()
images = sorted((args.game / 'DHGR').rglob('*.RLE.BIN'))
if not images:
    raise SystemExit('No images for DIAPO')
paths = []
for image in images:
    if image.read_bytes()[:8] != b'DHRR\x01\x00\x00\x40':
        raise SystemExit(f'Not a DHGR stream: {image}')
    path = image.relative_to(args.game).as_posix()[:-4]
    if len(path) >= 63:
        raise SystemExit(f'Path too long: {path}')
    paths.append(path)
target = args.game / 'DIAPO'
target.mkdir(exist_ok=True)
output = target / 'DIAPO.LIST.TXT'
data = ('\r'.join(paths) + '\r').encode('ascii')
if not output.exists() or output.read_bytes() != data:
    output.write_bytes(data)
print(f'DIAPO: {len(paths)} images')

# Music and illustrations are shared with the game, never copied into DIAPO.
tracks = sorted((args.game / 'MUSIC').glob('*.MB.BIN'))
if len(tracks) > 63:
    raise SystemExit('DIAPO music catalogue exceeds 63 tracks')
titles = {'SWORDTREES': 'Sword Trees', 'WILLOWISP': 'Will-o-the-Wisp',
          'WOLFMASTER': 'Wolf Master', 'NORTHSWAMP': 'Northern Swamp',
          'SOUTHSWAMP': 'Southern Swamp', 'DEEPWATER': 'Deep Water',
          'DWARFSCORP': 'Dwarf Scorpions', 'BENTBEAKS': 'Bent Beaks'}
entries = []
for track in tracks:
    content = track.read_bytes()
    if not 8 < len(content) <= 2304 or content[:3] != b'MB1':
        raise SystemExit(f'Invalid MB1 track: {track}')
    name = track.name[:-4]
    entries.append(name + '|' + titles.get(name[:-3], name[:-3].title()))
output = target / 'MUSIC.LIST.TXT'
data = ('\r'.join(entries) + '\r').encode('ascii')
if not output.exists() or output.read_bytes() != data:
    output.write_bytes(data)
print(f'DIAPO: {len(tracks)} Mockingboard tracks')

# Ready-to-load startup metadata: no text parsing or image-list scan on Apple II.
# DIA1, uint16 image count, uint8 track count (including STOP), record size 48.
import struct
records = [('', 'STOP')]
records += [tuple(entry.split('|', 1)) for entry in entries]
if not 0 < len(paths) <= 65535:
    raise SystemExit('Invalid image count')
data = bytearray(struct.pack('<4sHBB', b'DIA1', len(paths), len(records), 48))
for name, title in records:
    if len(name) >= 16 or len(title) >= 32:
        raise SystemExit('Music metadata record too long')
    data.extend(name.encode('ascii').ljust(16, b'\0'))
    data.extend(title.encode('ascii').ljust(32, b'\0'))
output = target / 'DIAPO.DATA.BIN'
if not output.exists() or output.read_bytes() != data:
    output.write_bytes(data)

# Fixed-size image records give O(1) previous/next access and the real page title.
# Bxxx combat illustrations use the title of Nxxx, just like their scene partner.
import re
image_data = bytearray()
for path in paths:
    ident = Path(path).name[1:4]
    page = args.game / 'TEXTEN' / f'N{int(ident) // 50 * 50:03}' / f'N{ident}.TXT'
    title = ''
    if page.exists():
        for line in page.read_text(encoding='utf-8').splitlines():
            match = re.match(r'^T\s+(?:\d{3}\s+)?(.+)$', line)
            if match:
                title = match.group(1).strip()
                break
    # Some shipped illustrations have no narrative page. Label that explicitly.
    if not title:
        title = f'N{ident} - No scene title'
    title = title.encode('ascii', errors='replace')[:79]
    image_data.extend(path.encode('ascii').ljust(64, b'\0'))
    image_data.extend(title.ljust(80, b'\0'))
output = target / 'DIAPO.IMAGES.BIN'
if not output.exists() or output.read_bytes() != image_data:
    output.write_bytes(image_data)
