#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
try:
    from playwright.sync_api import sync_playwright
except Exception:
    print('VISUAL VERIFY: Python Playwright not installed'); sys.exit(2)
outdir=ROOT/'release-evidence/visual-latest';outdir.mkdir(parents=True,exist_ok=True)
checks=[]
def ck(n,o,d=''):checks.append((n,bool(o),d))
transparent='data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=='
html=(ROOT/'index.html').read_text(encoding='utf-8')
for ref in sorted(set(re.findall(r'assets/[A-Za-z0-9_./-]+\.(?:png|jpg|jpeg|webp)',html)),key=len,reverse=True):html=html.replace(ref,transparent)
m=re.search(r'const MAP_ASSETS=\[(.*?)\];',html,re.S)
if m:
    block=m.group(1)
    for name in re.findall(r"['\"]([^'\"]+\.png)['\"]",block):
        block=block.replace(repr(name),repr(transparent)).replace('"'+name+'"','"'+transparent+'"')
    html=html[:m.start(1)]+block+html[m.end(1):]
with sync_playwright() as p:
    b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
    page=b.new_page(viewport={'width':1440,'height':900});page.set_default_timeout(3000);errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
    page.set_content(html,wait_until='domcontentloaded',timeout=30000);page.wait_for_timeout(250)
    ck('desktop menu visible',page.get_by_role('button',name='Play now').is_visible())
    page.screenshot(path=str(outdir/'desktop-menu-layout.png'))
    page.get_by_role('button',name='Play now').click();page.wait_for_timeout(150)
    pos=page.evaluate('''() => {const s=window.__VANTAGE__.getState(),p=s.map.buildPads[0],r=document.querySelector('#stage').getBoundingClientRect();const scale=Math.min(r.width/960,r.height/540),ox=(r.width-960*scale)/2,oy=(r.height-540*scale)/2;return{x:r.left+ox+p.x*scale,y:r.top+oy+p.y*scale};}''')
    page.mouse.click(pos['x'],pos['y']);page.wait_for_timeout(80)
    state=page.evaluate('window.__VANTAGE__.getState()');ck('tower placement interaction',len(state['towers'])==1)
    page.get_by_role('button',name='Start wave').click();page.wait_for_timeout(500)
    state=page.evaluate('window.__VANTAGE__.getState()');ck('live wave interaction',state['wave']==1 and (state['waveRunning'] or len(state['enemies'])>0))
    ck('desktop interaction page errors',not errs,str(errs));page.screenshot(path=str(outdir/'desktop-combat-layout.png'))
    page.set_viewport_size({'width':844,'height':390});page.wait_for_timeout(120)
    wave=page.locator('#waveBtn').bounding_box();ck('mobile Start wave in viewport',bool(wave) and wave['x']>=0 and wave['x']+wave['width']<=844+0.5,str(wave))
    page.evaluate('window.__VANTAGE__.exitToMenu(false)');page.wait_for_timeout(80)
    settings=page.locator('#settingsBtn').bounding_box(timeout=3000);ck('mobile Settings visible without scroll',bool(settings) and settings['y']>=0 and settings['y']+settings['height']<=390+0.5,str(settings))
    page.screenshot(path=str(outdir/'mobile-menu-layout.png'));b.close()
print('VISUAL/LAYOUT VERIFY')
for n,o,d in checks:print(('PASS' if o else 'FAIL'),n,('' if o else d))
(ROOT/'release-evidence/logs/visual-review-latest.json').write_text(json.dumps({'mode':'layout-interaction; actual art covered by asset validator + all-towers-live-visual.png','checks':[{'name':n,'pass':o,'detail':d} for n,o,d in checks]},indent=2))
sys.exit(1 if any(not o for _,o,_ in checks) else 0)
