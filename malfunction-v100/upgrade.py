from pathlib import Path
p=Path('mm100/app/src/main/java/com/technicallyunavailable/malfunctionmarbles/GameRenderer.java')
s=p.read_text()

def R(a,b):
    global s
    if a not in s:
        raise SystemExit('missing pattern: '+a[:140])
    s=s.replace(a,b,1)

# Remove the old low starting shelf that forced racers to crawl uphill into the course.
R('for(int i=0;i<10;i++){path[i][1]=40f-i*.12f;path[i][0]*=.16f;}',
  'for(int i=0;i<10;i++){float q=i/9f;path[i][1]=path[10][1]+5.2f-q*5.2f;path[i][0]*=.16f;}')

# Hold marbles above the starting deck during preview/countdown so the gate release is a gravity drop.
R('r.spin=0;r.air=0;r.airVelocity=0;r.funnelAngle=i*.55f+rng.nextFloat()*.45f;',
  'r.spin=0;r.air=3.2f+row*.34f+rng.nextFloat()*.22f;r.airVelocity=0;r.funnelAngle=i*.55f+rng.nextFloat()*.45f;')

# Release with useful forward momentum; gravity immediately owns the vertical fall.
R('if(state==COUNTDOWN){if(stateTime>=5.15f){for(int i=0;i<MARBLES;i++){Racer r=racers[i];r.velocity=1.05f+rng.nextFloat()*.75f;r.laneVelocity+=(rng.nextFloat()-.5f)*.22f;}state=RUNNING;stateNs=System.nanoTime();stateTime=0;}pushHud(false);return;}',
  'if(state==COUNTDOWN){if(stateTime>=5.15f){for(int i=0;i<MARBLES;i++){Racer r=racers[i];r.velocity=5.2f+rng.nextFloat()*2.2f;r.laneVelocity+=(rng.nextFloat()-.5f)*.30f;r.airVelocity=-.35f-rng.nextFloat()*.35f;}state=RUNNING;stateNs=System.nanoTime();stateTime=0;}pushHud(false);return;}')

# The race should never become a multi-minute crawl on ordinary track. This is traction assist, not speed synchronization.
R('if(r.velocity<.72f)accel+=.52f*(1f-r.velocity/.72f);',
  'if(r.velocity<3.2f)accel+=2.2f*(1f-r.velocity/3.2f);')
R('r.velocity=Math.max(.18f,r.velocity+accel*dt);',
  'r.velocity=Math.max(.85f,r.velocity+accel*dt);')

# Powered lift/conveyor behavior for genuinely steep uphill geometry: machinery carries the marble quickly,
# then releases it back to independent physics as soon as the incline ends.
R('float accel=gravityAccel-(r.velocity>0?rollingResistance:0f)-aeroDrag-curveScrub;',
  'float accel=gravityAccel-(r.velocity>0?rollingResistance:0f)-aeroDrag-curveScrub;\n            if(sinTheta<-.18f){float conveyorTarget=10.5f;accel+=Math.max(0f,(conveyorTarget-r.velocity)*3.8f);}')

# Keep feature-level lower clamps consistent with the new practical pacing floor while preserving variation.
R('r.velocity=clamp(r.velocity,.18f,34f);', 'r.velocity=clamp(r.velocity,.85f,34f);')
R('a.velocity=clamp(a.velocity,.18f,34f);b.velocity=clamp(b.velocity,.18f,34f);',
  'a.velocity=clamp(a.velocity,.85f,34f);b.velocity=clamp(b.velocity,.85f,34f);')

# Version bump.
b=Path('mm100/app/build.gradle')
t=b.read_text().replace('versionCode 9','versionCode 10').replace("versionName '0.9.0'","versionName '0.10.0'")
b.write_text(t)
p.write_text(s)
