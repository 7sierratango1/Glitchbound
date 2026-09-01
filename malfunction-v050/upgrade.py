from pathlib import Path
import re
p=Path('mm050/app/src/main/java/com/technicallyunavailable/malfunctionmarbles/GameRenderer.java')
s=p.read_text()
s=s.replace('private static final int MARBLES=10, POINTS=520;','private static final int MARBLES=10, POINTS=620;')
s=s.replace('private final float[] cameraPos=new float[3];\n    private int lastPlace=-1,lastCountdown=-99;','private final float[] cameraPos=new float[3];\n    private final float[] smoothEye=new float[3],smoothTarget=new float[3];\n    private boolean cameraPrimed=false;\n    private int lastPlace=-1,lastCountdown=-99;')
s=s.replace('float progress,velocity,lane,laneVelocity,spin,air,airVelocity;','float progress,velocity,lane,laneVelocity,spin,air,airVelocity,funnelAngle;')
s=s.replace('r.spin=0;r.air=0;r.airVelocity=0;r.finished=false;', 'r.spin=0;r.air=0;r.airVelocity=0;r.funnelAngle=i*.55f;r.finished=false;')
s=s.replace('public void resetToPreview(){state=PREVIEW;stateNs=System.nanoTime();lastNs=0;stateTime=0;totalTime=0;lastPlace=-1;lastCountdown=-99;resetRacers();pushHud(true);}', 'public void resetToPreview(){state=PREVIEW;stateNs=System.nanoTime();lastNs=0;stateTime=0;totalTime=0;lastPlace=-1;lastCountdown=-99;cameraPrimed=false;resetRacers();pushHud(true);}')
start=s.index('    private void buildMap(){'); end=s.index('\n    private void update(float dt){',start)
s=s[:start]+'''    private void buildMap(){
        float seed=mapIndex+1;float turns=5.0f+(mapIndex%5)*.74f;float length=560f+(mapIndex%4)*62f;
        for(int i=0;i<POINTS;i++){
            float t=i/(float)(POINTS-1);float a=t*turns*6.28318f;
            float x=(float)Math.sin(a)*20f+(float)Math.sin(t*37f+seed)*3.8f;
            float z=t*length+(float)Math.cos(a*.63f+seed)*12f+(float)Math.sin(t*13f)*5f;
            float y=66f-t*(170f+(mapIndex%5)*8f);
            if(t>.08f&&t<.16f){float q=(t-.08f)/.08f,ang=q*12.566f;x+=(float)Math.sin(ang)*13f;z+=(float)Math.cos(ang)*13f;y-=q*10f;}
            if(t>.34f&&t<.45f){float q=(t-.34f)/.11f,ang=q*18.849f;x+=(float)Math.cos(ang)*17f;z+=(float)Math.sin(ang)*17f;y-=q*13f;}
            if(t>.70f&&t<.80f){float q=(t-.70f)/.10f,ang=q*12.566f;x+=(float)Math.sin(ang)*14f;z+=(float)Math.cos(ang)*14f;y-=q*11f;}
            if(t>=.20f&&t<=.285f){float q=(t-.20f)/.085f;float[] entry=basePoint(.20f,seed,turns,length);float[] exit=basePoint(.285f,seed,turns,length);x=mix(entry[0],exit[0],q)*.94f;z=entry[2]+q*6.5f;y=entry[1]-q*34f;}
            if(t>.285f&&t<.315f){float q=(t-.285f)/.03f;y-=34f*(1f-q);}
            if(mapIndex%5==1)x+=(float)Math.sin(t*49f)*5f;
            if(mapIndex%5==2){x+=(float)Math.sin(t*17f)*9f;z+=(float)Math.sin(t*11f)*7f;}
            if(mapIndex%5==3&&t>.49f&&t<.61f)y-=8f*(float)Math.sin((t-.49f)/.12f*3.14159f);
            if(mapIndex%5==4)x+=(float)Math.sin(t*33f)*6f;
            path[i][0]=x;path[i][1]=y;path[i][2]=z;
        }
        for(int i=0;i<10;i++){path[i][1]=40f-i*.12f;path[i][0]*=.16f;}
        for(int i=POINTS-10;i<POINTS;i++)path[i][1]=path[POINTS-10][1]-(i-(POINTS-10))*.12f;
    }
    private float[] basePoint(float t,float seed,float turns,float length){float a=t*turns*6.28318f;return new float[]{(float)Math.sin(a)*20f+(float)Math.sin(t*37f+seed)*3.8f,66f-t*(170f+(mapIndex%5)*8f),t*length+(float)Math.cos(a*.63f+seed)*12f+(float)Math.sin(t*13f)*5f};}
'''+s[end:]
s=s.replace('''            float downhill=clamp(-dy/horiz,-.28f,.72f);
            float accel=.0018f+.0052f*Math.max(0,downhill); // gravity projected down slope
            r.velocity+=accel*dt;r.velocity*=1f-.055f*dt;
            r.laneVelocity*=1f-.75f*dt;r.lane+=r.laneVelocity*dt;
''','''            float slope=clamp(-dy/horiz,-.35f,2.5f);float curvature=trackCurvature(p);
            float accel=.0011f+.0048f*Math.max(0,slope);float rolling=.032f+.065f*Math.min(1f,curvature*.85f);
            if(curvature>.85f&&slope>.12f)accel+=.0015f*Math.min(1.8f,curvature);
            r.velocity+=accel*dt;r.velocity*=Math.max(.90f,1f-rolling*dt);
            r.laneVelocity*=Math.max(.72f,1f-1.35f*dt);r.lane+=r.laneVelocity*dt;
''')
s=s.replace('if(r.air>0||r.airVelocity!=0){r.airVelocity-=8.8f*dt;r.air+=r.airVelocity*dt;if(r.air<0){r.air=0;r.airVelocity=0;}}','if(r.air>0||r.airVelocity!=0){r.airVelocity-=9.81f*dt;r.air+=r.airVelocity*dt;if(r.air<0){r.air=0;r.airVelocity=0;r.velocity*=.985f;}}')
start=s.index('    private void applyCourseFeature'); end=s.index('\n    private static boolean in',start)
s=s[:start]+'''    private void applyCourseFeature(Racer r,int i,float dt,float p){
        if(in(p,.20f,.285f)){int row=(int)((p-.20f)/.085f*12f);float target=((row+i)%2==0?1f:-1f)*(0.65f+(row%3)*.52f);r.laneVelocity+=(target-r.lane)*3.1f*dt;if(((int)(p*2400)+i*7)%19==0){r.laneVelocity+=(rng.nextFloat()-.5f)*.55f;r.velocity*=.9975f;}r.velocity+=.0020f*dt;}
        if(in(p,.315f,.34f)){float desired=(float)Math.sin(p*92f+i*.8f)*2.0f;r.laneVelocity+=(desired-r.lane)*1.45f*dt;}
        if(in(p,.455f,.475f))r.velocity+=.0040f*dt;
        if(p>.492f&&p<.501f&&r.air==0&&r.airVelocity==0){r.airVelocity=4.8f+(i%3)*.20f;r.velocity+=.0010f;}
        if(in(p,.57f,.645f)){float q=(p-.57f)/.075f;r.funnelAngle+=dt*(2.4f+q*8.4f);r.lane=(float)Math.sin(r.funnelAngle)*(2.7f*(1f-q)+.35f);r.velocity+=.00045f*q*dt;}
        if(p>.645f&&p<.655f)r.velocity+=.0018f*dt;
        if(in(p,.70f,.755f)){float blocker=(float)Math.sin(totalTime*2.3f+p*24f)*2.5f;if(Math.abs(r.lane-blocker)<.60f){r.velocity*=Math.max(.90f,1f-1.35f*dt);r.laneVelocity+=(r.lane>=blocker?1:-1)*1.4f*dt;}}
        if(in(p,.805f,.825f)&&Math.abs(r.lane)<1.15f)r.velocity+=.0046f*dt;
        if(in(p,.87f,.925f)&&rng.nextFloat()<dt*1.8f){r.laneVelocity+=(rng.nextFloat()-.5f)*1.7f;r.velocity*=.996f;}
        if(mapIndex%4==1&&in(p,.12f,.15f))r.velocity*=Math.max(.96f,1f-.12f*dt);
        if(mapIndex%4==2&&in(p,.52f,.55f))r.laneVelocity+=(float)Math.sin(totalTime*4+i)*.45f*dt;
        if(mapIndex%4==3&&in(p,.66f,.69f))r.velocity+=.0015f*dt;
        r.velocity=clamp(r.velocity,.0029f,.0128f);
    }
    private float trackCurvature(float p){float[] a=sample(Math.max(.001f,p-.008f)),b=sample(p),c=sample(Math.min(.999f,p+.008f));float ax=b[0]-a[0],az=b[2]-a[2],bx=c[0]-b[0],bz=c[2]-b[2];float al=(float)Math.sqrt(ax*ax+az*az)+.001f,bl=(float)Math.sqrt(bx*bx+bz*bz)+.001f;float dot=clamp((ax*bx+az*bz)/(al*bl),-1f,1f);return (float)Math.acos(dot)*1.65f;}
'''+s[end:]
s=s.replace('float av=(a.velocity+b.velocity)*.5f;a.velocity=av*.985f+(rng.nextFloat()-.5f)*.00035f;b.velocity=av*.985f+(rng.nextFloat()-.5f)*.00035f;\n                if(a.progress>b.progress)a.progress+=.00018f;else b.progress+=.00018f;','float av=(a.velocity+b.velocity)*.5f;a.velocity=av*.992f+(rng.nextFloat()-.5f)*.00012f;b.velocity=av*.992f+(rng.nextFloat()-.5f)*.00012f;')
start=s.index('    private void setupCamera(){'); end=s.index('\n    private float packSpread',start)
s=s[:start]+'''    private void setupCamera(){
        float[] eye=new float[3],target=new float[3];
        if(state==PREVIEW){float t=(stateTime*.055f)%1f;float[] mid=sample(.48f);float a=t*6.28318f;eye[0]=mid[0]+(float)Math.cos(a)*72f;eye[1]=mid[1]+44f;eye[2]=mid[2]+(float)Math.sin(a)*72f;target=mid;}
        else if(state==COUNTDOWN){float[] start=sample(.012f),ahead=sample(.06f);eye[0]=start[0]-13f;eye[1]=start[1]+9f;eye[2]=start[2]-15f;target[0]=ahead[0];target[1]=start[1]+.7f;target[2]=ahead[2];}
        else{Racer focus=racers[0];float p=focus.finished?.985f:focus.progress;float[] pos=racerPosition(focus,p),ahead=sample(Math.min(.999f,p+.028f));float dx=ahead[0]-pos[0],dy=ahead[1]-pos[1],dz=ahead[2]-pos[2];float len=(float)Math.sqrt(dx*dx+dy*dy+dz*dz)+.001f;dx/=len;dy/=len;dz/=len;float spread=packSpread(p);float zoom=9.8f+Math.min(4.5f,spread*.58f);if(in(p,.20f,.285f)||in(p,.57f,.65f))zoom+=2.2f;eye[0]=pos[0]-dx*zoom;eye[1]=pos[1]+6.7f;eye[2]=pos[2]-dz*zoom;target[0]=pos[0]+dx*5.7f;target[1]=pos[1]+.75f;target[2]=pos[2]+dz*5.7f;}
        if(!cameraPrimed){System.arraycopy(eye,0,smoothEye,0,3);System.arraycopy(target,0,smoothTarget,0,3);cameraPrimed=true;}
        float k=state==RUNNING?.115f:.18f;for(int j=0;j<3;j++){smoothEye[j]=mix(smoothEye[j],eye[j],k);smoothTarget[j]=mix(smoothTarget[j],target[j],k);}cameraPos[0]=smoothEye[0];cameraPos[1]=smoothEye[1];cameraPos[2]=smoothEye[2];Matrix.setLookAtM(view,0,smoothEye[0],smoothEye[1],smoothEye[2],smoothTarget[0],smoothTarget[1],smoothTarget[2],0,1,0);Matrix.multiplyMM(vp,0,proj,0,view,0);
    }
    private float[] racerPosition(Racer r,float p){float[] pos=sampleOffset(clamp(p,0,.995f),r.lane);if(in(p,.57f,.645f)){float q=(p-.57f)/.075f,rad=2.9f*(1f-q)+.35f;float[] c=sample(p);pos[0]=c[0]+(float)Math.cos(r.funnelAngle)*rad;pos[2]=c[2]+(float)Math.sin(r.funnelAngle)*rad;pos[1]=c[1]+.32f*(1f-q);}pos[1]+=.72f+r.air;return pos;}
'''+s[end:]
s=s.replace('drawBeam(a,b,3.6f,.32f,new float[]{.10f,.11f,.14f},.82f,.24f,0f,1f);','drawBeam(a,b,3.6f,.32f,new float[]{.20f,.22f,.28f},.42f,.20f,.05f,.72f);')
s=s.replace('drawPegboard(.19f,.30f,theme);','drawPegboard(.20f,.285f,theme);').replace('drawTunnel(.305f,.34f,new float[]{.17f,.18f,.22f});','drawTunnel(.315f,.34f,new float[]{.22f,.25f,.32f});')
s=s.replace('Racer r=racers[i];float p=clamp(r.progress,0,.995f);float[] pos=sampleOffset(p,r.lane);float s=i==0?.72f:.66f;float y=pos[1]+.72f+r.air;','Racer r=racers[i];float p=clamp(r.progress,0,.995f);float[] pos=racerPosition(r,p);float s=i==0?.72f:.66f;float y=pos[1];')
s=s.replace('float[] back=sampleOffset(Math.max(.001f,p-.0045f),r.lane);for(int f=0;f<5;f++){float q=f/4f;float fx=mix(pos[0],back[0],q),fy=mix(y,back[1]+.72f,q)+(float)Math.sin(totalTime*15f+f)*.18f,fz=mix(pos[2],back[2],q);float fs=.42f*(1f-q*.72f);','float[] back=sampleOffset(Math.max(.001f,p-.0060f),r.lane);for(int f=0;f<6;f++){float q=f/5f;float fx=mix(pos[0],back[0],q),fy=mix(y,back[1]+.72f,q)+.05f*(1f-q),fz=mix(pos[2],back[2],q);float fs=.40f*(1f-q*.72f);')
start=s.index('    private void drawPegboard'); end=s.index('    private void drawBumperField',start)
s=s[:start]+'''    private void drawPegboard(float a,float b,float[] color){float[] top=sample(a),bottom=sample(b);float midY=(top[1]+bottom[1])*.5f,midZ=(top[2]+bottom[2])*.5f;drawBox((top[0]+bottom[0])*.5f,midY,midZ,3.7f,Math.abs(top[1]-bottom[1])*.52f,.12f,new float[]{.22f,.25f,.31f},0,.18f,.22f,.08f,.34f);for(int row=0;row<12;row++)for(int col=-3;col<=3;col++){float q=row/11f;float y=mix(top[1]-1.4f,bottom[1]+1.4f,q),x=mix(top[0],bottom[0],q)+(col+(row%2)*.5f)*.86f,z=midZ-.10f;drawSphereMaterial(x,y,z,.25f,color,.52f,.20f,.20f,.92f,0);}drawBox(top[0],top[1]+.25f,top[2],3.8f,.16f,1.2f,new float[]{.35f,.38f,.45f},0,.30f,.2f,.04f,.74f);drawBox(bottom[0],bottom[1]-.15f,bottom[2],3.8f,.16f,1.2f,new float[]{.35f,.38f,.45f},0,.30f,.2f,.04f,.74f);}
    private void drawTunnel(float a,float b,float[] color){for(int j=0;j<13;j++){float p=a+(b-a)*(j/12f),radius=4.0f;float[] c=sample(p),n=sample(Math.min(.999f,p+.006f));float yaw=yawTo(c,n);for(int q=0;q<12;q++){double rad=Math.toRadians(q*30f);float ox=(float)Math.cos(rad)*radius,oy=(float)Math.sin(rad)*radius+1.2f;Matrix.setIdentityM(model,0);Matrix.translateM(model,0,c[0]+ox,c[1]+oy,c[2]);Matrix.rotateM(model,0,yaw,0,1,0);Matrix.scaleM(model,0,.22f,.22f,.62f);draw(cube,color,.38f,.17f,.10f,.58f);}}}
'''+s[end:]
s=re.sub(r'    private void drawFunnel\(float a,float b,float\[\] color\)\{.*?\n    private void drawMovingBlockers','    private void drawFunnel(float a,float b,float[] color){for(int j=0;j<16;j++){float p=a+(b-a)*(j/15f);float radius=3.5f-(j/15f)*2.6f;float[] c=sample(p);for(int q=0;q<14;q++){double rad=Math.toRadians(q*(360f/14f));drawSphereMaterial(c[0]+(float)Math.cos(rad)*radius,c[1]+.9f-(j/15f)*1.1f,c[2]+(float)Math.sin(rad)*radius,.20f,color,.30f,.18f,.16f,.62f,0);}}}\n    private void drawMovingBlockers',s,flags=re.S)
p.write_text(s)
b=Path('mm050/app/build.gradle');t=b.read_text().replace('versionCode 4','versionCode 5').replace("versionName '0.4.0'","versionName '0.5.0'");b.write_text(t)
