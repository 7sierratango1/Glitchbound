from pathlib import Path
import re
p=Path('app/src/main/assets/www/game.js')
s=p.read_text()

# Stronger size-to-damage scaling for normal enemies.
old="damage:9*Math.sqrt(Math.max(1,m))*Math.pow(size,.65)"
new="damage:9*Math.sqrt(Math.max(1,m))*Math.pow(size,1.25)"
if old not in s: raise SystemExit('missing size damage scaling')
s=s.replace(old,new,1)

# Add comparison helpers + pickup popup ahead of ground-loot updating.
marker="function updateGroundLoot(dt){"
if marker not in s: raise SystemExit('missing ground loot updater')
helper=r'''
function compareCandidate(it){let slot=it.slot,current=null;if(slot==='ring'){let r1=save.loot.equipped.ring1,r2=save.loot.equipped.ring2;if(!r1||!r2)current=r1&&r2?(itemScore(r1)<=itemScore(r2)?r1:r2):(r1||r2);else current=itemScore(r1)<=itemScore(r2)?r1:r2}else current=save.loot.equipped[slot];if(!current)return{kind:'up',icon:'▲',color:'#53d769',label:'UPGRADE',current:null};let a=itemScore(it),b=itemScore(current),diff=(a-b)/Math.max(1,b);if(diff>.05)return{kind:'up',icon:'▲',color:'#53d769',label:'UPGRADE',current};if(diff<-.05)return{kind:'down',icon:'▼',color:'#ff5b5b',label:'DOWNGRADE',current};return{kind:'side',icon:'━',color:'#ffd34d',label:'SIDEGRADE',current}}
function showLootPopup(it){let c=compareCandidate(it);run.choosing=true;let el=$('#choiceList');el.innerHTML='';let card=document.createElement('div');card.className='choice';card.style.cssText='text-align:center;border:2px solid '+c.color+';padding:14px';card.innerHTML=`<div style="font-size:28px;color:${c.color};font-weight:900">${c.icon}</div><b style="color:${it.color};font-size:16px">${it.name}</b><span style="display:block;color:${c.color};font-weight:900;margin:6px 0">${c.label}</span><span>Power ${it.power}</span><span style="display:block;font-size:11px;margin-top:6px">${statText(it)}</span>${c.current?`<span style="display:block;margin-top:8px;color:#aaa">Currently: ${c.current.name} • Power ${c.current.power}</span>`:'<span style="display:block;margin-top:8px;color:#53d769">Empty slot</span>'}`;el.appendChild(card);let gear=document.createElement('button');gear.className='choice';gear.innerHTML='<b>OPEN GEAR</b><span>Review and equip this item.</span>';gear.onclick=()=>{run.choosing=false;$('#choiceOverlay').classList.add('hidden');open('gear');renderGear()};el.appendChild(gear);let keep=document.createElement('button');keep.className='choice';keep.innerHTML='<b>KEEP PLAYING</b><span>Leave the item in inventory for later.</span>';keep.onclick=()=>{run.choosing=false;$('#choiceOverlay').classList.add('hidden')};el.appendChild(keep);$('#choiceOverlay').classList.remove('hidden')}
'''
s=s.replace(marker,helper+marker,1)

# Replace pickup behavior so each collected item triggers a comparison prompt.
pat=r"function updateGroundLoot\(dt\)\{for\(const d of run\.lootDrops\)\{.*?run\.potions=run\.potions\.filter\(x=>!x\.dead\)\}"
rep="function updateGroundLoot(dt){for(const d of run.lootDrops){let dist=D(d,run.p);if(dist<run.p.magnet){let a=Math.atan2(run.p.y-d.y,run.p.x-d.x);d.x+=Math.cos(a)*180*dt;d.y+=Math.sin(a)*180*dt}if(dist<24&&save.loot.inventory.length<120&&!run.choosing){save.loot.inventory.push(d.item);d.dead=true;persist();showLootPopup(d.item)}}run.lootDrops=run.lootDrops.filter(x=>!x.dead);for(const q of run.potions){let dist=D(q,run.p);if(dist<run.p.magnet){let a=Math.atan2(run.p.y-q.y,run.p.x-q.x);q.x+=Math.cos(a)*190*dt;q.y+=Math.sin(a)*190*dt}if(dist<24){run.p.hp=Math.min(run.p.maxHp,run.p.hp+run.p.maxHp*q.heal);q.dead=true}}run.potions=run.potions.filter(x=>!x.dead)}"
s,n=re.subn(pat,rep,s,count=1)
if n!=1: raise SystemExit('failed loot popup updater patch')

p.write_text(s)
