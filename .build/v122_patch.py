from pathlib import Path
p=Path('app/src/main/assets/www/game.js')
s=p.read_text(); end='})();'
if end not in s: raise SystemExit('missing game closure')
block=r'''
// v1.2.2: make elemental/skill auras mechanically match their visible radius and advertised DPS.
// Aura damage is expressed per SECOND; update(dt) multiplies by dt so frame/tick rate cannot multiply the advertised percentage.
function gbAuraBossCap(e,pctPerSec){
  if(e.kind==='worldboss') return Math.min(pctPerSec,.018);
  if(e.kind==='boss') return Math.min(pctPerSec,.025);
  return pctPerSec;
}
function gbAuraConfig(){
  let out=[];
  const fireR=rank('fire'), frostR=rank('frost'), poisonR=rank('poison'), bladeR=rank('blades');
  // Rank 10 is the permanent-aura mastery point already used by the game.
  if(fireR>=10&&activeEnabled('fire')){
    let tier=Math.floor(fireR/5), radius=105+tier*8;
    out.push({kind:'fire',radius,pct:.010+tier*.0015,status:1.25});
  }
  if(frostR>=10&&activeEnabled('frost')){
    let tier=Math.floor(frostR/5), radius=110+tier*8;
    out.push({kind:'frost',radius,pct:.007+tier*.00115,status:.40+tier*.025});
  }
  if(poisonR>=10&&activeEnabled('poison')){
    let tier=Math.floor(poisonR/5), radius=120+tier*9;
    out.push({kind:'poison',radius,pct:.018+tier*.0022,status:2.2+tier*.12});
  }
  if(bladeR>=10&&activeEnabled('blades')){
    let tier=Math.floor(bladeR/5), radius=92+tier*7;
    out.push({kind:'blade',radius,pct:.008+tier*.00125,status:0});
  }
  // Mythic radius powers receive real continuous effects too.
  let lv=equippedMythicLevels?equippedMythicLevels():{};
  if(lv[10]&&poisonR>0&&activeEnabled('poison')) out.push({kind:'poison',radius:190+lv[10]*25,pct:.025+.005*lv[10],status:4+lv[10]});
  if(lv[8]&&frostR>0&&activeEnabled('frost')) out.push({kind:'frost',radius:105+lv[8]*14,pct:.010+.0025*lv[8],status:.65+.08*lv[8]});
  if(lv[0]&&fireR>0&&activeEnabled('fire')) out.push({kind:'fire',radius:150+lv[0]*24,pct:.012+.003*lv[0],status:1.5+.2*lv[0]});
  return out;
}
function gbApplyAuras(dt){
  if(!run?.p||!run.enemies)return;
  let auras=gbAuraConfig();
  if(!auras.length)return;
  for(const e of run.enemies){
    if(e.dead||e.area!==run.area)continue;
    let d=Math.hypot(e.x-run.p.x,e.y-run.p.y);
    for(const a of auras){
      if(d>a.radius+(e.r||0))continue;
      let pct=gbAuraBossCap(e,a.pct), dmg=Math.max(0,(e.maxHp||e.hp||1)*pct*dt);
      e.hp-=dmg;
      if(a.kind==='fire'){
        e.burn=Math.max(e.burn||0,a.status);
        e.burnDps=Math.max(e.burnDps||0,(e.maxHp||1)*gbAuraBossCap(e,a.pct*.35));
      }else if(a.kind==='poison'){
        e.poison=Math.max(e.poison||0,a.status);
        // poisonDps is kept consistent with the aura's PER-SECOND model, not per tick.
        e.poisonDps=Math.max(e.poisonDps||0,(e.maxHp||1)*gbAuraBossCap(e,a.pct*.45));
      }else if(a.kind==='frost'){
        e.frost=Math.max(e.frost||0,1.0);
        e.freeze=Math.max(e.freeze||0,Math.min((e.kind==='boss'||e.kind==='worldboss')?.35:a.status,a.status*dt*2.5));
      }
    }
  }
}
function gbDrawAuras(){
  if(!run?.p)return;
  let auras=gbAuraConfig(); if(!auras.length)return;
  let x=sx(run.p.x),y=sy(run.p.y);ctx.save();ctx.globalCompositeOperation='lighter';
  for(const a of auras){
    let r=a.radius,g=ctx.createRadialGradient(x,y,r*.35,x,y,r);
    if(a.kind==='fire'){g.addColorStop(0,'#ffb52b10');g.addColorStop(.72,'#ff6a2030');g.addColorStop(1,'#ff321080');ctx.strokeStyle='#ff7a2a';}
    else if(a.kind==='poison'){g.addColorStop(0,'#54ff3910');g.addColorStop(.72,'#48e52b30');g.addColorStop(1,'#8cff5a75');ctx.strokeStyle='#79ff58';}
    else if(a.kind==='frost'){g.addColorStop(0,'#aef6ff10');g.addColorStop(.72,'#74ddff2f');g.addColorStop(1,'#d6fbff75');ctx.strokeStyle='#b8f6ff';}
    else {g.addColorStop(0,'#ffffff08');g.addColorStop(.72,'#e8e8ff24');g.addColorStop(1,'#ffffff68');ctx.strokeStyle='#f7f7ff';}
    ctx.globalAlpha=.34;ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();
    ctx.globalAlpha=.75;ctx.lineWidth=2;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.stroke();
  }
  ctx.restore();
}
const updateV122=update;update=function(dt){updateV122(dt);gbApplyAuras(dt)};
const drawV122=draw;draw=function(){drawV122();gbDrawAuras()};
'''
head,tail=s.rsplit(end,1);p.write_text(head+'\n'+block+'\n'+end+tail)
