from pathlib import Path
p=Path('app/src/main/assets/www/game.js')
s=p.read_text()

# v1.0.2: gear opened from a loot pickup is an in-run pause, never a run exit/restart.
old="gear.onclick=()=>{run.choosing=false;$('#choiceOverlay').classList.add('hidden');open('gear');renderGear()}"
new="gear.onclick=()=>{run.choosing=true;run.gearPause=true;$('#choiceOverlay').classList.add('hidden');open('gear');renderGear();showGearResume()}"
if old not in s: raise SystemExit('missing loot gear handler')
s=s.replace(old,new,1)

marker="function updateGroundLoot(dt){"
if marker not in s: raise SystemExit('missing ground loot marker')
helper=r'''
function showGearResume(){let screen=$('#screen-gear'),old=$('#gearResumeBtn');if(old)old.remove();let b=document.createElement('button');b.id='gearResumeBtn';b.className='primary';b.style.cssText='position:sticky;bottom:14px;z-index:50;width:calc(100% - 28px);margin:14px;font-size:16px;padding:14px';b.textContent='▶ CONTINUE CURRENT RUN';b.onclick=resumeFromGear;screen.appendChild(b)}
function resumeFromGear(){let b=$('#gearResumeBtn');if(b)b.remove();open('game');run.gearPause=false;run.choosing=false;$('#pauseOverlay').classList.add('hidden');$('#choiceOverlay').classList.add('hidden')}
'''
s=s.replace(marker,helper+marker,1)

# If the normal Gear back arrow is used during a run, resume that exact run too.
marker2="p.write_text(s)"
# runtime event listener installed after existing bindings; capture phase prevents navigation back to camp.
append=r'''

# Add a capture listener near the end of the game script so Gear's back arrow resumes gameplay when gearPause is active.
s += r"""
document.addEventListener('click',function(ev){let b=ev.target.closest&&ev.target.closest('#screen-gear .back');if(b&&run&&run.gearPause){ev.preventDefault();ev.stopImmediatePropagation();resumeFromGear()}},true);
"""
'''
# execute append logic in this patch script itself
exec(append)
p.write_text(s)
