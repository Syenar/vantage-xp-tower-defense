#!/usr/bin/env python3
import json, math, sys, re
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'index.html').read_text(encoding='utf-8')
play=(ROOT/'play.html').read_text(encoding='utf-8')
fail=[]; rows=[]
try:
    live=json.loads(re.search(r'<script>const MAP_GEOMETRY=(.*?);</script>',html,re.S).group(1))
except Exception as e:
    print('FAIL: unable to parse live MAP_GEOMETRY',e);sys.exit(1)
maps=json.load(open(ROOT/'release-evidence/manifests/map-geometry.json'))
map_manifest=json.load(open(ROOT/'release-evidence/manifests/map-manifest.json'))
asset_match=re.search(r"const MAP_ASSETS=\[(.*?)\];",html,re.S)
assets=re.findall(r"'([^']+)'",asset_match.group(1)) if asset_match else []
if html!=play: fail.append('index.html and play.html differ')
if live!=maps: fail.append('runtime MAP_GEOMETRY differs from map-geometry.json')
if len(map_manifest)!=len(maps): fail.append('map-manifest map count differs from geometry manifest')
if len(assets)!=len(maps): fail.append(f'MAP_ASSETS has {len(assets)} entries, expected {len(maps)}')
by_id={m.get('id'):m for m in map_manifest}
for i,m in enumerate(maps):
    mm=by_id.get(m['id'])
    if not mm:
        fail.append(f"{m['id']}: missing from map-manifest.json")
    else:
        for k in ('paths','buildPads','worldSize','imageSize'):
            if mm.get(k)!=m.get(k): fail.append(f"{m['id']}: map-manifest {k} differs from live geometry")
    if i<len(assets):
        img=ROOT/'assets/maps'/assets[i]
        if not img.exists(): fail.append(f"{m['id']}: missing map image {assets[i]}")
        else:
            with Image.open(img) as im:
                actual={'width':im.width,'height':im.height}
            if actual!=m.get('imageSize'): fail.append(f"{m['id']}: image size {actual} != manifest {m.get('imageSize')}")

def segdist(px,py,ax,ay,bx,by):
    dx,dy=bx-ax,by-ay
    if dx==0 and dy==0:return math.hypot(px-ax,py-ay)
    t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy)))
    return math.hypot(px-(ax+t*dx),py-(ay+t*dy))
for m in maps:
    W,H=m['worldSize']['width'],m['worldSize']['height']
    if (W,H)!=(960,540): fail.append(f"{m['id']}: unexpected world size {W}x{H}")
    if not m['paths']:fail.append(f"{m['id']}: no paths")
    if not m['buildPads']:fail.append(f"{m['id']}: no build pads")
    for pi,p in enumerate(m['paths']):
        pts=p['points']
        if len(pts)<2:fail.append(f"{m['id']} path {pi}: <2 points");continue
        for j,q in enumerate(pts):
            if not (-30<=q['x']<=W+30 and -30<=q['y']<=H+30): fail.append(f"{m['id']} path {pi} point {j}: out of bounds {q}")
        for j,(a,b) in enumerate(zip(pts,pts[1:])):
            d=math.hypot(b['x']-a['x'],b['y']-a['y'])
            if d>260: fail.append(f"{m['id']} path {pi} segment {j}: excessive waypoint gap {d:.1f}")
    minclear=999
    for i,pad in enumerate(m['buildPads']):
        r=pad.get('radius',20)
        if not (r<=pad['x']<=W-r and r<=pad['y']<=H-r):fail.append(f"{m['id']} pad {i}: outside world")
        for j,other in enumerate(m['buildPads'][i+1:],i+1):
            if math.hypot(pad['x']-other['x'],pad['y']-other['y']) < max(r,other.get('radius',20))*1.15:
                fail.append(f"{m['id']} pads {i},{j}: overlap/duplicate")
        for path in m['paths']:
            pts=path['points']
            for a,b in zip(pts,pts[1:]):
                d=segdist(pad['x'],pad['y'],a['x'],a['y'],b['x'],b['y']);minclear=min(minclear,d)
                if d < r+3: fail.append(f"{m['id']} pad {i+1}: route centerline crosses build pad (clearance {d:.1f}, radius {r:.1f})")
    rows.append((m['id'],len(m['paths']),len(m['buildPads']),minclear))
# Artwork-specific regression guards for previously observed route shortcuts.
# These are independent of manifest/runtime synchronization: they verify that the
# traced polylines stay outside roundabout islands and do not chord across the
# Build Islands upper-right water gap.
def min_seg_distance_to_point(path,cx,cy):
    return min(segdist(cx,cy,a['x'],a['y'],b['x'],b['y']) for a,b in zip(path['points'],path['points'][1:]))

art_guards={
    'fork': {'center_source_px':(785,400),'min_world_clearance':65.0},
    'convergence': {'center_source_px':(850,460),'min_world_clearance':80.0},
}
by_geom={m['id']:m for m in maps}
for mid,guard in art_guards.items():
    m=by_geom[mid]; sx=m['worldSize']['width']/m['imageSize']['width']; sy=m['worldSize']['height']/m['imageSize']['height']
    cx=guard['center_source_px'][0]*sx; cy=guard['center_source_px'][1]*sy
    for path in m['paths']:
        clearance=min_seg_distance_to_point(path,cx,cy)
        if clearance < guard['min_world_clearance']:
            fail.append(f"{mid} {path['id']}: roundabout route cuts across central island (clearance {clearance:.1f} < {guard['min_world_clearance']:.1f})")

m=by_geom['islands']; scale_x=m['imageSize']['width']/m['worldSize']['width']; scale_y=m['imageSize']['height']/m['worldSize']['height']
for path in m['paths']:
    for j,(a,b) in enumerate(zip(path['points'],path['points'][1:])):
        sx=((a['x']+b['x'])/2)*scale_x; sy=((a['y']+b['y'])/2)*scale_y
        if 1100 < sx < 1500 and 250 < sy < 650:
            gap=math.hypot(b['x']-a['x'],b['y']-a['y'])
            if gap > 40:
                fail.append(f"islands {path['id']} segment {j}: upper-right bend shortcuts across artwork (gap {gap:.1f} > 40.0)")

# Runtime map artwork must use the same non-letterboxed world transform.
for token in ['background-size:100% 100%','updateMapArtTransform','worldPos(ev)','getCamera,setCamera,setCameraZoom']:
    if token not in html: fail.append('runtime camera/map transform missing '+token)
print('MAP GEOMETRY VALIDATION')
for r in rows:print(f"  {r[0]:12s} lanes={r[1]} pads={r[2]} min-centerline-clearance={r[3]:.1f}px")
if fail:
    print('FAIL')
    for x in fail:print(' -',x)
    sys.exit(1)
print('PASS · runtime/manifests/images synchronized')
