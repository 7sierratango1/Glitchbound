from pathlib import Path
p=Path('mm090/app/src/main/java/com/technicallyunavailable/malfunctionmarbles/GameRenderer.java')
s=p.read_text()

def R(a,b):
    global s
    if a not in s:
        raise SystemExit('missing pattern: '+a[:120])
    s=s.replace(a,b,1)

R('''    static class Racer {
        float progress,velocity,lane,laneVelocity,spin,air,airVelocity,funnelAngle; // velocity = world units/second
        boolean finished;
        float finishTime;
        float[] color=new float[3];
    }''','''    static class Racer {
        // Independent per-marble physical state. Track provides contact/guidance, never a shared animation speed.
        float progress,velocity,lane,laneVelocity,spin,air,airVelocity,funnelAngle;
        float mass,restitution,rolling,driftBias,spinBias;
        int lastPegRow,lastBumperBucket,lastBlockBucket;
        boolean finished;
        float finishTime;
        float[] color=new float[3];
    }''')

R('''    private void resetRacers(){
        for(int i=0;i<MARBLES;i++){
            Racer r=racers[i];int row=i/5,col=i%5;r.progress=.006f+row*.008f;r.velocity=0;r.lane=(col-2)*1.08f+(row==1?.52f:0);r.laneVelocity=0;r.spin=0;r.air=0;r.airVelocity=0;r.funnelAngle=i*.55f;r.finished=false;r.finishTime=999f;
        }
    }''','''    private void resetRacers(){
        for(int i=0;i<MARBLES;i++){
            Racer r=racers[i];int row=i/5,col=i%5;
            r.progress=.006f+row*.008f;
            r.velocity=0;
            r.lane=(col-2)*1.08f+(row==1?.52f:0)+(rng.nextFloat()-.5f)*.10f;
            r.laneVelocity=(rng.nextFloat()-.5f)*.08f;
            r.spin=0;r.air=0;r.airVelocity=0;r.funnelAngle=i*.55f+rng.nextFloat()*.45f;
            r.mass=.88f+rng.nextFloat()*.26f;
            r.restitution=.56f+rng.nextFloat()*.25f;
            r.rolling=.0075f+rng.nextFloat()*.0075f;
            r.driftBias=(rng.nextFloat()-.5f)*.22f;
            r.spinBias=.92f+rng.nextFloat()*.18f;
            r.lastPegRow=-1;r.lastBumperBucket=-1;r.lastBlockBucket=-1;
            r.finished=false;r.finishTime=999f;
        }
    }''')

R('if(state==COUNTDOWN){if(stateTime>=5.15f){for(Racer r:racers)r.velocity=Math.max(r.velocity,1.35f);state=RUNNING;stateNs=System.nanoTime();stateTime=0;}pushHud(false);return;}','if(state==COUNTDOWN){if(stateTime>=5.15f){for(int i=0;i<MARBLES;i++){Racer r=racers[i];r.velocity=1.05f+rng.nextFloat()*.75f;r.laneVelocity+=(rng.nextFloat()-.5f)*.22f;}state=RUNNING;stateNs=System.nanoTime();stateTime=0;}pushHud(false);return;}')

