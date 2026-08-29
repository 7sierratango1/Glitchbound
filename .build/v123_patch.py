from pathlib import Path
p=Path('app/src/main/assets/www/game.js')
s=p.read_text(); end='})();'
if end not in s: raise SystemExit('missing game closure')
block=r'''
// v1.2.3: Mythic powers are premium damage effects. Their damage scales with
// character level and duplicate Mythic tier, and uses enemy max HP so adaptive
// enemy health cannot make a Mythic proc appear to do nothing.
function gbMythicLevelScale(){
  let lvl=Math.max(1,save?.character?.level||1);
  return Math.min(2.6,1+Math.log2(1+lvl)/7.5);
}
function gbMythicPctHit(e,pct){
  if(!e||e.dead)return;
  let cap=e.kind==='worldboss'?.055:e.kind==='boss'?.075:.32;
  let amount=(e.maxHp||e.hp||1)*Math.min(cap,pct*gbMythicLevelScale());
  e.hp-=Math.max(1,amount);
}
function gbMythicDamagePass(dt){
  if(!run?.p||!run.enemies)return;
  let lv=equippedMythicLevels?equippedMythicLevels():{};
  let now=performance.now()/1000;
  run.gbMythicDamageTimers=run.gbMythicDamageTimers||{};
  const active=(id)=>lv[id]||0;
  const enemies=(radius)=>run.enemies.filter(e=>!e.dead&&e.area===run.area&&Math.hypot(e.x-run.p.x,e.y-run.p.y)<=radius+(e.r||0));
  const pulse=(id,seconds,radius,basePct,element)=>{
    let L=active(id);if(!L)return;
    let key='p'+id;if((run.gbMythicDamageTimers[key]||0)>now)return;
    run.gbMythicDamageTimers[key]=now/1+Math.max(.45,seconds/(1+.16*(L-1)));
    for(const e of enemies(radius+L*18)){
      gbMythicPctHit(e,basePct*(1+.28*(L-1)));
      if(element==='fire'){e.burn=Math.max(e.burn||0,3+L);e.burnDps=Math.max(e.burnDps||0,(e.maxHp||1)*(.012+.003*L));}
      if(element==='poison'){e.poison=Math.max(e.poison||0,5+L);e.poisonDps=Math.max(e.poisonDps||0,(e.maxHp||1)*(.014+.0035*L));}
      if(element==='frost'){e.frost=Math.max(e.frost||0,2+L);e.freeze=Math.max(e.freeze||0,(e.kind==='boss'||e.kind==='worldboss')?.35:1.0+L*.18);}
    }
  };
  // Fire Mythics: hard-hitting bursts / trail pressure.
  pulse(0,4.5,175,.14,'fire'); pulse(1,3.0,220,.10,'fire'); pulse(2,5.5,260,.20,'fire');
  pulse(3,1.0,105,.045,'fire'); pulse(4,3.6,210,.13,'fire');
  // Frost Mythics: substantial damage plus their control identity.
  pulse(5,9.0,900,.12,'frost'); pulse(6,3.2,230,.105,'frost'); pulse(7,6.0,260,.15,'frost');
  pulse(8,1.5,145,.055,'frost'); pulse(9,4.2,300,.13,'frost');
  // Poison Mythics: strong initial hit plus meaningful DOT.
  pulse(10,2.0,215,.065,'poison'); pulse(11,2.6,250,.09,'poison'); pulse(12,4.0,250,.14,'poison');
  pulse(13,1.1,300,.045,'poison'); pulse(14,2.0,260,.055,'poison');
  // Blade Mythics: frequent, aggressive damage. Elemental variants retain status.
  pulse(15,1.3,180,.07,'fire'); pulse(16,1.6,190,.07,'frost'); pulse(17,1.4,190,.07,'poison');
  pulse(18,2.4,220,.12); pulse(19,2.1,240,.105); pulse(20,1.8,220,.09); pulse(21,1.1,180,.065); pulse(22,1.7,230,.09);
  // Hybrid/ultimate Mythics hit harder but less often.
  pulse(23,3.3,300,.13); pulse(24,5.2,330,.16); pulse(25,1.5,240,.075); pulse(26,4.8,250,.10);
  pulse(27,5.5,330,.12,'frost'); pulse(28,4.4,340,.15); pulse(29,11.0,900,.28);
}
const updateV123=update;update=function(dt){updateV123(dt);gbMythicDamagePass(dt)};
'''
head,tail=s.rsplit(end,1);p.write_text(head+'\n'+block+'\n'+end+tail)
