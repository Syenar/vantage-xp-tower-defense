#!/usr/bin/env python3
from pathlib import Path
import json,sys,time
ROOT=Path(__file__).resolve().parents[1]
try:
    from playwright.sync_api import sync_playwright
except Exception:
    print('RUNTIME VERIFY: Playwright for Python is not installed; runtime browser gate not executed.')
    sys.exit(2)
html=(ROOT/'index.html').read_text(encoding='utf-8')
checks=[]
def ck(name,ok,detail=''):
    checks.append((name,bool(ok),detail))
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None,
        args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1280,'height':800})
    errors=[]; page.on('pageerror',lambda e: errors.append(str(e)))
    page.evaluate("""() => { window.requestAnimationFrame=()=>0; window.confirm=()=>true; const mem={}; Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>Object.prototype.hasOwnProperty.call(mem,k)?mem[k]:null,setItem:(k,v)=>mem[k]=String(v),removeItem:k=>delete mem[k],clear:()=>{for(const k in mem)delete mem[k]}}}); }""")
    page.set_content(html,wait_until='domcontentloaded',timeout=30000); page.wait_for_timeout(250)
    ck('startup page errors',not errors,str(errors))
    data=page.evaluate('window.__VANTAGE__.getData()')
    ck('10 towers',len(data['towers'])==10)
    ck('10 maps',len(data['maps'])==10)
    ck('31 waves per map',all(len(m['waves'])==31 for m in data['maps']))
    combat=page.evaluate("""() => {const a=window.__VANTAGE__,D=a.getData(),out=[];for(let ti=0;ti<D.towers.length;ti++){a.newGame(0,'normal');let s=a.getState(),p=s.map.buildPads[0],t=a.placeTower(D.towers[ti].id,p.x,p.y,true);a.spawnEnemy({kind:'grunt',lane:0,hp:4,sp:.2,rw:1});let e=s.enemies[0];e.x=p.x+40;e.y=p.y;e.path={points:[{x:e.x,y:e.y},{x:e.x+100,y:e.y}]};e.seg=0;for(let k=0;k<600;k++)a.tick(1/60);out.push({id:t.type,shots:t.shots,damage:t.totalDamage,xp:t.xp});}return out;}""")
    ck('all towers attack/contribute',all(x['shots']>0 and x['damage']>0 and x['xp']>0 for x in combat),str(combat))
    save=page.evaluate("""() => {const a=window.__VANTAGE__;a.newGame(2,'hard');let s=a.getState(),p=s.map.buildPads[0],t=a.placeTower('railgun',p.x,p.y,true);t.xp=123;t.level=4;a.saveCheckpoint();a.exitToMenu(true);let ok=a.loadCheckpoint(),r=a.getState();return {ok,map:r.mapIndex,d:r.difficulty,n:r.towers.length,type:r.towers[0]?.type,xp:r.towers[0]?.xp,level:r.towers[0]?.level};}""")
    ck('checkpoint round trip',save=={'ok':True,'map':2,'d':'hard','n':1,'type':'railgun','xp':123,'level':4},str(save))
    sold=page.evaluate("""() => {window.confirm=()=>true;const a=window.__VANTAGE__;a.newGame(0,'normal');let s=a.getState(),p=s.map.buildPads[0],t=a.placeTower('ember',p.x,p.y,true);a.spawnEnemy({kind:'grunt',lane:0,hp:4,sp:.1,rw:1});let e=s.enemies[0];e.burns=[{tower:t,left:10,dps:2}];e.slowEffects=[{towerId:t.id,amount:.2,until:10,hard:false}];s.projectiles=[{tower:t,target:e.id,x:t.x,y:t.y,speed:1,dead:false}];a.sellSelected(t);return {t:s.towers.length,p:s.projectiles.length,b:e.burns.length,sl:e.slowEffects.length};}""")
    ck('sell cleanup',sold=={'t':0,'p':0,'b':0,'sl':0},str(sold))
    maps=page.evaluate("""() => {const a=window.__VANTAGE__,D=a.getData(),R=[];for(let mi=0;mi<D.maps.length;mi++){a.newGame(mi,'normal');let s=a.getState();s.lives=9999;for(let i=0;i<s.map.buildPads.length;i++){let p=s.map.buildPads[i],def=D.towers[i%D.towers.length],t=a.placeTower(def.id,p.x,p.y,true);t.xp=999999;t.level=15;}let guard=0,ticks=0;while(!s.over&&guard<31){a.startWave();let inner=0;while(s.waveRunning&&!s.over&&inner<20000){a.tick(1/60);inner++;ticks++;}if(inner>=20000)break;guard++;}R.push({map:s.map.name,wave:s.wave,victory:s.victory,lives:s.lives,running:s.waveRunning,enemies:s.enemies.length,ticks});}return R;}""")
    ck('all maps complete without deadlock',all(x['victory'] and x['wave']==31 and not x['running'] and x['enemies']==0 for x in maps),str(maps))
    ck('final page errors',not errors,str(errors))
    browser.close()
print('RUNTIME VERIFY')
for n,ok,d in checks: print(('PASS' if ok else 'FAIL'),n,('' if ok else d))
f=[x for x in checks if not x[1]]
(ROOT/'release-evidence/logs/runtime-review-latest.json').write_text(json.dumps({'checks':[{'name':n,'pass':o,'detail':d} for n,o,d in checks],'combat':combat,'maps':maps},indent=2))
sys.exit(1 if f else 0)
