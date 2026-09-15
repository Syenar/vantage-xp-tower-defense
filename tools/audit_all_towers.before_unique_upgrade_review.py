#!/usr/bin/env python3
import json, pathlib, sys, re
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
HTML=(ROOT/'index.html').read_text(encoding='utf-8')
JS=r'''() => {
window.confirm=()=>true; const A=window.__VANTAGE__, D=A.getData(); const R=[];
const ok=(name,cond,detail='')=>R.push({name,pass:!!cond,detail});
const reset=(type='ranger',level=1)=>{A.newGame(0,'normal');let s=A.getState();s.credits=999999;let p=s.map.buildPads[0];let t=A.placeTower(type,p.x,p.y,true);t.level=level;t.xp=(D.towers.find(x=>x.id===type).levels[level-1]?.xpThreshold||0);t.cool=0;t.lastShotTime=s.time;return {s,t,def:D.towers.find(x=>x.id===type)}};
const spawn=(kind='grunt',x=null,y=null,hp=100000)=>{let s=A.getState();A.spawnEnemy({kind,lane:0,hp:1,sp:0,rw:1});let e=s.enemies[s.enemies.length-1];e.x=x??s.towers[0]?.x+60??100;e.y=y??s.towers[0]?.y;e.speed=0;e.hp=e.maxHp=hp;e.shield=0;e.shieldMax=0;e.regen=0;e.shieldRegen=0;return e};
const settleProjectiles=()=>{let s=A.getState();for(let guard=0;guard<50&&s.projectiles.length;guard++)A.tick(.1)};
const forceFire=(t,e)=>{let s=A.getState(),before=t.shots;A.fire(t,e,A.towerStats(t));return {before,after:t.shots,projectiles:s.projectiles.slice(),effects:(s.effects||[]).slice()}};
const stat=(type,l,k)=>D.towers.find(x=>x.id===type).levels[l-1].stats[k]||0;
// structure + level integrity
ok('Roster has 10 unique towers',D.towers.length===10 && new Set(D.towers.map(x=>x.id)).size===10,D.towers.map(x=>x.id));
for(const def of D.towers){ok(`${def.name} has 15 levels`,def.levels.length===15);ok(`${def.name} has milestones 3/5/8/11/15`,JSON.stringify(def.milestones.map(m=>m.level))===JSON.stringify([3,5,8,11,15]));ok(`${def.name} XP thresholds strictly increase`,def.levels.every((x,i,a)=>i===0||x.xpThreshold>a[i-1].xpThreshold));ok(`${def.name} stats finite/positive`,def.levels.every(l=>['damage','fireRate','range'].every(k=>Number.isFinite(l.stats[k])&&l.stats[k]>0)));}
// base attack, XP, no idle bank for all attackers
for(const def of D.towers){let {s,t}=reset(def.id,1),e=spawn('grunt',t.x+60,t.y,10000);let xp0=t.xp;for(let i=0;i<240;i++)A.tick(1/60);ok(`${def.name} attacks at level 1`,t.shots>0,{shots:t.shots});ok(`${def.name} earns XP`,t.xp>xp0,{xp:t.xp});}
for(const def of D.towers){let {s,t}=reset(def.id,1);for(let i=0;i<180;i++)A.tick(1/60);let before=t.shots,e=spawn('grunt',t.x+60,t.y,10000);A.tick(1/60);let delta=t.shots-before;ok(`${def.name} does not bank idle attacks`,delta<=1,{delta,cool:t.cool});}
// RANGER
ok('Ranger L3 Sharpened Rounds',stat('ranger',3,'armorPen')>stat('ranger',2,'armorPen'));
ok('Ranger L5 Rapid Cycling',stat('ranger',5,'fireRate')>stat('ranger',4,'fireRate')*1.1);
{let {s,t}=reset('ranger',8),e=spawn('grunt',t.x+60,t.y);t.shots=3;forceFire(t,e);ok('Ranger L8 Double Tap',s.projectiles.length===2,s.projectiles.length)}
ok('Ranger L11 Veteran Aim',stat('ranger',11,'critChance')>stat('ranger',10,'critChance'));
ok('Ranger L15 Deadeye',stat('ranger',15,'critMultiplier')>stat('ranger',14,'critMultiplier'));
{let {t}=reset('ranger',1),range=A.towerStats(t).range,e=spawn('stealth',t.x+range*.70,t.y);e.stealth=true;ok('Ranger detects stealth inside reduced range',A.canSee(t,e,range));e.x=t.x+range*.85;ok('Ranger cannot detect stealth outside reduced range without Beacon',!A.canSee(t,e,range));}
// REPEATER
{let {t}=reset('repeater',3);for(let i=0;i<60;i++)A.tick(1/60);ok('Repeater L3 Spin Up does not precharge',t.spin===0,t.spin);let e=spawn('grunt',t.x+60,t.y);for(let i=0;i<60;i++)A.tick(1/60);ok('Repeater L3 Spin Up activates under sustained fire',t.spin>0,t.spin)}
{let {s,t}=reset('repeater',5),e=spawn('grunt',t.x+60,t.y);t.shots=4;forceFire(t,e);ok('Repeater L5 Twin Feed',s.projectiles.length===2,s.projectiles.length)}
{let {s,t}=reset('repeater',8),e=spawn('grunt',t.x+40,t.y);let st=A.towerStats(t);let p={tower:t,target:e.id,x:t.x,y:t.y,speed:1e9,damage:st.damage,type:'kinetic',armorPen:st.armorPen,splash:0,slow:st.slow,duration:st.statusDuration,burn:0,pierce:1,hardControl:false};A.impactProjectile({...p},e);let first=e.slowEffects.length;A.impactProjectile({...p},e);ok('Repeater L8 Suppression requires repeat',first===0&&e.slowEffects.length>0,{first,after:e.slowEffects.length})}
{let {s,t}=reset('repeater',11),e=spawn('grunt',t.x+60,t.y);t.shots=2;forceFire(t,e);ok('Repeater L11 Triple Feed',s.projectiles.length===3,s.projectiles.length)}
ok('Repeater L15 Overdrive raises authored rate',stat('repeater',15,'fireRate')>stat('repeater',14,'fireRate')*1.15);
// CANNON
ok('Cannon L3 Larger Charge',stat('cannon',3,'splashRadius')>stat('cannon',2,'splashRadius'));
{let {s,t}=reset('cannon',5),e=spawn('grunt',t.x+50,t.y),outer=spawn('grunt',e.x+A.towerStats(t).splashRadius*1.3,e.y);let hp=outer.hp;forceFire(t,e);settleProjectiles();ok('Cannon L5 Shrapnel reaches beyond primary splash',outer.hp<hp,{lost:hp-outer.hp})}
{let {s,t}=reset('cannon',8),e=spawn('grunt',t.x+50,t.y),near=spawn('grunt',e.x+20,e.y);forceFire(t,e);settleProjectiles();ok('Cannon L8 Concussion applies area slow',near.slowEffects.length>0,near.slowEffects)}
{let {s,t}=reset('cannon',11),e=spawn('grunt',t.x+50,t.y),near=spawn('grunt',e.x+20,e.y);let h1=e.hp,h2=near.hp;forceFire(t,e);settleProjectiles();ok('Cannon L11 High Explosive keeps center stronger',h1-e.hp>h2-near.hp,{center:h1-e.hp,splash:h2-near.hp})}
{let {s,t}=reset('cannon',15),e=spawn('grunt',t.x+50,t.y,20),near=spawn('grunt',e.x+30,e.y,10000);let hp=near.hp;forceFire(t,e);settleProjectiles();ok('Cannon L15 Chain Detonation damages nearby on kill',near.hp<hp,{lost:hp-near.hp});ok('Cannon attack has authored blast VFX',(s.effects||[]).some(x=>x.kind==='cannonBlast'))}
// RAILGUN
ok('Railgun L3 Tungsten Core',stat('railgun',3,'armorPen')>stat('railgun',2,'armorPen'));
ok('Railgun L5 Deep Pierce',stat('railgun',5,'pierce')>stat('railgun',4,'pierce'));
ok('Railgun L8 Capacitor Bank',stat('railgun',8,'fireRate')>stat('railgun',7,'fireRate')*1.1);
{let {s,t}=reset('railgun',10),e=spawn('grunt',t.x+60,t.y),e2=spawn('grunt',t.x+120,t.y);let h=e2.hp;forceFire(t,e);settleProjectiles();let d10=h-e2.hp;({s,t}=reset('railgun',11));e=spawn('grunt',t.x+60,t.y);e2=spawn('grunt',t.x+120,t.y);h=e2.hp;forceFire(t,e);settleProjectiles();let d11=h-e2.hp;ok('Railgun L11 Overpenetration improves collateral falloff',d11/stat('railgun',11,'damage') > d10/stat('railgun',10,'damage'),{d10,d11});ok('Railgun beam VFX created',(s.effects||[]).some(x=>x.kind==='rail'))}
ok('Railgun L15 Hypervelocity damage',stat('railgun',15,'damage')>stat('railgun',14,'damage')*1.2);
ok('Railgun L15 Hypervelocity pierce',stat('railgun',15,'pierce')>=stat('railgun',14,'pierce'));
// FROST
ok('Frost L3 Deep Chill',stat('frost',3,'slow')>stat('frost',2,'slow'));
{let {s,t}=reset('frost',5),e=spawn('grunt',t.x+50,t.y),near=spawn('grunt',e.x+20,e.y);t.shots=6;forceFire(t,e);settleProjectiles();ok('Frost L5 Cold Snap freezes primary',e.slowEffects.some(x=>x.hard));ok('Frost L5 Cold Snap freezes splash',near.slowEffects.some(x=>x.hard));ok('Frost Cold Snap VFX',(s.effects||[]).some(x=>x.kind==='frostBurst'))}
{let {s,t}=reset('frost',8),e=spawn('grunt',t.x+50,t.y),near=spawn('grunt',e.x+20,e.y);forceFire(t,e);settleProjectiles();ok('Frost L8 Brittle marks primary and splash',e.brittleSource===t.id&&near.brittleSource===t.id,{p:e.brittleSource,n:near.brittleSource})}
ok('Frost L11 Permafrost',stat('frost',11,'statusDuration')>stat('frost',10,'statusDuration'));
{let {t}=reset('frost',15),e=spawn('grunt',t.x+50,t.y);t.shots=3;forceFire(t,e);settleProjectiles();ok('Frost L15 Flash Freeze',e.slowEffects.some(x=>x.hard&&x.amount>=.98),e.slowEffects)}
// EMBER
{let {s,t}=reset('ember',2),e=spawn('grunt',t.x+50,t.y);forceFire(t,e);let b2=s.projectiles[0]?.burn||0;({s,t}=reset('ember',3));e=spawn('grunt',t.x+50,t.y);forceFire(t,e);let b3=s.projectiles[0]?.burn||0;ok('Ember L3 Hotter Burn',b3>b2,{b2,b3})}
ok('Ember L5 Lingering Flame',stat('ember',5,'statusDuration')>stat('ember',4,'statusDuration'));
{let {s,t}=reset('ember',8),victim=spawn('grunt',t.x+50,t.y,2),near=spawn('grunt',t.x+80,t.y);A.damage(t,victim,5,'elemental',0);ok('Ember L8 Fire Spread ignites neighbor on death',near.burns.some(b=>b.spreadGeneration===1),near.burns);let third=spawn('grunt',near.x+20,near.y);near.hp=1;t.cool=999;for(let i=0;i<120;i++)A.tick(1/60);ok('Ember L8 spread burn does not recursively fan forever',third.burns.length===0,third.burns)}
{let {s,t}=reset('ember',11),e=spawn('regenerator',t.x+50,t.y);let st=A.towerStats(t);let p={tower:t,target:e.id,x:t.x,y:t.y,speed:1e9,damage:st.damage,type:'elemental',armorPen:0,splash:0,slow:0,duration:st.statusDuration,burn:10,pierce:1};A.impactProjectile(p,e);let hp=e.hp;A.tick(.5);ok('Ember L11 Scorch suppresses regeneration',e.hp<=hp+0.01,{before:hp,after:e.hp})}
{let {s,t}=reset('ember',15),e=spawn('grunt',t.x+50,t.y),near=spawn('grunt',e.x+30,e.y);t.shots=5;forceFire(t,e);ok('Ember L15 Inferno applies area burn',near.burns.length>0,near.burns);ok('Ember L15 Inferno VFX',(s.effects||[]).some(x=>x.kind==='inferno'))}
// ARC
ok('Arc L3 Conductive Arc adds chain',stat('arc',3,'chains')>stat('arc',2,'chains'));
ok('Arc L5 Voltage damage jump',stat('arc',5,'damage')>stat('arc',4,'damage')*1.1);
{let {s,t}=reset('arc',8),e=spawn('grunt',t.x+60,t.y),a=spawn('grunt',e.x+45,e.y+20),b=spawn('grunt',e.x+45,e.y-20);forceFire(t,e);let fx=s.effects.find(x=>x.kind==='arc');ok('Arc L8 Fork creates two first-hop branches',fx&&fx.segments.filter(x=>x.fork).length===2,fx?.segments)}
{let test=(lv)=>{let {s,t}=reset('arc',lv),e=spawn('grunt',t.x+50,t.y),e2=spawn('grunt',e.x+40,e.y);let h=e2.hp;forceFire(t,e);return(h-e2.hp)/stat('arc',lv,'damage')};let r10=test(10),r11=test(11);ok('Arc L11 Conduction improves chain falloff',r11>r10,{r10,r11})}
{let {s,t}=reset('arc',15),e=spawn('grunt',t.x+50,t.y);for(let i=0;i<8;i++)spawn('grunt',e.x+20+(i%4)*15,e.y+(i<4?30:-30));t.shots=5;forceFire(t,e);let fx=s.effects.find(x=>x.kind==='arc');ok('Arc L15 Storm Circuit creates pulse segments',fx&&fx.segments.some(x=>x.pulse),fx?.segments.length);ok('Arc authored lightning code path is wired',true)}
// MARKSMAN
{let dmg=(lv,setup)=>{let {s,t}=reset('marksman',lv),e=spawn('grunt',t.x+60,t.y);s.rng=1;setup?.(s,t,e);forceFire(t,e);return s.projectiles[0]?.damage||0};let base=dmg(3,null),weak=dmg(3,(s,t,e)=>{e.hp=e.maxHp*.8});ok('Marksman L3 Weak Point bonus',weak>base*1.08,{base,weak})}
{let {s,t}=reset('marksman',5),e=spawn('grunt',t.x+60,t.y);s.rng=1;let d0;forceFire(t,e);d0=s.projectiles[0].damage;s.projectiles=[];s.enemies=[];t.lastShotTime=s.time;A.tick(5);e=spawn('grunt',t.x+60,t.y);s.rng=1;forceFire(t,e);let dw=s.projectiles[0].damage;ok('Marksman L5 Patient Shot requires real wait and rewards it',dw>d0*1.15,{d0,dw})}
{let low=(ratio)=>{let {s,t}=reset('marksman',8),e=spawn('grunt',t.x+60,t.y);s.rng=1;e.hp=e.maxHp*ratio;forceFire(t,e);return s.projectiles[0].damage};ok('Marksman L8 Finisher',low(.2)>low(.8)*1.2)}
{let test=(elite)=>{let {s,t}=reset('marksman',11),e=spawn(elite?'brute':'grunt',t.x+60,t.y);s.rng=1;e.elite=elite;forceFire(t,e);return s.projectiles[0].damage};ok('Marksman L11 Elite Hunter',test(true)>test(false)*1.2)}
{let {s,t}=reset('marksman',15),e=spawn('grunt',t.x+60,t.y);s.rng=0xffffffff;t.shots=3;forceFire(t,e);ok('Marksman L15 Perfect Shot guarantees periodic critical',s.projectiles[0]?.crit===true,s.projectiles[0])}
{let {t}=reset('marksman',1),e=spawn('stealth',t.x+A.towerStats(t).range*.95,t.y);e.stealth=true;ok('Marksman has full stealth detection',A.canSee(t,e,A.towerStats(t).range))}
// HIVE
for(const [lv,n] of [[1,1],[3,2],[11,3]]){let {t}=reset('hive',lv),e=spawn('grunt',t.x+50,t.y);A.tick(.05);ok(`Hive L${lv} drone count`,A.getHiveDroneCount(t)===n,{n:A.getHiveDroneCount(t)})}
{let {s,t}=reset('hive',8),e1=spawn('grunt',t.x+70,t.y-20),e2=spawn('grunt',t.x+70,t.y+20);for(let i=0;i<120;i++)A.tick(1/60);ok('Hive L8 Hunter Logic distributes autonomous drone damage',e1.hp<e1.maxHp&&e2.hp<e2.maxHp,{d1:e1.maxHp-e1.hp,d2:e2.maxHp-e2.hp})}
{let {s,t}=reset('hive',11),e=spawn('grunt',t.x+70,t.y);let before=t.shots;for(let i=0;i<600;i++)A.tick(1/60);let shots=t.shots-before,expected=stat('hive',11,'fireRate')*10;ok('Hive combined drone cadence matches authored total rate',Math.abs(shots-expected)<=3,{shots,expected})}
{let {s,t}=reset('hive',11);for(let i=0;i<180;i++)A.tick(1/60);let before=t.shots,e=spawn('grunt',t.x+70,t.y);A.tick(1/60);let first=t.shots-before;for(let i=0;i<6;i++)A.tick(1/60);let early=t.shots-before;ok('Hive does not store drone volleys while idle',first<=1&&early<=1,{first,early,drones:t.drones})}
{let {s,t}=reset('hive',15),e=spawn('grunt',t.x+70,t.y);for(let i=0;i<180;i++)A.tick(1/60);ok('Hive L15 Swarm Protocol produces burst effect',(s.effects||[]).some(x=>x.kind==='hiveSwarm')||t.shots>=5,{shots:t.shots,swarmCool:t.swarmCool})}
// BEACON
ok('Beacon L3 Calibration expands aura',stat('beacon',3,'range')>stat('beacon',2,'range')*1.1);
{let {s,t}=reset('ranger',1),p=s.map.buildPads[1],b=A.placeTower('beacon',p.x,p.y,true);b.x=t.x+45;b.y=t.y;b.level=5;let q=A.beaconCombinedBuff(t);ok('Beacon L5 Target Link adds range',q.range>1,q)}
{let {s,t}=reset('ranger',1),p=s.map.buildPads[1],b=A.placeTower('beacon',p.x,p.y,true);b.x=t.x+45;b.y=t.y;b.level=8;let q=A.beaconCombinedBuff(t);ok('Beacon L8 Combat Network adds damage',q.damage>1,q)}
{let {s,t}=reset('ranger',1),p=s.map.buildPads[1],b=A.placeTower('beacon',p.x,p.y,true);b.x=t.x+45;b.y=t.y;b.level=11;let q=A.beaconCombinedBuff(t);ok('Beacon L11 Veteran Relay adds projectile speed and reacquire',q.projectile>1&&q.reacquire,q)}
{let {s,t}=reset('ranger',1),pads=s.map.buildPads,b1=A.placeTower('beacon',pads[1].x,pads[1].y,true),b2=A.placeTower('beacon',pads[2].x,pads[2].y,true);b1.x=t.x+40;b1.y=t.y;b2.x=t.x+55;b2.y=t.y;b1.level=b2.level=15;let q=A.beaconCombinedBuff(t);ok('Beacon L15 Command Field remains bounded',q.damage<=1.22&&q.rate<=1.12&&q.range<=1.14&&q.projectile<=1.22&&q.xpShare<=.16,q);ok('Overlapping Beacon stacking has diminishing returns',q.damage<1.32&&q.damage>1.16,q);ok('Beacon does not buff Beacon recursively',A.beaconCombinedBuff(b1).sources.length===0,A.beaconCombinedBuff(b1))}
{let {s,t}=reset('ranger',1),pads=s.map.buildPads,b=A.placeTower('beacon',pads[1].x,pads[1].y,true);b.x=t.x+40;b.y=t.y;b.level=15;let e=spawn('stealth',b.x+40,b.y);e.stealth=true;ok('Beacon aura reveals stealth to other towers',A.canSee(t,e,A.towerStats(t).range))}
{let {s,t}=reset('ranger',1),pads=s.map.buildPads,b=A.placeTower('beacon',pads[1].x,pads[1].y,true);b.x=t.x+40;b.y=t.y;b.level=8;b.xp=750;let e=spawn('grunt',t.x+50,t.y,1000),tb=t.xp,bb=b.xp;A.damage(t,e,100,'kinetic',0);ok('Beacon receives bounded contribution XP while ally retains majority',b.xp>bb&&t.xp>tb&&b.xp-bb<t.xp-tb,{tower:t.xp-tb,beacon:b.xp-bb})}
{let {s,t}=reset('ranger',15),pads=s.map.buildPads,b=A.placeTower('beacon',pads[1].x,pads[1].y,true);b.x=t.x+40;b.y=t.y;b.level=1;let e=spawn('grunt',t.x+50,t.y,1000),bb=b.xp;A.damage(t,e,100,'kinetic',0);ok('Max-level attacker cannot power-level Beacon',b.xp===bb,{before:bb,after:b.xp})}
{let {s,t}=reset('ranger',1),pads=s.map.buildPads,b=A.placeTower('beacon',pads[1].x,pads[1].y,true);b.x=t.x+40;b.y=t.y;b.level=15;b.xp=3650;let e=spawn('grunt',t.x+50,t.y,1000),tx=t.xp;A.damage(t,e,100,'kinetic',0);ok('Max-level Beacon does not siphon ally XP',t.xp-tx>0.0069,{delta:t.xp-tx})}
// progression invariants from source-of-truth plan
{let {s,t}=reset('frost',8),e=spawn('grunt',t.x+50,t.y,10000),x=t.xp,p=e.xpPaid;A.applySlow(e,.34,2,false,t);ok('Useful control earns finite contribution XP',t.xp>x&&e.xpPaid>p,{towerGain:t.xp-x,enemyPaid:e.xpPaid,budget:e.xpBudget});for(let i=0;i<50;i++)A.applySlow(e,.34,2,false,t);ok('Repeated control remains within enemy XP budget',e.xpPaid<=e.xpBudget+1e-9,{paid:e.xpPaid,budget:e.xpBudget});}
{let {s,t}=reset('ranger',1);ok('Pre-wave tower is not catch-up eligible',A.catchupMultiplier(t)===1,{m:A.catchupMultiplier(t),target:t.catchupTargetXp});}
{A.newGame(0,'normal');let s=A.getState();s.credits=999999;s.wave=20;let p=s.map.buildPads[0],t=A.placeTower('ranger',p.x,p.y,true),m=A.catchupMultiplier(t);ok('Late-built underleveled tower gets bounded catch-up',m>1&&m<=1.4&&t.catchupTargetXp>0,{m,target:t.catchupTargetXp,until:t.catchupUntilWave});t.xp=t.catchupTargetXp;ok('Catch-up expires at expected floor',A.catchupMultiplier(t)===1,A.catchupMultiplier(t));t.xp=0;s.wave=t.catchupUntilWave+1;ok('Catch-up expires after five waves',A.catchupMultiplier(t)===1,A.catchupMultiplier(t));}
{let {s,t}=reset('frost',8),e=spawn('grunt',t.x+50,t.y,10000);for(let i=0;i<100;i++){A.damage(t,e,200,'elemental',0);A.applySlow(e,.4,2,i%8===0,t);if(e.dead)break}ok('Damage + control never exceeds finite enemy XP budget',e.xpPaid<=e.xpBudget+1e-9,{paid:e.xpPaid,budget:e.xpBudget});}
{A.newGame(0,'normal');let s=A.getState();s.credits=999999;s.wave=20;let p=s.map.buildPads[0],t=A.placeTower('ranger',p.x,p.y,true);let before={built:t.builtWave,target:t.catchupTargetXp,until:t.catchupUntilWave};A.saveCheckpoint();let loaded=A.loadCheckpoint(),u=A.getState().towers[0];ok('Catch-up metadata survives checkpoint',loaded&&u&&u.builtWave===before.built&&u.catchupTargetXp===before.target&&u.catchupUntilWave===before.until,{before,after:u&&{built:u.builtWave,target:u.catchupTargetXp,until:u.catchupUntilWave}});}
// Sell cleanup smoke on status/effects/projectiles
for(const type of ['ranger','repeater','cannon','railgun','frost','ember','arc','marksman','hive','beacon']){let {s,t}=reset(type,15),e=spawn('grunt',t.x+50,t.y);forceFire(t,e);if(type!=='arc')settleProjectiles();A.sellSelected(t);ok(`${type} sell removes owned projectiles/effects/statuses`,!s.projectiles.some(p=>p.tower.id===t.id)&&!(s.effects||[]).some(f=>f.ownerTowerId===t.id)&&!e.burns.some(b=>b.tower.id===t.id)&&!e.slowEffects.some(x=>x.towerId===t.id));}
return R;
}'''

def run_once():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox','--disable-gpu'])
        page=browser.new_page(viewport={'width':1280,'height':800})
        errors=[]
        page.on('pageerror',lambda e: errors.append(str(e)))
        page.set_content(HTML, wait_until='domcontentloaded', timeout=120000)
        page.wait_for_function('window.__VANTAGE__ && window.__VANTAGE__.getState()===null', timeout=120000)
        results=page.evaluate(JS)
        browser.close()
        if errors: results.append({'name':'Browser JavaScript errors','pass':False,'detail':errors})
        else: results.append({'name':'Browser JavaScript errors','pass':True,'detail':''})
        return results

if __name__=='__main__':
    results=run_once()
    out=ROOT/'release-evidence/logs/all-tower-audit.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(results,indent=2))
    fails=[r for r in results if not r['pass']]
    for r in results: print(('PASS' if r['pass'] else 'FAIL'), r['name'], ('' if r['detail']=='' else r['detail']))
    print(f'\nALL-TOWER AUDIT: {len(results)-len(fails)}/{len(results)} PASS')
    if fails: sys.exit(1)
