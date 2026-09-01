package com.technicallyunavailable.malfunctionmarbles;

import android.opengl.GLES30;
import android.opengl.GLSurfaceView;
import android.opengl.Matrix;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;
import java.nio.ShortBuffer;
import java.util.Random;
import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

public class GameRenderer implements GLSurfaceView.Renderer {
    public interface Listener { void onHud(int place,int total,String mapName,int mapIndex); }
    public volatile Listener listener;

    private static final int MARBLES=10, POINTS=120;
    private static final String[] NAMES={
            "Ember Run","Arc Furnace","Copper Canyon","Blackglass Drop","Molten Switchback",
            "Rift Spiral","Ashfall Circuit","Inferno Junction","Foundry Falls","Obsidian Orbit",
            "Voltage Valley","Static Cliffs","Relay Rush","Surge Shaft","Breaker Bay",
            "Gravity Graveyard","Warpworks","Pendulum Pass","Crusher Corridor","Pinball Foundry",
            "Helix Horizon","Titan Tangle","Malfunction Mile","Redline Reactor","Final Fault"
    };
    private static final float[][] THEMES={
            {1f,.22f,.03f},{1f,.45f,.05f},{.85f,.3f,.08f},{.65f,.1f,.08f},{1f,.12f,.03f},
            {.7f,.08f,.12f},{.8f,.3f,.03f},{1f,.28f,0f},{.85f,.16f,.02f},{.5f,.04f,.04f},
            {.95f,.55f,.08f},{1f,.7f,.18f},{.85f,.25f,.05f},{1f,.35f,.02f},{.7f,.2f,.04f},
            {.8f,.12f,.08f},{1f,.3f,.03f},{.9f,.42f,.06f},{.75f,.08f,.03f},{1f,.5f,.07f},
            {.92f,.18f,.03f},{.7f,.11f,.04f},{1f,.25f,.02f},{.9f,.05f,.02f},{1f,.38f,.04f}
    };

    private int program, uMvp,uModel,uColor,uLight,uCamera,uMetallic,uRoughness,uAlpha,uEmissive;
    private Mesh cube,sphere;
    private int width=1,height=1,mapIndex=0;
    private final float[][] path=new float[POINTS][3];
    private final Racer[] racers=new Racer[MARBLES];
    private final Random rng=new Random(7719);
    private long startNs,lastNs;
    private float raceTime;
    private boolean flyover=true;
    private final float[] proj=new float[16],view=new float[16],vp=new float[16],model=new float[16],mvp=new float[16];
    private final float[] cameraPos=new float[3];
    private int lastPlace=-1;

    static class Racer { float progress,speed,lane,phase; int stunTicks; float[] color=new float[3]; }

    @Override public void onSurfaceCreated(GL10 gl, EGLConfig config){
        GLES30.glEnable(GLES30.GL_DEPTH_TEST); GLES30.glEnable(GLES30.GL_CULL_FACE);
        GLES30.glClearColor(.012f,.012f,.016f,1f);
        program=createProgram(VS,FS); uMvp=GLES30.glGetUniformLocation(program,"uMvp"); uModel=GLES30.glGetUniformLocation(program,"uModel");
        uColor=GLES30.glGetUniformLocation(program,"uColor");uLight=GLES30.glGetUniformLocation(program,"uLight");
        uCamera=GLES30.glGetUniformLocation(program,"uCamera");uMetallic=GLES30.glGetUniformLocation(program,"uMetallic");uRoughness=GLES30.glGetUniformLocation(program,"uRoughness");
        uAlpha=GLES30.glGetUniformLocation(program,"uAlpha");uEmissive=GLES30.glGetUniformLocation(program,"uEmissive");
        cube=Mesh.cube(); sphere=Mesh.sphere(18,14);
        for(int i=0;i<MARBLES;i++){racers[i]=new Racer(); racers[i].color=hsv(i/(float)MARBLES,.75f,1f);}
        buildMap(); restartRace();
    }
    @Override public void onSurfaceChanged(GL10 gl,int w,int h){width=w;height=h;GLES30.glViewport(0,0,w,h);Matrix.perspectiveM(proj,0,55f,w/(float)Math.max(1,h),.1f,500f);}
    @Override public void onDrawFrame(GL10 gl){
        long now=System.nanoTime(); float dt=lastNs==0?0:Math.min(.033f,(now-lastNs)/1_000_000_000f); lastNs=now; raceTime=(now-startNs)/1_000_000_000f;
        update(dt); setupCamera();
        GLES30.glClear(GLES30.GL_COLOR_BUFFER_BIT|GLES30.GL_DEPTH_BUFFER_BIT); GLES30.glUseProgram(program);
        GLES30.glUniform3f(uLight,-.35f,.85f,.25f);
        GLES30.glUniform3fv(uCamera,1,cameraPos,0);
        drawWorld();
    }

