#!/usr/bin/env python3
from pathlib import Path
import json, sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'index.html').read_text(encoding='utf-8')
checks=[]
def ck(name, ok, detail=''):
    checks.append({'name':name,'pass':bool(ok),'detail':detail})
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None, args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1280,'height':800})
    errors=[]; page.on('pageerror', lambda e: errors.append(str(e)))
    page.set_content(HTML, wait_until='domcontentloaded', timeout=120000)
    page.wait_for_function('window.__VANTAGE__ && window.__VANTAGE__.getState()===null', timeout=120000)
    page.evaluate("window.__VANTAGE__.enterGame(); window.__VANTAGE__.newGame(0,'normal')")
    page.wait_for_timeout(100)
    init=page.evaluate("window.__VANTAGE__.getCamera()")
    ck('Camera starts at 100% centered', abs(init['zoom']-1)<1e-9 and abs(init['cx']-480)<1e-9 and abs(init['cy']-270)<1e-9, init)
    ck('Accessible camera controls exist', page.locator('#cameraZoomIn').count()==1 and page.locator('#cameraZoomOut').count()==1 and page.locator('#cameraReset').count()==1)

    # Zoom-to-cursor invariant.
    inv=page.evaluate("""() => {const A=window.__VANTAGE__,r=document.querySelector('#stage').getBoundingClientRect();let x=r.left+r.width*.58,y=r.top+r.height*.52,b=A.worldPos({clientX:x,clientY:y});A.setCameraZoom(2,x,y);let a=A.worldPos({clientX:x,clientY:y});return {b,a,c:A.getCamera()};}""")
    err=((inv['b']['x']-inv['a']['x'])**2+(inv['b']['y']-inv['a']['y'])**2)**.5
    ck('Zoom-to-cursor preserves world point', err<1e-6, {'error':err, **inv})

    # Artwork/world coordinate transform alignment.
    align=page.evaluate("""() => {const A=window.__VANTAGE__,m=document.querySelector('#mapArt').getBoundingClientRect();let tl=A.worldPos({clientX:m.left,clientY:m.top}),br=A.worldPos({clientX:m.right,clientY:m.bottom});return {tl,br,map:{left:m.left,top:m.top,width:m.width,height:m.height}};}""")
    ok_align=abs(align['tl']['x'])<.02 and abs(align['tl']['y'])<.02 and abs(align['br']['x']-960)<.02 and abs(align['br']['y']-540)<.02
    ck('Map artwork uses exact gameplay camera transform', ok_align, align)

    # API pan and clamp.
    pan=page.evaluate("""() => {const A=window.__VANTAGE__;A.setCamera(2,480,270);let b=A.getCamera();A.panCameraScreen(100,60);let a=A.getCamera();A.setCamera(99,-9999,9999);let c=A.getCamera();return {b,a,c};}""")
    ck('Pan moves camera in screen-drag direction', pan['a']['cx']<pan['b']['cx'] and pan['a']['cy']<pan['b']['cy'], pan)
    ck('Camera zoom and pan are bounded', 1<=pan['c']['zoom']<=3 and 0<=pan['c']['cx']<=960 and 0<=pan['c']['cy']<=540, pan['c'])

    # Real mouse drag pans and does not accidentally place.
    page.evaluate("window.__VANTAGE__.setCamera(2,480,270)")
    rect=page.locator('#stage').bounding_box(); cx=rect['x']+rect['width']/2; cy=rect['y']+rect['height']/2
    before=page.evaluate("({cam:window.__VANTAGE__.getCamera(),n:window.__VANTAGE__.getState().towers.length})")
    page.mouse.move(cx,cy); page.mouse.down(); page.mouse.move(cx+120,cy+60,steps=6); page.mouse.up(); page.wait_for_timeout(30)
    after=page.evaluate("({cam:window.__VANTAGE__.getCamera(),n:window.__VANTAGE__.getState().towers.length})")
    ck('Mouse drag pans battlefield', abs(after['cam']['cx']-before['cam']['cx'])>1 or abs(after['cam']['cy']-before['cam']['cy'])>1, {'before':before,'after':after})
    ck('Drag gesture never becomes a placement click', after['n']==before['n'], {'before':before['n'],'after':after['n']})

    # Click placement after arbitrary camera transform lands on exact authored pad.
    place=page.evaluate("""() => {const A=window.__VANTAGE__,s=A.getState(),p=s.map.buildPads[4]||s.map.buildPads[0];A.setCamera(2,p.x,p.y);let m=document.querySelector('#mapArt').getBoundingClientRect();return {p,x:m.left+p.x/960*m.width,y:m.top+p.y/540*m.height};}""")
    page.mouse.click(place['x'],place['y']); page.wait_for_timeout(30)
    placed=page.evaluate("window.__VANTAGE__.getState().towers.at(-1)")
    ck('Placement remains exact after zoom/pan', bool(placed) and abs(placed['x']-place['p']['x'])<1e-6 and abs(placed['y']-place['p']['y'])<1e-6, {'pad':place['p'],'tower':placed})

    # Real wheel zoom.
    page.evaluate("window.__VANTAGE__.resetCamera()")
    rect=page.locator('#stage').bounding_box(); page.mouse.move(rect['x']+rect['width']*.5,rect['y']+rect['height']*.5); page.mouse.wheel(0,-300); page.wait_for_timeout(30)
    wheel=page.evaluate("window.__VANTAGE__.getCamera()")
    ck('Mouse wheel zoom works', wheel['zoom']>1.05, wheel)

    # UI buttons and keyboard reset.
    z0=wheel['zoom']; page.click('#cameraZoomIn'); z1=page.evaluate("window.__VANTAGE__.getCamera().zoom")
    ck('Zoom-in control works', z1>z0, {'before':z0,'after':z1})
    page.keyboard.press('Home'); home=page.evaluate("window.__VANTAGE__.getCamera()")
    ck('Home resets camera', abs(home['zoom']-1)<1e-9 and abs(home['cx']-480)<1e-9 and abs(home['cy']-270)<1e-9, home)

    # Desktop strategy-game keyboard panning (WASD + arrows) must use the same bounded camera path.
    page.evaluate("window.__VANTAGE__.setCamera(2,480,270)")
    kb0=page.evaluate("window.__VANTAGE__.getCamera()")
    page.keyboard.press('KeyD'); page.keyboard.press('KeyS')
    kb1=page.evaluate("window.__VANTAGE__.getCamera()")
    ck('WASD pans the battlefield', kb1['cx']>kb0['cx'] and kb1['cy']>kb0['cy'], {'before':kb0,'after':kb1})
    page.keyboard.press('ArrowLeft'); page.keyboard.press('ArrowUp')
    kb2=page.evaluate("window.__VANTAGE__.getCamera()")
    ck('Arrow keys pan through the same camera path', kb2['cx']<kb1['cx'] and kb2['cy']<kb1['cy'], {'before':kb1,'after':kb2})

    # Synthetic touch pinch exercises the same PointerEvent path used by mobile browsers/Cordova WebView.
    pinch=page.evaluate("""() => {const st=document.querySelector('#stage'),r=st.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2,A=window.__VANTAGE__;A.resetCamera();const ev=(type,id,x,y)=>st.dispatchEvent(new PointerEvent(type,{bubbles:true,cancelable:true,pointerId:id,pointerType:'touch',button:0,buttons:type==='pointerup'?0:1,clientX:x,clientY:y}));ev('pointerdown',41,cx-55,cy);ev('pointerdown',42,cx+55,cy);ev('pointermove',41,cx-105,cy);ev('pointermove',42,cx+105,cy);let mid=A.getCamera();ev('pointerup',41,cx-105,cy);ev('pointerup',42,cx+105,cy);return mid;}""")
    ck('Two-finger pinch zoom works', pinch['zoom']>1.45, pinch)

    # Single-touch pan after zoom.
    touch=page.evaluate("""() => {const st=document.querySelector('#stage'),r=st.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2,A=window.__VANTAGE__;A.setCamera(2,480,270);let b=A.getCamera();const ev=(type,x,y)=>st.dispatchEvent(new PointerEvent(type,{bubbles:true,cancelable:true,pointerId:51,pointerType:'touch',button:0,buttons:type==='pointerup'?0:1,clientX:x,clientY:y}));ev('pointerdown',cx,cy);ev('pointermove',cx+90,cy+45);ev('pointerup',cx+90,cy+45);return {b,a:A.getCamera()};}""")
    ck('Single-touch drag pans battlefield', touch['a']['cx']<touch['b']['cx'] and touch['a']['cy']<touch['b']['cy'], touch)

    # Reset via on-screen percentage button.
    page.click('#cameraReset'); reset=page.evaluate("window.__VANTAGE__.getCamera()")
    ck('On-screen reset control returns to full-map view', abs(reset['zoom']-1)<1e-9 and abs(reset['cx']-480)<1e-9 and abs(reset['cy']-270)<1e-9, reset)
    ck('No browser JavaScript errors', not errors, errors)
    browser.close()

out=ROOT/'release-evidence/logs/camera-audit.json'; out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(checks,indent=2))
for c in checks: print(('PASS' if c['pass'] else 'FAIL'),c['name'],'' if c['pass'] else c['detail'])
fails=[c for c in checks if not c['pass']]
print(f"\nCAMERA AUDIT: {len(checks)-len(fails)}/{len(checks)} PASS")
sys.exit(1 if fails else 0)
