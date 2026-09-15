#!/usr/bin/env python3
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
if DIST.exists(): shutil.rmtree(DIST)
DIST.mkdir()
for f in ['index.html','manifest.webmanifest']:
    shutil.copy2(ROOT/f,DIST/f)
shutil.copytree(ROOT/'assets',DIST/'assets')
print(f'Static web build: {DIST}')
