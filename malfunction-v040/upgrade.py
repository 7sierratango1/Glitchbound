from pathlib import Path
p=Path('mm040/app/src/main/java/com/technicallyunavailable/malfunctionmarbles/GameRenderer.java')
s=p.read_text()
s=s.replace('private static final int MARBLES=10, POINTS=150;','private static final int MARBLES=10, POINTS=520;')
old='''        float seed=mapIndex+1;float turns=1.0f+(mapIndex%5)*.34f;float length=112f+(mapIndex%4)*12f;
        for(int i=0;i<POINTS;i++){
            float t=i/(float)(POINTS-1);float a=t*turns*6.28318f;
            float x=(float)Math.sin(a)*14f+(float)Math.sin(t*18f+seed)*2.3f;
            float z=t*length+(float)Math.cos(a*.72f+seed)*7f;
            float y=38f-t*(62f+(mapIndex%5)*3.4f);
            y+=(float)Math.sin(t*12.566f+seed)*2.2f;
            if(mapIndex%5==1){x+=(float)Math.sin(t*31f)*4f;y+=(float)Math.sin(t*25f)*1.5f;}
            if(mapIndex%5==2){x+=(float)Math.sin(t*10f)*8f;z+=(float)Math.sin(t*6f)*5f;}
            if(mapIndex%5==3){if(t>.34f&&t<.51f)y-=6f*(float)Math.sin((t-.34f)/.17f*3.14159f);}
            if(mapIndex%5==4){x+=(float)Math.sin(t*24f)*5f;}
            path[i][0]=x;path[i][1]=y;path[i][2]=z;
        }'''
new='''        float seed=mapIndex+1;float turns=4.2f+(mapIndex%5)*.62f;float length=470f+(mapIndex%4)*55f;
        for(int i=0;i<POINTS;i++){
            float t=i/(float)(POINTS-1);float a=t*turns*6.28318f;
            float x=(float)Math.sin(a)*20f+(float)Math.sin(t*41f+seed)*4.8f;
            float z=t*length+(float)Math.cos(a*.63f+seed)*13f+(float)Math.sin(t*17f)*7f;
            float y=62f-t*(155f+(mapIndex%5)*8f);y+=(float)Math.sin(t*31.416f+seed)*3.4f;
            if(t>.16f&&t<.27f){float q=(t-.16f)/.11f,ang=q*12.566f;x+=(float)Math.sin(ang)*15f;z+=(float)Math.cos(ang)*15f;y+=(float)Math.sin(ang)*7f;}
            if(t>.43f&&t<.56f){float q=(t-.43f)/.13f,ang=q*18.849f;x+=(float)Math.cos(ang)*18f;z+=(float)Math.sin(ang)*18f;y+=(float)Math.sin(ang)*9f;}
            if(t>.72f&&t<.84f){float q=(t-.72f)/.12f,ang=q*12.566f;x+=(float)Math.sin(ang)*13f;z+=(float)Math.cos(ang)*13f;y+=(float)Math.sin(ang)*6f;}
            if(mapIndex%5==1){x+=(float)Math.sin(t*53f)*6f;y+=(float)Math.sin(t*37f)*2.2f;}
            if(mapIndex%5==2){x+=(float)Math.sin(t*19f)*11f;z+=(float)Math.sin(t*13f)*9f;}
            if(mapIndex%5==3){if(t>.31f&&t<.46f)y-=10f*(float)Math.sin((t-.31f)/.15f*3.14159f);}
            if(mapIndex%5==4){x+=(float)Math.sin(t*39f)*7f;}
            path[i][0]=x;path[i][1]=y;path[i][2]=z;
        }'''