    public void selectRelative(int d){mapIndex=(mapIndex+d+NAMES.length)%NAMES.length;buildMap();restartRace();}
    public void restartRace(){
        startNs=System.nanoTime();lastNs=0;raceTime=0;flyover=true;lastPlace=-1;
        for(int i=0;i<MARBLES;i++){Racer r=racers[i];r.progress=-i*.007f;r.speed=.048f+rng.nextFloat()*.006f;r.lane=(i-4.5f)*.30f;r.phase=rng.nextFloat()*6.28f;r.stunTicks=0;}
        pushHud();
    }

    private void buildMap(){
        float seed=mapIndex+1, turns=2.2f+(mapIndex%5)*.55f, radius=19f+(mapIndex%4)*2.7f;
        for(int i=0;i<POINTS;i++){
            float t=i/(float)(POINTS-1), a=t*turns*6.28318f;
            float wobble=(float)Math.sin(t*6.28318f*(2+(mapIndex%3)))*3.3f;
            float r=radius+wobble+(float)Math.sin(a*.5f+seed)*2.2f;
            float x=(float)Math.cos(a)*r;
            float z=(float)Math.sin(a)*r;
            float y=8f + (float)Math.sin(a*1.35f+seed)*5f - t*(4f+(mapIndex%6)*1.7f);
            if(mapIndex%5==1)y+=(float)Math.sin(t*31f)*2f;
            if(mapIndex%5==2){x+=t*22f; z-=t*12f;}
            if(mapIndex%5==3)y-=Math.max(0,t-.55f)*20f;
            if(mapIndex%5==4){float h=(float)Math.sin(t*12.56f);x+=h*7f;}
            path[i][0]=x;path[i][1]=y;path[i][2]=z;
        }
    }

    private void update(float dt){
        if(raceTime<6.5f){flyover=true;pushHud();return;} flyover=false;
        for(int i=0;i<MARBLES;i++){
            Racer r=racers[i]; if(r.progress>=1f)continue;
            if(r.stunTicks>0){r.stunTicks--;continue;}
            float skill=i==0?1.0f:.93f+rng.nextFloat()*.12f;
            r.speed += ((.055f*skill)-r.speed)*dt*.75f;
            r.speed += (rng.nextFloat()-.5f)*.0025f*dt;
            float p=Math.max(0,r.progress);
            if(crossed(p,.18f,dt,r.speed) && ((mapIndex+i)%3==0)) r.stunTicks=10+(i%12);
            if(p>.33f&&p<.39f) r.speed*=1f-.15f*dt;
            if(p>.51f&&p<.535f && ((mapIndex+i)%4==1)) r.progress+=.035f;
            if(p>.66f&&p<.71f) r.speed+=.018f*dt;
            if(p>.79f&&p<.83f && rng.nextFloat()<dt*.32f) r.stunTicks=8;
            r.progress += r.speed*dt;
            r.lane += (float)Math.sin(raceTime*1.8f+r.phase)*dt*.04f;
        }
        pushHud();
    }
    private boolean crossed(float p,float at,float dt,float speed){return p<at&&p+speed*dt>=at;}

