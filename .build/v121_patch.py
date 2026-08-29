from pathlib import Path
p=Path('app/src/main/assets/www/game.js')
s=p.read_text(); end='})();'
if end not in s: raise SystemExit('missing game closure')
block=r'''
// v1.2.1: Bosses inflict threatening but bounded damage.
function bossDamageHit(frac,heavy=false,world=false){
  let min=heavy?(world?.17:.14):(world?.12:.09);
  let max=heavy?(world?.30:.26):(world?.23:.20);
  return adaptiveHit(frac+(world?.025:0),min,max);
}
bossAbility=function(e,dt){
  e.abilityCool-=dt;if(e.abilityCool>0)return;
  e.abilityCool=e.kind==='worldboss'?1.35:2.35;
  let d=D(e,run.p),wb=e.kind==='worldboss';
  if(e.ability==='charge'&&d<500){let a=Math.atan2(run.p.y-e.y,run.p.x-e.x);e.x+=Math.cos(a)*150;e.y+=Math.sin(a)*150;if(D(e,run.p)<e.r+run.p.r+35)run.p.hp-=bossDamageHit(.17,false,wb)}
  if(e.ability==='slam'&&d<155){run.p.hp-=bossDamageHit(.22,true,wb);burstFx('hit',run.p.x,run.p.y,1.35);playSfx('boss',1.25)}
  if(e.ability==='fire'&&d<390){run.p.hp-=bossDamageHit(.18,false,wb);burstFx('fire',run.p.x,run.p.y,1.1);playSfx('fire',1.0)}
  if(e.ability==='poison')run.pools.push({x:run.p.x,y:run.p.y,r:68,life:3.4,dps:run.p.maxHp*(wb?.048:.036),hostile:true});
  if(e.ability==='frost'&&d<330){run.p.hp-=bossDamageHit(.17,false,wb);burstFx('frost',run.p.x,run.p.y,1.05);playSfx('frost',1.0)}
  if(e.ability==='summon')spawnPack(e.area,{x:e.x,y:e.y},3);
  if(e.ability==='dash'){let a=Math.atan2(run.p.y-e.y,run.p.x-e.x);e.x+=Math.cos(a)*190;e.y+=Math.sin(a)*190;if(D(e,run.p)<e.r+run.p.r+30)run.p.hp-=bossDamageHit(.18,false,wb)}
  if(e.ability==='nova'&&d<220){run.p.hp-=bossDamageHit(.23,true,wb);burstFx('hit',run.p.x,run.p.y,1.5);playSfx('boss',1.35)}
  if(e.ability==='lightning'&&d<450){run.p.hp-=bossDamageHit(.21,true,wb);burstFx('frost',run.p.x,run.p.y,1.25);playSfx('boss',1.2)}
  if(e.ability==='waves'&&d<290){run.p.hp-=bossDamageHit(.20,true,wb);burstFx('hit',run.p.x,run.p.y,1.25);playSfx('boss',1.15)}
  if(e.ability==='meteor'&&d<410){run.p.hp-=bossDamageHit(.25,true,wb);burstFx('fire',run.p.x,run.p.y,1.6);playSfx('boss',1.45)}
  if(e.ability==='void'&&d<260){run.p.hp-=bossDamageHit(.27,true,wb);burstFx('poison',run.p.x,run.p.y,1.6);playSfx('boss',1.45)}
};
// Add meaningful sustained danger when standing directly on a boss, without allowing a one-frame kill.
let gbBossContactClock=0;
const updateV121=update;
update=function(dt){
  updateV121(dt);
  gbBossContactClock-=dt;
  if(gbBossContactClock<=0&&run?.enemies){
    for(const e of run.enemies){
      if(e.dead||(e.kind!=='boss'&&e.kind!=='worldboss'))continue;
      if(Math.hypot(e.x-run.p.x,e.y-run.p.y)<e.r+run.p.r+6){
        let wb=e.kind==='worldboss';
        run.p.hp-=run.p.maxHp*(wb?.024:.017);
        burstFx('hit',run.p.x,run.p.y,wb?1.2:.95);
        playSfx('hit',wb?1.25:1.0);
        gbBossContactClock=.45;
        break;
      }
    }
  }
};
'''
head,tail=s.rsplit(end,1);p.write_text(head+'\n'+block+'\n'+end+tail)