assert old in s
s=s.replace(old,new)
repls={
'float accel=.040f+.105f*Math.max(0,downhill);':'float accel=.0018f+.0052f*Math.max(0,downhill);',
'r.velocity*=1f-.16f*dt;':'r.velocity*=1f-.055f*dt;',
'if(in(p,.445f,.475f))r.velocity+=.092f*dt;':'if(in(p,.445f,.475f))r.velocity+=.0045f*dt;',
'r.velocity+=.012f;':'r.velocity+=.0012f;',
'if(in(p,.805f,.835f)&&Math.abs(r.lane)<1.2f)r.velocity+=.12f*dt;':'if(in(p,.805f,.835f)&&Math.abs(r.lane)<1.2f)r.velocity+=.0055f*dt;',
'if(mapIndex%4==3&&in(p,.64f,.68f))r.velocity+=.035f*dt;':'if(mapIndex%4==3&&in(p,.64f,.68f))r.velocity+=.0020f*dt;',
'r.velocity=clamp(r.velocity,.012f,.19f);':'r.velocity=clamp(r.velocity,.0036f,.0105f);',
'+(rng.nextFloat()-.5f)*.004f':'+(rng.nextFloat()-.5f)*.00035f',
'a.progress+=.0012f;else b.progress+=.0012f;':'a.progress+=.00018f;else b.progress+=.00018f;',
'float spread=packSpread(p);float zoom=11.5f+Math.min(12f,spread*1.8f);if(in(p,.18f,.30f)||in(p,.56f,.66f))zoom+=4f;':'float spread=packSpread(p);float zoom=9.2f+Math.min(5f,spread*.65f);if(in(p,.18f,.30f)||in(p,.56f,.66f))zoom+=2.5f;'}
for a,b in repls.items(): assert a in s,(a);s=s.replace(a,b)
s=s.replace('''        drawBumperField(.86f,.93f,new float[]{1f,.32f,.08f});\n\n        // marbles: luminous core + glass shell''','''        drawBumperField(.86f,.93f,new float[]{1f,.32f,.08f});
        drawTunnel(.075f,.12f,new float[]{.13f,.14f,.18f});drawBoostStrip(.135f,.155f,new float[]{1f,.24f,.04f});
        drawBumperField(.315f,.34f,new float[]{1f,.55f,.08f});drawTunnel(.655f,.69f,new float[]{.12f,.13f,.17f});
        drawFunnel(.765f,.795f,theme);drawMovingBlockers(.835f,.855f,new float[]{1f,.18f,.03f});

        // marbles: luminous core + glass shell''')
needle='''            drawSphereMaterial(pos[0],y,pos[2],s,new float[]{.74f+.20f*r.color[0],.78f+.16f*r.color[1],.86f+.10f*r.color[2]},.04f,.06f,.04f,.31f,r.spin);\n        }'''
replacement='''            drawSphereMaterial(pos[0],y,pos[2],s,new float[]{.74f+.20f*r.color[0],.78f+.16f*r.color[1],.86f+.10f*r.color[2]},.04f,.06f,.04f,.31f,r.spin);
            if(i==0){drawSphereMaterial(pos[0],y,pos[2],s*1.18f,new float[]{1f,.20f,.015f},.05f,.12f,.92f,.22f,r.spin);float[] back=sampleOffset(Math.max(.001f,p-.0045f),r.lane);for(int f=0;f<5;f++){float q=f/4f;float fx=mix(pos[0],back[0],q),fy=mix(y,back[1]+.72f,q)+(float)Math.sin(totalTime*15f+f)*.18f,fz=mix(pos[2],back[2],q);float fs=.42f*(1f-q*.72f);drawSphereMaterial(fx,fy,fz,fs,new float[]{1f,.16f+.45f*(1f-q),.01f},.02f,.2f,1.15f,.62f-q*.35f,totalTime*180f);}}
        }'''
assert needle in s
p.write_text(s.replace(needle,replacement))
b=Path('mm040/app/build.gradle');t=b.read_text().replace('versionCode 3','versionCode 4').replace("versionName '0.2.0'","versionName '0.4.0'");b.write_text(t)