    private void pushHud(){
        int place=1;float player=racers[0].progress;for(int i=1;i<MARBLES;i++)if(racers[i].progress>player)place++;
        if(listener!=null && (place!=lastPlace || ((int)(raceTime*3)%3==0))){lastPlace=place;listener.onHud(place,MARBLES,NAMES[mapIndex],mapIndex);}
    }

    private void setupCamera(){
        float[] eye=new float[3],target=new float[3];
        if(flyover){
            float t=Math.min(1f,raceTime/6.5f), a=t*6.28318f*.85f + .6f;
            eye[0]=(float)Math.cos(a)*58f;eye[1]=35f+(float)Math.sin(t*3.14f)*12f;eye[2]=(float)Math.sin(a)*58f;
            target[0]=0;target[1]=2;target[2]=0;
        }else{
            float p=Math.max(0,Math.min(.995f,racers[0].progress));float[] pos=sample(p),ahead=sample(Math.min(.999f,p+.025f));
            float dx=ahead[0]-pos[0],dy=ahead[1]-pos[1],dz=ahead[2]-pos[2];float len=(float)Math.sqrt(dx*dx+dy*dy+dz*dz)+.001f;dx/=len;dy/=len;dz/=len;
            float zoom=(p>.43f&&p<.58f)?18f:10.5f;
            eye[0]=pos[0]-dx*zoom;eye[1]=pos[1]+6.2f+(zoom-10.5f)*.35f;eye[2]=pos[2]-dz*zoom;
            target[0]=pos[0]+dx*5f;target[1]=pos[1]+1.2f;target[2]=pos[2]+dz*5f;
        }
        cameraPos[0]=eye[0];cameraPos[1]=eye[1];cameraPos[2]=eye[2];
        Matrix.setLookAtM(view,0,eye[0],eye[1],eye[2],target[0],target[1],target[2],0,1,0);Matrix.multiplyMM(vp,0,proj,0,view,0);
    }

    private void drawWorld(){
        float[] theme=THEMES[mapIndex];
        for(int i=0;i<POINTS-1;i+=2){float[] a=path[i],b=path[Math.min(POINTS-1,i+2)];drawBeam(a,b,2.8f,.28f,new float[]{.11f,.12f,.15f},.78f,.26f,.0f,1f);drawRail(a,b,theme,1);drawRail(a,b,theme,-1);}
        for(int i=0;i<POINTS;i+=10){float[] p=path[i];drawBox(p[0],p[1]-4.5f,p[2],.7f,8.5f,.7f,new float[]{.06f,.065f,.075f},i*.12f,.9f,.34f,0f,1f);}
        drawGate(.18f,theme,0);drawGate(.52f,new float[]{.15f,.55f,1f},1);drawGate(.68f,new float[]{1f,.75f,.12f},2);drawSpinner(.81f,theme);
        drawGate(.01f,new float[]{1f,1f,1f},3);drawGate(.985f,new float[]{.2f,1f,.35f},3);
        for(int i=0;i<MARBLES;i++){
            Racer r=racers[i];float p=Math.max(0,Math.min(.999f,r.progress));float[] pos=sampleOffset(p,r.lane);float pulse=i==0?1.15f:1f;float s=.64f*pulse;
            float[] core={Math.min(1f,r.color[0]*1.15f+.08f),Math.min(1f,r.color[1]*1.15f+.08f),Math.min(1f,r.color[2]*1.15f+.08f)};
            drawSphereMaterial(pos[0],pos[1]+.62f,pos[2],s*.72f,core,.22f,.20f,.33f,1f);
            drawSphereMaterial(pos[0],pos[1]+.62f,pos[2],s,new float[]{.72f+.22f*r.color[0],.76f+.18f*r.color[1],.82f+.14f*r.color[2]},.06f,.08f,.05f,.32f);
        }
    }

