#!/usr/bin/env python3
"""Render current runtime path/pad geometry directly over authored map art for visual review."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
GEOM=json.loads((ROOT/'release-evidence/manifests/map-geometry.json').read_text())
OUT=ROOT/'release-evidence/map-path-review'
OUT.mkdir(parents=True,exist_ok=True)
COLORS=[(76,220,255,255),(255,78,109,255),(114,255,120,255),(255,214,80,255)]
outputs=[]
for m in GEOM:
    img=Image.open(ROOT/'assets/maps'/m['image']).convert('RGBA')
    draw=ImageDraw.Draw(img,'RGBA')
    W,H=m['worldSize']['width'],m['worldSize']['height']; sx=img.width/W; sy=img.height/H
    for pi,path in enumerate(m['paths']):
        pts=[(q['x']*sx,q['y']*sy) for q in path['points']]
        col=COLORS[pi%len(COLORS)]
        draw.line(pts,fill=(0,0,0,190),width=8,joint='curve')
        draw.line(pts,fill=col,width=4,joint='curve')
        for x,y in pts: draw.ellipse((x-3,y-3,x+3,y+3),fill=(255,255,255,210))
    for i,p in enumerate(m['buildPads'],1):
        x,y,r=p['x']*sx,p['y']*sy,p.get('radius',20)*(sx+sy)/2
        draw.ellipse((x-r,y-r,x+r,y+r),outline=(255,218,90,230),width=3)
        draw.text((x-5,y-7),str(i),fill=(255,255,255,235),stroke_width=2,stroke_fill=(0,0,0,200))
    op=OUT/f"{m['id']}_overlay.png";img.save(op);outputs.append((m['id'],op))

# compact contact sheet in map order
thumbs=[]
for mid,p in outputs:
    im=Image.open(p).convert('RGB');im.thumbnail((720,405))
    canvas=Image.new('RGB',(720,430),(7,10,14));canvas.paste(im,(0,25));
    d=ImageDraw.Draw(canvas);d.text((8,6),mid,fill='white')
    thumbs.append(canvas)
cols=2;rows=(len(thumbs)+1)//2
sheet=Image.new('RGB',(1440,430*rows),(0,0,0))
for i,im in enumerate(thumbs):sheet.paste(im,((i%2)*720,(i//2)*430))
sheet.save(OUT/'all_maps_overlay_contact_sheet.jpg',quality=90)
print(f'Rendered {len(outputs)} path overlays from current map-geometry.json')
print(OUT/'all_maps_overlay_contact_sheet.jpg')