start=s.index('    private void update(float dt){')
end=s.index('\n    private void applyCourseFeature',start)
s=s[:start]+'''    private void update(float dt){
        if(state==COUNTDOWN){if(stateTime>=5.15f){for(int i=0;i<MARBLES;i++){Racer r=racers[i];r.velocity=1.05f+rng.nextFloat()*.75f;r.laneVelocity+=(rng.nextFloat()-.5f)*.22f;}state=RUNNING;stateNs=System.nanoTime();stateTime=0;}pushHud(false);return;}
        if(state!=RUNNING){pushHud(false);return;}

        int done=0;
        for(int i=0;i<MARBLES;i++){
            Racer r=racers[i];if(r.finished){done++;continue;}
            float p=clamp(r.progress,0,.998f);
            float[] a=sample(Math.max(.001f,p-.003f)),b=sample(Math.min(.999f,p+.003f));
            float dx=b[0]-a[0],dy=b[1]-a[1],dz=b[2]-a[2];float ds=(float)Math.sqrt(dx*dx+dy*dy+dz*dz)+.001f;
            float sinTheta=clamp(-dy/ds,-1f,1f);float curvature=trackCurvature(p);

            // Solid sphere rolling acceleration plus each marble's own losses.
            float gravityAccel=(5f/7f)*9.81f*sinTheta;
            float normalFactor=(float)Math.sqrt(Math.max(0f,1f-sinTheta*sinTheta));
            float rollingResistance=r.rolling*9.81f*normalFactor;
            float aeroDrag=.00145f*r.velocity*r.velocity;
            float curveScrub=Math.min(1.6f,curvature*.46f)*r.velocity*(.060f+r.rolling*2.5f);
            float accel=gravityAccel-(r.velocity>0?rollingResistance:0f)-aeroDrag-curveScrub;

            // Track traction only prevents a dead numerical stall; it does not synchronize speeds.
            if(r.velocity<.72f)accel+=.52f*(1f-r.velocity/.72f);
            r.velocity=Math.max(.18f,r.velocity+accel*dt);

            // Independent lateral dynamics. Curves, tiny surface imperfections, and entry angle change each line.
            float curveSide=trackCurveSign(p);
            float lateralAccel=curveSide*curvature*r.velocity*r.velocity*.016f+r.driftBias*.12f;
            r.laneVelocity+=lateralAccel*dt;
            r.laneVelocity*=Math.max(.74f,1f-(.54f+r.rolling*18f)*dt);
            r.lane+=r.laneVelocity*dt;

            applyCourseFeature(r,i,dt,p);
            r.progress+=worldDistanceToProgress(Math.max(0f,r.velocity)*dt,p);
            r.spin+=(r.velocity/.68f)*dt*57.2958f*r.spinBias;

            if(r.air>0||r.airVelocity!=0){
                r.airVelocity-=9.81f*dt;r.air+=r.airVelocity*dt;
                if(r.air<0){float impact=-r.airVelocity;r.air=0;r.airVelocity=impact>.9f?impact*r.restitution*.12f:0f;r.velocity*=Math.max(.88f,1f-impact*.006f);r.laneVelocity+=(rng.nextFloat()-.5f)*Math.min(.65f,impact*.045f);}
            }

            // Physical side-wall contact: reflect lateral velocity with energy loss rather than snapping silently.
            if(r.lane>3.15f){float over=r.lane-3.15f;r.lane=3.15f-over*.15f;r.laneVelocity=-Math.abs(r.laneVelocity)*r.restitution;r.velocity*=.985f;}
            if(r.lane<-3.15f){float over=-3.15f-r.lane;r.lane=-3.15f+over*.15f;r.laneVelocity=Math.abs(r.laneVelocity)*r.restitution;r.velocity*=.985f;}

            if(r.progress>=.992f){r.progress=.992f;r.finished=true;r.finishTime=stateTime;done++;}
        }
        solveMarbleCollisions();
        if(done==MARBLES){state=FINISHED;stateNs=System.nanoTime();stateTime=0;}
        pushHud(false);
    }

    private float trackCurveSign(float p){
        float[] a=sample(Math.max(.001f,p-.006f)),b=sample(p),c=sample(Math.min(.999f,p+.006f));
        float ax=b[0]-a[0],az=b[2]-a[2],bx=c[0]-b[0],bz=c[2]-b[2];
        float cross=ax*bz-az*bx;return cross>=0?1f:-1f;
    }
'''+s[end:]

start=s.index('    private void applyCourseFeature(Racer r,int i,float dt,float p){')
end=s.index('\n    private float worldDistanceToProgress',start)
s=s[:start]+'''    private void applyCourseFeature(Racer r,int i,float dt,float p){
        // Vertical pegboard: one collision opportunity per row. Result depends on exact lane, speed, mass and restitution.
        if(in(p,.20f,.285f)){
            int row=Math.max(0,Math.min(11,(int)((p-.20f)/.085f*12f)));
            if(row!=r.lastPegRow){
                r.lastPegRow=row;float stagger=((row&1)==0?0f:.43f);float nearest=Math.round((r.lane-stagger)/.86f)*.86f+stagger;float delta=r.lane-nearest;
                if(Math.abs(delta)<.36f){float side=(Math.abs(delta)<.045f?(rng.nextBoolean()?1f:-1f):(delta>=0?1f:-1f));float impulse=(1.25f+r.velocity*.10f)*(1.15f/r.mass);r.laneVelocity+=side*impulse*(.65f+r.restitution);r.velocity*=.90f+r.restitution*.07f;r.airVelocity+=.16f+rng.nextFloat()*.18f;}
            }
        }

        // Groove section: spring-like contact guides toward the groove but momentum controls overshoot and exit line.
        if(in(p,.315f,.34f)){float groove=(float)Math.sin(p*92f)*2.05f;float spring=(groove-r.lane)*2.15f-r.laneVelocity*.72f;r.laneVelocity+=spring*dt;}

        if(in(p,.455f,.475f))r.velocity+=5.0f*dt;

        // Actual launch impulse; all marbles launch with slightly different existing velocity/contact state.
        if(p>.492f&&p<.501f&&r.air==0&&r.airVelocity==0){r.airVelocity=5.15f+r.velocity*.085f+rng.nextFloat()*.45f;r.velocity+=.75f+rng.nextFloat()*.65f;r.laneVelocity+=(rng.nextFloat()-.5f)*.35f;}

        // Funnel groove attracts toward a moving orbital channel; it no longer assigns lane directly.
        if(in(p,.57f,.645f)){float q=(p-.57f)/.075f;float radius=2.9f*(1f-q)+.35f;float omega=Math.max(1.1f,r.velocity/Math.max(.55f,radius));r.funnelAngle+=dt*omega;float target=(float)Math.sin(r.funnelAngle)*radius;float grooveForce=(target-r.lane)*(2.2f+q*2.8f)-r.laneVelocity*(.35f+q*.45f);r.laneVelocity+=grooveForce*dt;r.velocity*=Math.max(.982f,1f-(.010f+r.rolling)*dt);}
        if(p>.645f&&p<.655f)r.velocity+=1.8f*dt;

        // Moving blockers: impact only when crossing a bucket near the blocker, then reflect lateral momentum.
        if(in(p,.70f,.755f)){int bucket=(int)((p-.70f)/.055f*8f);float blocker=(float)Math.sin(totalTime*2.3f+bucket*.85f)*2.5f;if(bucket!=r.lastBlockBucket&&Math.abs(r.lane-blocker)<.68f){r.lastBlockBucket=bucket;float side=r.lane>=blocker?1f:-1f;r.laneVelocity+=side*(1.4f+r.velocity*.06f)*(1.1f/r.mass);r.velocity*=.84f+r.restitution*.10f;r.airVelocity+=rng.nextFloat()*.22f;}}

        if(in(p,.805f,.825f)&&Math.abs(r.lane)<1.15f)r.velocity+=5.8f*dt;

        // Bumper/pinball field: discrete contacts, not random continuous steering.
        if(in(p,.87f,.925f)){int bucket=(int)((p-.87f)/.055f*12f);float bumperLane=(float)Math.sin(bucket*2.17f+mapIndex*.7f)*2.35f;if(bucket!=r.lastBumperBucket&&Math.abs(r.lane-bumperLane)<.78f){r.lastBumperBucket=bucket;float side=r.lane>=bumperLane?1f:-1f;r.laneVelocity+=side*(1.8f+r.velocity*.085f)*(1.15f/r.mass);r.velocity*=.88f+r.restitution*.08f;r.airVelocity+=.12f+rng.nextFloat()*.28f;}}

        if(in(p,.94f,.985f)){r.velocity+=2.4f*dt;r.laneVelocity+=(-r.lane)*1.35f*dt;}
        if(p>.985f)r.velocity=Math.max(r.velocity,2.2f);
        if(mapIndex%4==1&&in(p,.12f,.15f))r.velocity*=Math.max(.97f,1f-.055f*dt);
        if(mapIndex%4==2&&in(p,.52f,.55f))r.laneVelocity+=(float)Math.sin(totalTime*4+i*1.37f)*.40f*dt;
        if(mapIndex%4==3&&in(p,.66f,.69f))r.velocity+=2.0f*dt;
        r.velocity=clamp(r.velocity,.18f,34f);
    }
'''+s[end:]