    private float[] sample(float p){float f=p*(POINTS-1);int i=Math.min(POINTS-2,Math.max(0,(int)f));float q=f-i;return new float[]{mix(path[i][0],path[i+1][0],q),mix(path[i][1],path[i+1][1],q),mix(path[i][2],path[i+1][2],q)};}
    private float[] sampleOffset(float p,float lane){float[] c=sample(p),n=sample(Math.min(.999f,p+.008f));float dx=n[0]-c[0],dz=n[2]-c[2],l=(float)Math.sqrt(dx*dx+dz*dz)+.001f;return new float[]{c[0]-dz/l*lane,c[1],c[2]+dx/l*lane};}
    private static float mix(float a,float b,float t){return a+(b-a)*t;}

    private void drawBeam(float[] a,float[] b,float width,float height,float[] color){drawBeam(a,b,width,height,color,.35f,.45f,0f,1f);}
    private void drawBeam(float[] a,float[] b,float width,float height,float[] color,float metallic,float roughness,float emissive,float alpha){
        float mx=(a[0]+b[0])*.5f,my=(a[1]+b[1])*.5f,mz=(a[2]+b[2])*.5f;float dx=b[0]-a[0],dy=b[1]-a[1],dz=b[2]-a[2];float len=(float)Math.sqrt(dx*dx+dy*dy+dz*dz);float yaw=(float)Math.toDegrees(Math.atan2(dx,dz));float pitch=-(float)Math.toDegrees(Math.atan2(dy,Math.sqrt(dx*dx+dz*dz)));
        Matrix.setIdentityM(model,0);Matrix.translateM(model,0,mx,my,mz);Matrix.rotateM(model,0,yaw,0,1,0);Matrix.rotateM(model,0,pitch,1,0,0);Matrix.scaleM(model,0,width,height,len*.5f);draw(cube,color,metallic,roughness,emissive,alpha);
    }
    private void drawRail(float[] a,float[] b,float[] color,int side){
        float dx=b[0]-a[0],dz=b[2]-a[2],l=(float)Math.sqrt(dx*dx+dz*dz)+.001f;float ox=-dz/l*3.1f*side,oz=dx/l*3.1f*side;float[] aa={a[0]+ox,a[1]+.7f,a[2]+oz},bb={b[0]+ox,b[1]+.7f,b[2]+oz};drawBeam(aa,bb,.16f,.16f,color,.55f,.18f,.72f,1f);
    }
    private void drawGate(float p,float[] color,int style){float[] c=sample(p),n=sample(Math.min(.999f,p+.01f));float yaw=(float)Math.toDegrees(Math.atan2(n[0]-c[0],n[2]-c[2]));drawBox(c[0],c[1]+2.8f,c[2],style==1?.28f:3.7f,style==1?4.8f:.22f,style==1?3.7f:.22f,color,yaw,.5f,.2f,.65f,1f);if(style!=1){drawBox(c[0],c[1]+1.6f,c[2],.22f,3.3f,3.6f,color,yaw,.5f,.2f,.55f,1f);}}
    private void drawSpinner(float p,float[] color){float[] c=sample(p);float angle=raceTime*110f;for(int i=0;i<4;i++){Matrix.setIdentityM(model,0);Matrix.translateM(model,0,c[0],c[1]+1.2f,c[2]);Matrix.rotateM(model,0,angle+i*90f,0,1,0);Matrix.translateM(model,0,2.7f,0,0);Matrix.scaleM(model,0,2.7f,.18f,.18f);draw(cube,color,.65f,.16f,.48f,1f);}}
    private void drawBox(float x,float y,float z,float sx,float sy,float sz,float[] color,float yaw){drawBox(x,y,z,sx,sy,sz,color,yaw,.35f,.45f,0f,1f);}
    private void drawBox(float x,float y,float z,float sx,float sy,float sz,float[] color,float yaw,float metallic,float roughness,float emissive,float alpha){Matrix.setIdentityM(model,0);Matrix.translateM(model,0,x,y,z);Matrix.rotateM(model,0,yaw,0,1,0);Matrix.scaleM(model,0,sx,sy,sz);draw(cube,color,metallic,roughness,emissive,alpha);}
    private void drawSphereMaterial(float x,float y,float z,float s,float[] color,float metallic,float roughness,float emissive,float alpha){Matrix.setIdentityM(model,0);Matrix.translateM(model,0,x,y,z);Matrix.rotateM(model,0,raceTime*145f,1,.35f,.2f);Matrix.scaleM(model,0,s,s,s);draw(sphere,color,metallic,roughness,emissive,alpha);}
    private void draw(Mesh mesh,float[] color,float metallic,float roughness,float emissive,float alpha){
        Matrix.multiplyMM(mvp,0,vp,0,model,0);GLES30.glUniformMatrix4fv(uMvp,1,false,mvp,0);GLES30.glUniformMatrix4fv(uModel,1,false,model,0);GLES30.glUniform3fv(uColor,1,color,0);
        GLES30.glUniform1f(uMetallic,metallic);GLES30.glUniform1f(uRoughness,roughness);GLES30.glUniform1f(uEmissive,emissive);GLES30.glUniform1f(uAlpha,alpha);
        if(alpha<.999f){GLES30.glEnable(GLES30.GL_BLEND);GLES30.glBlendFunc(GLES30.GL_SRC_ALPHA,GLES30.GL_ONE_MINUS_SRC_ALPHA);GLES30.glDepthMask(false);GLES30.glDisable(GLES30.GL_CULL_FACE);}
        mesh.draw();
        if(alpha<.999f){GLES30.glDepthMask(true);GLES30.glDisable(GLES30.GL_BLEND);GLES30.glEnable(GLES30.GL_CULL_FACE);}
    }

