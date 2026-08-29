from pathlib import Path
p=Path('app/src/main/assets/www/game.js')
s=p.read_text(); end='})();'
if end not in s: raise SystemExit('missing game closure')
block=r'''
// v1.2.0: dangerous large monsters, territorial pursuit, richer VFX, procedural music and SFX controls.
if(!save.settings)save.settings={};
if(save.settings.music===undefined)save.settings.music=true;
if(save.settings.sfx===undefined)save.settings.sfx=true;

// ---------- AUDIO ----------
let GB_AUDIO=null,GB_MASTER=null,GB_MUSIC=null,GB_SFX=null,GB_MUSIC_TIMER=0,GB_BEAT=0;
function gbAudio(){if(GB_AUDIO)return GB_AUDIO;let A=window.AudioContext||window.webkitAudioContext;if(!A)return null;GB_AUDIO=new A();GB_MASTER=GB_AUDIO.createGain();GB_MUSIC=GB_AUDIO.createGain();GB_SFX=GB_AUDIO.createGain();GB_MASTER.gain.value=.72;GB_MUSIC.gain.value=save.settings.music?.42:0;GB_SFX.gain.value=save.settings.sfx?.58:0;GB_MUSIC.connect(GB_MASTER);GB_SFX.connect(GB_MASTER);GB_MASTER.connect(GB_AUDIO.destination);return GB_AUDIO}
function gbTone(freq,dur,type='sawtooth',vol=.08,dest=null,slide=0){let a=gbAudio();if(!a)return;let o=a.createOscillator(),g=a.createGain();o.type=type;o.frequency.setValueAtTime(Math.max(25,freq),a.currentTime);if(slide)o.frequency.exponentialRampToValueAtTime(Math.max(25,freq+slide),a.currentTime+dur);g.gain.setValueAtTime(Math.max(.0001,vol),a.currentTime);g.gain.exponentialRampToValueAtTime(.0001,a.currentTime+dur);o.connect(g);g.connect(dest||GB_SFX);o.start();o.stop(a.currentTime+dur+.02)}
function gbNoise(dur=.12,vol=.07,filter=1800){let a=gbAudio();if(!a)return;let n=Math.max(1,Math.floor(a.sampleRate*dur)),buf=a.createBuffer(1,n,a.sampleRate),d=buf.getChannelData(0);for(let i=0;i<n;i++)d[i]=(Math.random()*2-1)*Math.pow(1-i/n,1.7);let src=a.createBufferSource(),f=a.createBiquadFilter(),g=a.createGain();src.buffer=buf;f.type='lowpass';f.frequency.value=filter;g.gain.value=vol;src.connect(f);f.connect(g);g.connect(GB_SFX);src.start()}
function playSfx(kind,power=1){if(!save.settings.sfx)return;let a=gbAudio();if(!a)return;if(a.state==='suspended')a.resume();power=Math.max(.5,Math.min(3,power));if(kind==='hit'){gbNoise(.07,.05*power,2200);gbTone(95,.08,'square',.035*power,null,-28)}else if(kind==='fire'){gbNoise(.18,.07*power,1500);gbTone(180,.16,'sawtooth',.045*power,null,-90)}else if(kind==='frost'){gbTone(980,.16,'triangle',.045*power,null,-420);gbTone(1380,.09,'sine',.025*power)}else if(kind==='poison'){gbTone(110,.28,'sine',.045*power,null,-45);gbTone(220,.22,'triangle',.02*power)}else if(kind==='blade'){gbNoise(.08,.035*power,4200);gbTone(620,.1,'triangle',.025*power,null,420)}else if(kind==='boss'){gbTone(52,.42,'sawtooth',.09*power,null,-16);gbNoise(.3,.08*power,700)}else if(kind==='pickup'){gbTone(660,.08,'sine',.03);setTimeout(()=>gbTone(990,.12,'sine',.03),55)}else if(kind==='level'){[440,660,880,1180].forEach((f,i)=>setTimeout(()=>gbTone(f,.22,'triangle',.04),i*70))}}
function musicBeat(){if(!save.settings.music||!GB_AUDIO)return;let roots=[55,55,65.4,49,73.4,65.4,55,82.4],r=roots[GB_BEAT%roots.length],b=GB_BEAT%16;gbTone(r,b%4===0?.55:.28,'sawtooth',b%4===0?.055:.028,GB_MUSIC,-8);if(b%2===0)gbTone(r*2,.15,'square',.018,GB_MUSIC,18);if(b===3||b===7||b===11||b===15)gbNoiseMusic(.08,.018,5200);if(b%8===0){gbTone(r*4,.5,'triangle',.018,GB_MUSIC,120);gbTone(r*6,.7,'sine',.012,GB_MUSIC,-80)}GB_BEAT++}
function gbNoiseMusic(dur=.08,vol=.02,filter=4500){let a=gbAudio();if(!a)return;let n=Math.floor(a.sampleRate*dur),buf=a.createBuffer(1,n,a.sampleRate),d=buf.getChannelData(0);for(let i=0;i<n;i++)d[i]=(Math.random()*2-1)*(1-i/n);let src=a.createBufferSource(),f=a.createBiquadFilter(),g=a.createGain();src.buffer=buf;f.type='highpass';f.frequency.value=filter;g.gain.value=vol;src.connect(f);f.connect(g);g.connect(GB_MUSIC);src.start()}
function ensureMusic(){let a=gbAudio();if(!a)return;if(a.state==='suspended')a.resume();if(GB_MUSIC_TIMER)return;GB_MUSIC_TIMER=setInterval(musicBeat,185)}
function syncAudioSettings(){if(GB_MUSIC)GB_MUSIC.gain.value=save.settings.music?.42:0;if(GB_SFX)GB_SFX.gain.value=save.settings.sfx?.58:0;if(save.settings.music)ensureMusic();persist()}
document.addEventListener('pointerdown',()=>{if(save.settings.music)ensureMusic()},{once:true});

// Add controls to Settings without depending on static HTML shape.
function installAudioControls(){let scr=document.querySelector('#screen-settings')||document.querySelector('[id*=settings]');if(!scr||scr.querySelector('#gbAudioControls'))return;let box=document.createElement('div');box.id='gbAudioControls';box.style.cssText='margin:14px 0;padding:14px;border:1px solid #4a4a4a;border-radius:12px;background:#161616';box.innerHTML=`<div style="font-weight:800;margin-bottom:10px">AUDIO</div><button id="gbMusicToggle" class="primary" style="width:100%;margin:5px 0"></button><button id="gbSfxToggle" class="primary" style="width:100%;margin:5px 0"></button>`;scr.appendChild(box);let refresh=()=>{box.querySelector('#gbMusicToggle').textContent=`MUSIC: ${save.settings.music?'ON':'OFF'}`;box.querySelector('#gbSfxToggle').textContent=`SOUND EFFECTS: ${save.settings.sfx?'ON':'OFF'}`};box.querySelector('#gbMusicToggle').onclick=()=>{save.settings.music=!save.settings.music;syncAudioSettings();refresh()};box.querySelector('#gbSfxToggle').onclick=()=>{save.settings.sfx=!save.settings.sfx;syncAudioSettings();refresh()};refresh()}
setInterval(installAudioControls,1200);

// ---------- HIGHER QUALITY FX ----------
function burstFx(type,x,y,power=1){run.fx2=run.fx2||[];let count=Math.floor(10+power*6);for(let i=0;i<count;i++){let a=Math.random()*Math.PI*2,sp=(35+Math.random()*120)*power;run.fx2.push({type,x,y,vx:Math.cos(a)*sp,vy:Math.sin(a)*sp,life:.35+Math.random()*.45,max:.8,size:2+Math.random()*5*power,spin:Math.random()*6})}}
function updateFx2(dt){if(!run)return;run.fx2=run.fx2||[];for(const f of run.fx2){f.life-=dt;f.x+=f.vx*dt;f.y+=f.vy*dt;f.vx*=Math.pow(.12,dt);f.vy*=Math.pow(.12,dt);if(f.type==='fire')f.vy-=18*dt;if(f.type==='frost')f.vy+=8*dt}run.fx2=run.fx2.filter(f=>f.life>0)}
function drawFx2(){if(!run?.fx2)return;ctx.save();ctx.globalCompositeOperation='lighter';for(const f of run.fx2){let a=Math.max(0,f.life/f.max),x=sx(f.x),y=sy(f.y);ctx.globalAlpha=Math.min(1,a*.9);if(f.type==='fire'){let g=ctx.createRadialGradient(x,y,0,x,y,f.size*3);g.addColorStop(0,'#fff7b0');g.addColorStop(.25,'#ffca45');g.addColorStop(.62,'#ff5a1f');g.addColorStop(1,'#40100000');ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,f.size*3,0,7);ctx.fill()}else if(f.type==='frost'){ctx.strokeStyle='#d9fbff';ctx.lineWidth=Math.max(1,f.size*.45);ctx.beginPath();ctx.moveTo(x-f.size*2,y);ctx.lineTo(x+f.size*2,y);ctx.moveTo(x,y-f.size*2);ctx.lineTo(x,y+f.size*2);ctx.stroke()}else if(f.type==='poison'){ctx.fillStyle='#7dff66';ctx.beginPath();ctx.arc(x,y,f.size*1.6,0,7);ctx.fill()}else{ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x-f.size*2,y);ctx.lineTo(x+f.size*2,y);ctx.stroke()}}ctx.restore()}
const evolveSkillsV120=evolveSkills;evolveSkills=function(dt){evolveSkillsV120(dt);updateFx2(dt)};
const drawV120=draw;draw=function(){drawV120();drawFx2()};

// Hook visible Mythic/elemental activity into richer particles and SFX at controlled cadence.
let gbFxClock=0;const mythicVisualTickV120=mythicVisualTick;mythicVisualTick=function(dt){mythicVisualTickV120(dt);gbFxClock-=dt;if(gbFxClock<=0&&run?.p){gbFxClock=.32;let lv=equippedMythicLevels();if(lv[3]){burstFx('fire',run.p.x,run.p.y,.65);playSfx('fire',.55)}if(Object.keys(lv).some(k=>k>=5&&k<=9)){burstFx('frost',run.p.x,run.p.y,.5)}if(Object.keys(lv).some(k=>k>=10&&k<=14)){burstFx('poison',run.p.x,run.p.y,.5)}if(Object.keys(lv).some(k=>k>=15&&k<=22)){burstFx('blade',run.p.x,run.p.y,.45)}}};

// ---------- LARGE MONSTER THREAT + TERRITORY ----------
function enforceLargeEnemyTerritories(dt){if(!run?.enemies)return;for(const e of run.enemies){if(e.dead||e.kind==='boss'||e.kind==='worldboss')continue;let sz=e.size||1;if(sz<1.35)continue;if(e.homeX===undefined){e.homeX=e.x;e.homeY=e.y;e.territoryRadius=220+Math.min(120,sz*45)}let dHome=Math.hypot(e.x-e.homeX,e.y-e.homeY),dPlayer=Math.hypot(run.p.x-e.x,run.p.y-e.y),territ=e.territoryRadius||280;
// Strongly scale contact damage for big normals. They should be scary, but not one-frame unavoidable kills.
e.damage=Math.max(e.damage||1,11*Math.pow(sz,2.15)*Math.sqrt(Math.max(1,save.world||1)));
// Prevent leap-like motion: cap displacement speed to a grounded pursuit envelope similar to other enemies.
let maxSp=88+Math.min(36,sz*12);e.speed=Math.min(e.speed||maxSp,maxSp);
// Hard leash: once outside territory, return home. Inside leash they may pursue only if player is reasonably near.
if(dHome>territ){let dx=e.homeX-e.x,dy=e.homeY-e.y,m=Math.hypot(dx,dy)||1;e.x+=dx/m*maxSp*dt;e.y+=dy/m*maxSp*dt;if(dHome>territ*1.35){e.x=e.homeX+dx/m*territ*.9;e.y=e.homeY+dy/m*territ*.9}}
else if(dPlayer>territ*1.15){let dx=e.homeX-e.x,dy=e.homeY-e.y,m=Math.hypot(dx,dy)||1;if(m>18){e.x+=dx/m*maxSp*.75*dt;e.y+=dy/m*maxSp*.75*dt}}
}}
const updateV120=update;update=function(dt){updateV120(dt);enforceLargeEnemyTerritories(dt)};

// Danger feedback when a large monster lands contact near the player.
let gbDangerClock=0;const updateV120b=update;update=function(dt){updateV120b(dt);gbDangerClock-=dt;if(gbDangerClock<=0&&run?.enemies){for(const e of run.enemies){if(e.dead||e.kind==='boss'||e.kind==='worldboss'||(e.size||1)<1.35)continue;if(Math.hypot(e.x-run.p.x,e.y-run.p.y)<e.r+run.p.r+8){gbDangerClock=.22;burstFx('hit',run.p.x,run.p.y,Math.min(1.4,e.size||1));playSfx('hit',Math.min(1.8,e.size||1));break}}}}
'''
head,tail=s.rsplit(end,1);p.write_text(head+'\n'+block+'\n'+end+tail)
