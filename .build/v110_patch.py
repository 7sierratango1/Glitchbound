from pathlib import Path
p=Path('app/src/main/assets/www/game.js')
s=p.read_text()

marker="function open(n){"
if marker not in s: raise SystemExit('missing open marker')
block=r'''
const MYTHIC_POWERS=[
['Inferno Nova','Fire attacks periodically erupt in a 360° blast.'],
['Living Flame','Burning enemies spread fire to nearby enemies.'],
['Meteoric Wrath','Periodically calls a meteor onto an enemy.'],
['Flamewake','Movement scorches enemies near your path.'],
['Phoenix Detonation','Low-health burning enemies violently detonate.'],
['Absolute Zero','Periodically freezes nearly the entire local battlefield.'],
['Shatterstorm','Frozen enemies periodically burst into damaging ice shards.'],
['Glacial Prison','Creates a freezing field around clustered enemies.'],
['Frozen Ground','Frost effects leave persistent damaging chill zones.'],
['Ice Lance Barrage','Launches volleys of piercing frost lances.'],
['Plague Ring','Creates a toxic ring that drains enemies over time.'],
['Virulent Outbreak','Poison repeatedly jumps to nearby enemies.'],
['Toxic Detonation','Poisoned enemies trigger toxic explosions.'],
['Corrosive Venom','Poisoned targets take increased damage from all sources.'],
['Devouring Plague','Poison damage restores a portion of your life.'],
['Flaming Blades','Blades ignite enemies and deal bonus fire damage.'],
['Frost Blades','Blade hits chill and periodically freeze targets.'],
['Venom Blades','Blade hits apply stacking poison damage.'],
['Explosive Blades','Blade attacks periodically explode in an area.'],
['Returning Blades','Extra blades sweep outward and return through enemies.'],
['Blade Replication','Blade strikes periodically create extra spectral blades.'],
['Executioner Edge','Blades deal increasing damage to wounded enemies.'],
['Elemental Bladestorm','Blades randomly carry fire, frost, or poison.'],
['Chain Reaction','Elemental conditions combine into violent reactions.'],
['Soul Harvest','Kills build soul energy that erupts and restores health.'],
['Blood Frenzy','Lower health increases attack speed and damage.'],
['Vampiric Surge','Critical combat periodically triggers heavy life recovery.'],
['Temporal Rupture','Creates time fields that heavily slow nearby enemies.'],
['Arcane Echo','Active abilities periodically echo without consuming cooldowns.'],
['Cataclysm','Periodically unleashes a massive effect based on your strongest skill.']
];
function mythicPowerData(it){return it&&it.mythicPower!=null?MYTHIC_POWERS[it.mythicPower]:null}
function equippedMythicLevels(){let out={};for(const k in save.loot.equipped){let it=save.loot.equipped[k];if(it&&it.rarity===5&&it.mythicPower!=null)out[it.mythicPower]=(out[it.mythicPower]||0)+1}return out}
function mythicDesc(it){let d=mythicPowerData(it);return d?`<div style="margin-top:7px;color:#ff7be5;font-weight:900">MYTHIC POWER: ${d[0]}</div><div style="font-size:10px;color:#ffc9f4">${d[1]}</div>`:''}
function enhanceMythicItem(it){if(!it||it.rarity!==5)return it;it.mythicPower=Math.floor(Math.random()*MYTHIC_POWERS.length);let keys=['damage','hp','armor','rate','crit','speed','lifesteal'],count=3+Math.floor(Math.random()*3);for(let i=keys.length-1;i>0;i--){let j=Math.floor(Math.random()*(i+1)),t=keys[i];keys[i]=keys[j];keys[j]=t}for(const k of keys.slice(0,count)){if(k==='armor')it.stats[k]=(it.stats[k]||0)+6+it.power*.032;else if(k==='lifesteal')it.stats[k]=(it.stats[k]||0)+.008+Math.min(.035,it.power*.000018);else if(k==='crit')it.stats[k]=(it.stats[k]||0)+.018+Math.min(.07,it.power*.00004);else it.stats[k]=(it.stats[k]||0)+.035+Math.min(.18,it.power*.00012)}return it}
const rollItemV110=rollItem;
rollItem=function(e){return enhanceMythicItem(rollItemV110(e))}
function mythicDamage(mult=1){return Math.max(1,run.p.damage*mult)}
function mythicEnemies(radius=99999){return run.enemies.filter(e=>e.area===run.area&&D(e,run.p)<=radius)}
function mythicBurst(radius,mult,element){for(const e of mythicEnemies(radius)){e.hp-=mythicDamage(mult);if(element==='fire'){e.burn=Math.max(e.burn,3);e.burnDps=Math.max(e.burnDps,run.p.burnDps*1.3)}if(element==='frost'){e.frost=Math.max(e.frost,2);e.freeze=Math.max(e.freeze,.5)}if(element==='poison'){e.poison=Math.max(e.poison||0,5);e.poisonDps=Math.max(e.poisonDps||0,run.p.poisonDps*1.5)}}}
function mythicRadial(element,count,mult,speed=480,pierce=3){radialBurst(element,count,mult,speed,pierce)}
function strongestActive(){let a=[['fire',rank('fire')],['frost',rank('frost')],['poison',rank('poison')],['blades',rank('blades')]];a.sort((x,y)=>y[1]-x[1]);return a[0][0]}
function mythicTick(dt){if(!run||!run.p)return;let lv=equippedMythicLevels();run.mythicTimers=run.mythicTimers||{};for(const id in lv)run.mythicTimers[id]=(run.mythicTimers[id]||0)-dt;let fire=rank('fire')>0&&activeEnabled('fire'),frost=rank('frost')>0&&activeEnabled('frost'),poison=rank('poison')>0&&activeEnabled('poison'),blades=rank('blades')>0&&activeEnabled('blades');let trig=(id,base,fn)=>{if(lv[id]&&run.mythicTimers[id]<=0){fn(lv[id]);run.mythicTimers[id]=Math.max(.55,base/(1+.28*(lv[id]-1)))}};
trig(0,4.5,L=>{if(fire){mythicBurst(150+L*24,2+L*.45,'fire');mythicRadial('fire',10+L*3,1.15+L*.2)}});
trig(1,2.8,L=>{if(fire)for(const e of mythicEnemies(600))if(e.burn>0){for(const q of run.enemies)if(q.area===e.area&&D(q,e)<95+L*12){q.burn=Math.max(q.burn,3+L);q.burnDps=Math.max(q.burnDps,run.p.burnDps*(1+.25*L))}}});
trig(2,5.5,L=>{if(fire){let a=mythicEnemies();if(a.length){let e=a[Math.floor(Math.random()*a.length)];for(const q of run.enemies)if(q.area===e.area&&D(q,e)<125+L*18){q.hp-=mythicDamage(3+L*.8);q.burn=5;q.burnDps=Math.max(q.burnDps,run.p.burnDps*2)}}}});
trig(3,1.1,L=>{if(fire)mythicBurst(70+L*8,.35+L*.08,'fire')});
trig(4,3.6,L=>{if(fire)for(const e of mythicEnemies(700))if(e.burn>0&&e.hp/e.maxHp<.35){let cap=(e.kind==='boss'||e.kind==='worldboss')?e.maxHp*.035:e.maxHp*.35;e.hp-=Math.min(cap,mythicDamage(2.2+L*.55));for(const q of run.enemies)if(q!==e&&D(q,e)<100+L*12)q.hp-=mythicDamage(1.1+L*.25)}});
trig(5,9,L=>{if(frost)for(const e of mythicEnemies()){e.freeze=Math.max(e.freeze,(e.kind==='boss'||e.kind==='worldboss')?Math.min(2,0.65+L*.2):Math.min(10,6+L));e.frost=Math.max(e.frost,5)}});
trig(6,3.2,L=>{if(frost)for(const e of mythicEnemies(650))if(e.freeze>0){for(const q of run.enemies)if(q.area===e.area&&D(q,e)<85+L*10)q.hp-=mythicDamage(.8+L*.18)}});
trig(7,6,L=>{if(frost){let a=mythicEnemies();if(a.length){let e=a[Math.floor(Math.random()*a.length)];for(const q of run.enemies)if(q.area===e.area&&D(q,e)<145+L*20){q.freeze=Math.max(q.freeze,1.5+L*.35);q.hp-=mythicDamage(1+L*.25)}}}});
trig(8,1.5,L=>{if(frost)mythicBurst(105+L*14,.4+L*.09,'frost')});
trig(9,4.2,L=>{if(frost)mythicRadial('frost',8+L*4,1.25+L*.22,560,4+L)});
trig(10,6,L=>{if(poison)for(const e of mythicEnemies(190+L*25)){let pct=(e.kind==='boss'||e.kind==='worldboss')?.008:.025;e.hp-=Math.min(e.maxHp*pct*L,mythicDamage(1.5+L*.4));e.poison=10;e.poisonDps=Math.max(e.poisonDps||0,run.p.poisonDps*(1+L*.3))}});
trig(11,2.6,L=>{if(poison)for(const e of mythicEnemies(650))if((e.poison||0)>0){for(const q of run.enemies)if(q!==e&&q.area===e.area&&D(q,e)<120+L*15){q.poison=Math.max(q.poison||0,5);q.poisonDps=Math.max(q.poisonDps||0,run.p.poisonDps*(1+L*.2))}}});
trig(12,4,L=>{if(poison)for(const e of mythicEnemies(650))if((e.poison||0)>0&&e.hp/e.maxHp<.4){for(const q of run.enemies)if(q.area===e.area&&D(q,e)<105+L*15)q.hp-=mythicDamage(1.2+L*.3)}});
trig(13,1.1,L=>{if(poison)for(const e of mythicEnemies(700))if((e.poison||0)>0)e.hp-=mythicDamage(.16*L)*dt*5});
trig(14,1.2,L=>{if(poison){let n=mythicEnemies(700).filter(e=>(e.poison||0)>0).length;if(n)run.p.hp=Math.min(run.p.maxHp,run.p.hp+run.p.maxHp*Math.min(.025,.0025*n*L))}});
trig(15,1.3,L=>{if(blades){mythicBurst(135+L*12,.55+L*.12,'fire');mythicRadial('fire',6+L*2,.55+L*.12,520,2+L)}});
trig(16,1.6,L=>{if(blades)for(const e of mythicEnemies(145+L*12)){e.frost=Math.max(e.frost,2);e.freeze=Math.max(e.freeze,.2+L*.12)}});
trig(17,1.4,L=>{if(blades)for(const e of mythicEnemies(145+L*12)){e.poison=Math.max(e.poison||0,4+L);e.poisonDps=Math.max(e.poisonDps||0,run.p.poisonDps*(.8+L*.25))}});
trig(18,2.4,L=>{if(blades)mythicBurst(155+L*20,1.1+L*.3)});
trig(19,2.1,L=>{if(blades){mythicRadial('blade',8+L*3,.9+L*.18,580,4+L);setTimeout(()=>{if(run&&run.p)mythicRadial('blade',8+L*3,.75+L*.15,460,3+L)},260)}});
trig(20,1.8,L=>{if(blades)mythicRadial('blade',5+L*2,.75+L*.16,600,3+L)});
trig(21,1.05,L=>{if(blades)for(const e of mythicEnemies(160)){let missing=1-e.hp/e.maxHp;e.hp-=mythicDamage(missing*(.35+.12*L))}});
trig(22,1.7,L=>{if(blades){let els=['fire','frost','poison'];mythicRadial(els[Math.floor(Math.random()*3)],7+L*2,.75+L*.14,530,3+L)}});
trig(23,3.3,L=>{if((fire?1:0)+(frost?1:0)+(poison?1:0)>=2)for(const e of mythicEnemies(500)){let c=(e.burn>0?1:0)+(e.frost>0?1:0)+((e.poison||0)>0?1:0);if(c>=2)e.hp-=mythicDamage((.8+L*.2)*c)}});
trig(24,5.2,L=>{mythicBurst(230+L*25,1.5+L*.4);run.p.hp=Math.min(run.p.maxHp,run.p.hp+run.p.maxHp*(.025+.01*L))});
trig(25,.9,L=>{let missing=1-run.p.hp/run.p.maxHp;if(missing>.15){for(const e of mythicEnemies(220))e.hp-=mythicDamage(missing*(.35+.12*L))}});
trig(26,4.8,L=>{run.p.hp=Math.min(run.p.maxHp,run.p.hp+run.p.maxHp*(.05+.018*L))});
trig(27,5.5,L=>{for(const e of mythicEnemies(260+L*22)){e.freeze=Math.max(e.freeze,.6+L*.18);e.frost=Math.max(e.frost,1.5)}});
trig(28,4.4,L=>{let k=strongestActive();if(k==='fire'&&fire)mythicRadial('fire',8+L*2,1+L*.2);else if(k==='frost'&&frost)mythicRadial('frost',8+L*2,1+L*.2);else if(k==='poison'&&poison)mythicRadial('poison',8+L*2,1+L*.2);else if(blades)mythicRadial('blade',10+L*2,1+L*.2)});
trig(29,11,L=>{let k=strongestActive();if(k==='fire'){mythicBurst(900,3+L,'fire');mythicRadial('fire',18+L*4,1.8+L*.25,560,6)}else if(k==='frost'){for(const e of mythicEnemies()){e.freeze=Math.max(e.freeze,(e.kind==='boss'||e.kind==='worldboss')?1.5:5+L);e.hp-=mythicDamage(2+L*.4)}mythicRadial('frost',20+L*4,1.5+L*.2,540,6)}else if(k==='poison'){for(const e of mythicEnemies()){e.poison=Math.max(e.poison||0,10);e.poisonDps=Math.max(e.poisonDps||0,run.p.poisonDps*(2+L*.4));e.hp-=mythicDamage(1.7+L*.35)}}else{mythicRadial('blade',24+L*5,1.7+L*.25,650,8)}})}
const evolveSkillsV110=evolveSkills;evolveSkills=function(dt){evolveSkillsV110(dt);mythicTick(dt)}
'''
s=s.replace(marker,block+'\n'+marker,1)