    private static int createProgram(String vs,String fs){int v=compile(GLES30.GL_VERTEX_SHADER,vs),f=compile(GLES30.GL_FRAGMENT_SHADER,fs),p=GLES30.glCreateProgram();GLES30.glAttachShader(p,v);GLES30.glAttachShader(p,f);GLES30.glLinkProgram(p);return p;}
    private static int compile(int type,String s){int sh=GLES30.glCreateShader(type);GLES30.glShaderSource(sh,s);GLES30.glCompileShader(sh);return sh;}
    private static float[] hsv(float h,float s,float v){float i=(float)Math.floor(h*6),f=h*6-i,p=v*(1-s),q=v*(1-f*s),t=v*(1-(1-f)*s);switch(((int)i)%6){case 0:return new float[]{v,t,p};case 1:return new float[]{q,v,p};case 2:return new float[]{p,v,t};case 3:return new float[]{p,q,v};case 4:return new float[]{t,p,v};default:return new float[]{v,p,q};}}

    static class Mesh {
        final FloatBuffer vb;final ShortBuffer ib;final int count;
        Mesh(float[] v,short[] idx){vb=ByteBuffer.allocateDirect(v.length*4).order(ByteOrder.nativeOrder()).asFloatBuffer();vb.put(v).position(0);ib=ByteBuffer.allocateDirect(idx.length*2).order(ByteOrder.nativeOrder()).asShortBuffer();ib.put(idx).position(0);count=idx.length;}
        void draw(){vb.position(0);GLES30.glEnableVertexAttribArray(0);GLES30.glVertexAttribPointer(0,3,GLES30.GL_FLOAT,false,24,vb);vb.position(3);GLES30.glEnableVertexAttribArray(1);GLES30.glVertexAttribPointer(1,3,GLES30.GL_FLOAT,false,24,vb);GLES30.glDrawElements(GLES30.GL_TRIANGLES,count,GLES30.GL_UNSIGNED_SHORT,ib);}
        static Mesh cube(){float[] v={-1,-1,-1,0,0,-1, 1,-1,-1,0,0,-1, 1,1,-1,0,0,-1,-1,1,-1,0,0,-1, -1,-1,1,0,0,1,1,-1,1,0,0,1,1,1,1,0,0,1,-1,1,1,0,0,1, -1,-1,-1,-1,0,0,-1,1,-1,-1,0,0,-1,1,1,-1,0,0,-1,-1,1,-1,0,0, 1,-1,-1,1,0,0,1,1,-1,1,0,0,1,1,1,1,0,0,1,1,1,-1,1,0,0, -1,-1,-1,0,-1,0,-1,-1,1,0,-1,0,1,-1,1,0,-1,0,1,-1,-1,0,-1,0, -1,1,-1,0,1,0,-1,1,1,0,1,0,1,1,1,0,1,0,1,1,-1,0,1,0};short[] idx=new short[36];int k=0;for(short f=0;f<6;f++){short o=(short)(f*4);idx[k++]=o;idx[k++]=(short)(o+1);idx[k++]=(short)(o+2);idx[k++]=o;idx[k++]=(short)(o+2);idx[k++]=(short)(o+3);}return new Mesh(v,idx);}
        static Mesh sphere(int seg,int rings){float[] v=new float[(rings+1)*(seg+1)*6];int k=0;for(int y=0;y<=rings;y++){float vv=y/(float)rings,ph=(float)(vv*Math.PI);for(int x=0;x<=seg;x++){float u=x/(float)seg,th=(float)(u*Math.PI*2);float sx=(float)(Math.sin(ph)*Math.cos(th)),sy=(float)Math.cos(ph),sz=(float)(Math.sin(ph)*Math.sin(th));v[k++]=sx;v[k++]=sy;v[k++]=sz;v[k++]=sx;v[k++]=sy;v[k++]=sz;}}short[] idx=new short[rings*seg*6];k=0;for(int y=0;y<rings;y++)for(int x=0;x<seg;x++){short a=(short)(y*(seg+1)+x),b=(short)(a+seg+1);idx[k++]=a;idx[k++]=b;idx[k++]=(short)(a+1);idx[k++]=(short)(a+1);idx[k++]=b;idx[k++]=(short)(b+1);}return new Mesh(v,idx);}
    }