start=s.index('    private void solveMarbleCollisions(){')
end=s.index('\n    private void pushHud',start)
s=s[:start]+'''    private void solveMarbleCollisions(){
        for(int i=0;i<MARBLES;i++)for(int j=i+1;j<MARBLES;j++){
            Racer a=racers[i],b=racers[j];if(a.finished||b.finished)continue;
            float forward=(a.progress-b.progress)*trackLength;
            float lateral=a.lane-b.lane;
            float vertical=a.air-b.air;
            float d2=forward*forward+lateral*lateral+vertical*vertical;
            float contact=1.34f;
            if(d2<contact*contact){
                float d=(float)Math.sqrt(Math.max(.0001f,d2));float nx=forward/d,ny=lateral/d,nz=vertical/d;
                float rvx=a.velocity-b.velocity,rvy=a.laneVelocity-b.laneVelocity,rvz=a.airVelocity-b.airVelocity;
                float rel=rvx*nx+rvy*ny+rvz*nz;
                if(rel<0f){
                    float e=Math.min(a.restitution,b.restitution);float invA=1f/a.mass,invB=1f/b.mass;
                    float impulse=-(1f+e)*rel/(invA+invB);
                    a.velocity+=impulse*nx*invA;b.velocity-=impulse*nx*invB;
                    a.laneVelocity+=impulse*ny*invA;b.laneVelocity-=impulse*ny*invB;
                    a.airVelocity+=impulse*nz*invA;b.airVelocity-=impulse*nz*invB;
                    a.spin+=impulse*ny*14f;b.spin-=impulse*ny*14f;
                }
                float overlap=contact-d;float invA=1f/a.mass,invB=1f/b.mass,total=invA+invB;
                float pushA=overlap*(invA/total)*.58f,pushB=overlap*(invB/total)*.58f;
                a.lane+=ny*pushA;b.lane-=ny*pushB;
                a.progress+=worldDistanceToProgress(Math.max(0f,nx*pushA),a.progress);
                b.progress=Math.max(0f,b.progress-worldDistanceToProgress(Math.max(0f,nx*pushB),Math.max(0f,b.progress-.001f)));
                if(Math.abs(nz)>.25f){a.air=Math.max(0f,a.air+nz*pushA*.35f);b.air=Math.max(0f,b.air-nz*pushB*.35f);}
                a.velocity=clamp(a.velocity,.18f,34f);b.velocity=clamp(b.velocity,.18f,34f);
            }
        }
    }
'''+s[end:]

# Version bump.
b=Path('mm090/app/build.gradle')
t=b.read_text().replace('versionCode 8','versionCode 9').replace("versionName '0.8.0'","versionName '0.9.0'")
b.write_text(t)
p.write_text(s)