# Mythic-aware comparison: a different Mythic power is treated as a sidegrade unless raw power is decisively different.
old="if(diff>.05)return{kind:'up',icon:'▲',color:'#53d769',label:'UPGRADE',current};if(diff<-.05)return{kind:'down',icon:'▼',color:'#ff5b5b',label:'DOWNGRADE',current};return{kind:'side',icon:'━',color:'#ffd34d',label:'SIDEGRADE',current}"
new="if(it.rarity===5&&current&&current.rarity===5&&it.mythicPower!==current.mythicPower&&Math.abs(diff)<.20)return{kind:'side',icon:'━',color:'#ffd34d',label:'MYTHIC SIDEGRADE',current};if(diff>.05)return{kind:'up',icon:'▲',color:'#53d769',label:'UPGRADE',current};if(diff<-.05)return{kind:'down',icon:'▼',color:'#ff5b5b',label:'DOWNGRADE',current};return{kind:'side',icon:'━',color:'#ffd34d',label:'SIDEGRADE',current}"
if old not in s: raise SystemExit('missing compare logic')
s=s.replace(old,new,1)

# Show Mythic power in pickup comparison cards.
old="<span style=\"display:block;font-size:11px;margin-top:6px\">${statText(it)}</span>${c.current?`<span style=\"display:block;margin-top:8px;color:#aaa\">Currently: ${c.current.name} • Power ${c.current.power}</span>`:'<span style=\"display:block;margin-top:8px;color:#53d769\">Empty slot</span>'}`"
new="<span style=\"display:block;font-size:11px;margin-top:6px\">${statText(it)}</span>${mythicDesc(it)}${c.current?`<span style=\"display:block;margin-top:8px;color:#aaa\">Currently: ${c.current.name} • Power ${c.current.power}</span>${mythicDesc(c.current)}`:'<span style=\"display:block;margin-top:8px;color:#53d769\">Empty slot</span>'}`"
if old not in s: raise SystemExit('missing pickup card details')
s=s.replace(old,new,1)

# Show Mythic powers on equipped and inventory cards.
old="<div style=\"font-size:10px\">${it?statText(it):''}</div>${it?'<button>UNEQUIP</button>':''}"
new="<div style=\"font-size:10px\">${it?statText(it):''}</div>${it?mythicDesc(it):''}${it?'<button>UNEQUIP</button>':''}"
if old not in s: raise SystemExit('missing equipped card details')
s=s.replace(old,new,1)
old="<div style=\"font-size:10px;margin:5px 0\">${statText(it)}</div><div style=\"display:flex;gap:6px;justify-content:center;flex-wrap:wrap\">"
new="<div style=\"font-size:10px;margin:5px 0\">${statText(it)}</div>${mythicDesc(it)}<div style=\"display:flex;gap:6px;justify-content:center;flex-wrap:wrap\">"
if old not in s: raise SystemExit('missing inventory mythic details')
s=s.replace(old,new,1)

p.write_text(s)
