#!/usr/bin/env python3
import json,sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
fail=[]
tm=json.load(open(ROOT/'release-evidence/manifests/tower-asset-manifest.json'))
em=json.load(open(ROOT/'release-evidence/manifests/enemy-asset-manifest-v2.json'))
if len(tm['towers'])!=10:fail.append(f"tower manifest has {len(tm['towers'])}, expected 10")
if len(em['enemies'])!=10:fail.append(f"enemy manifest has {len(em['enemies'])}, expected 10")
files=set()
def collect(x):
    if isinstance(x,dict):
        for k,v in x.items():
            if k=='file' or k.endswith('File') or k.endswith('Sheet') or k.endswith('Atlas'):
                if isinstance(v,str) and v.endswith('.png'):files.add(v)
            collect(v)
    elif isinstance(x,list):
        for v in x:collect(v)
collect(tm);collect(em)
for f in sorted(files):
    if not (ROOT/f).exists():fail.append('missing '+f)
html=(ROOT/'index.html').read_text()
for t in tm['towers']:
    if t['id'] not in html:fail.append(f"tower {t['id']} not referenced in runtime")
    if not t['projectile']['sourceRect']:fail.append(f"tower {t['id']} missing projectile crop")
for e in em['enemies']:
    if e['kind'] not in html:fail.append(f"enemy {e['kind']} not referenced in runtime")
# Hard live-renderer wiring invariants
for token in ['ART.tower.src','ART.enemy.src','ART.projectile.src','ART.milestone.src','ART.status.src','ART.towerIcon.src','PROJECTILE_RECTS','drawAtlas(ART.tower','drawAtlas(ART.enemy','drawCrop(ART.projectile']:
    if token not in html:fail.append('runtime missing '+token)
print(f"ASSET VALIDATION: towers={len(tm['towers'])}, enemies={len(em['enemies'])}, files={len(files)}")
if fail:
    print('FAIL');[print(' -',x) for x in fail];sys.exit(1)
print('PASS')