    private static final String VS="#version 300 es\nlayout(location=0) in vec3 aPos;layout(location=1) in vec3 aNormal;uniform mat4 uMvp;uniform mat4 uModel;out vec3 vN;out vec3 vP;void main(){vec4 w=uModel*vec4(aPos,1.0);vP=w.xyz;vN=mat3(uModel)*aNormal;gl_Position=uMvp*vec4(aPos,1.0);}";
    private static final String FS="#version 300 es\nprecision mediump float;in vec3 vN;in vec3 vP;uniform vec3 uColor;uniform vec3 uLight;uniform vec3 uCamera;uniform float uMetallic;uniform float uRoughness;uniform float uAlpha;uniform float uEmissive;out vec4 frag;void main(){vec3 n=normalize(vN);vec3 l=normalize(uLight);vec3 v=normalize(uCamera-vP);vec3 h=normalize(l+v);float ndl=max(dot(n,l),0.0);float ndh=max(dot(n,h),0.0);float fres=pow(1.0-max(dot(n,v),0.0),5.0);float shin=mix(18.0,180.0,1.0-clamp(uRoughness,0.0,1.0));float spec=pow(ndh,shin);vec3 f0=mix(vec3(0.04),uColor,clamp(uMetallic,0.0,1.0));vec3 diffuse=uColor*(0.10+0.90*ndl)*(1.0-uMetallic*.72);vec3 reflection=f0*(spec*(1.15-uRoughness*.55)+fres*(0.42+0.58*uMetallic));vec3 sky=mix(vec3(0.04,0.05,0.08),vec3(0.38,0.46,0.62),clamp(n.y*.5+.5,0.0,1.0))*fres*.34;vec3 c=diffuse+reflection+sky+uColor*uEmissive;frag=vec4(c,uAlpha);}";
}
