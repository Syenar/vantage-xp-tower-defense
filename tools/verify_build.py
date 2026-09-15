#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
fail=[]
req=['index.html','play.html','manifest.webmanifest','config.xml','package.json','tsconfig.json','vite.config.ts','tools/sync-cordova.mjs','tools/build_standalone.py']
for f in req:
    if not (ROOT/f).exists(): fail.append('missing '+f)
html=(ROOT/'index.html').read_text(encoding='utf-8')
refs=sorted(set(re.findall(r'assets/[A-Za-z0-9_./-]+\.(?:png|jpg|jpeg|webp)',html)))
for r in refs:
    if not (ROOT/r).exists(): fail.append('missing asset '+r)
# map image names are dynamic strings, validate them separately
m=re.search(r'const MAP_ASSETS=\[(.*?)\];',html,re.S)
if not m: fail.append('MAP_ASSETS missing')
else:
    for n in re.findall(r"['\"]([^'\"]+\.png)['\"]",m.group(1)):
        if not (ROOT/'assets/maps'/n).exists(): fail.append('missing map asset '+n)
try:
    manifest=json.loads((ROOT/'manifest.webmanifest').read_text())
    for icon in manifest.get('icons',[]):
        if not (ROOT/icon['src']).exists(): fail.append('missing manifest icon '+icon['src'])
except Exception as e: fail.append('manifest invalid: '+str(e))
# Extract inline JS and let Node parse it.
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',html,re.S)
inline='\n'.join(x for x in scripts if x.strip())
tmp=ROOT/'release-evidence/logs/_inline_check.js'; tmp.parent.mkdir(parents=True,exist_ok=True); tmp.write_text(inline)
r=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True)
if r.returncode: fail.append('JavaScript syntax: '+r.stderr.strip())
for tool in ['tools/validate_geometry.py','tools/validate_assets.py']:
    q=subprocess.run([sys.executable,str(ROOT/tool)],capture_output=True,text=True)
    if q.returncode: fail.append(tool+' failed: '+q.stdout+q.stderr)
print(f'BUILD VERIFY: html assets={len(refs)}')
if fail:
    print('FAIL'); [print(' -',x) for x in fail]; sys.exit(1)
print('PASS')
