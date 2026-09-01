from pathlib import Path
p=Path('mm080/app/src/main/java/com/technicallyunavailable/malfunctionmarbles/GameRenderer.java')
s=p.read_text()
# Reference-inspired course presentation: solid patterned deck, clear-ish upper guards, loops, obstacle arenas, and a terminal catch box.
s=s.replace('float[] deck={.10f+.28f*theme[0],.11f+.22f*theme[1],.14f+.18f*theme[2]};','float[] deck={.12f+.38f*theme[0],.12f+.30f*theme[1],.15f+.25f*theme[2]};')
s=s.replace('float[] deckHi={.18f+.42f*theme[0],.18f+.34f*theme[1],.20f+.26f*theme[2]};','float[] deckHi={.28f+.55f*theme[0],.24f+.48f*theme[1],.30f+.38f*theme[2]};')
s=s.replace('drawWall(a,b,theme,1);drawWall(a,b,theme,-1);','drawWall(a,b,theme,1);drawWall(a,b,theme,-1);if(((i/2)&1)==0)drawBeam(new float[]{a[0],a[1]+.50f,a[2]},new float[]{b[0],b[1]+.50f,b[2]},1.55f,.055f,new float[]{.035f,.035f,.045f},.18f,.08f,.38f,1f);')
s=s.replace('drawBeam(aa,bb,.12f,1.10f,glass,.28f,.16f,.10f,.86f);','drawBeam(aa,bb,.13f,1.16f,glass,.28f,.16f,.10f,.68f);')
# Add showcase geometry before racers are drawn.
needle='        drawFeatures(theme);\n        drawRacers(theme);'
insert='''        drawFeatures(theme);\n        drawArcadeShowpieces(theme);\n        drawRacers(theme);'''
assert needle in s
s=s.replace(needle,insert)
# Insert helpers before drawRail.
needle='    private void drawRail(float[] a,float[] b,float[] color,int side){'
helpers='''    private void drawArcadeShowpieces(float[] color){\n        // Two vertical loop structures inspired by the reference's roller-coaster sections.\n        drawLoopAt(.105f,5.3f,color);\n        drawLoopAt(.405f,6.2f,color);\n        // Wide obstacle arena with chunky bumpers/pillars.\n        float[] arena=sample(.735f);\n        for(int row=-2;row<=2;row++)for(int col=-2;col<=2;col++){if(((row+col)&1)==0){float x=arena[0]+col*1.25f,z=arena[2]+row*1.25f;drawBox(x,arena[1]+1.05f,z,.72f,1.85f,.72f,new float[]{.78f,.08f,.06f},0,.18f,.26f,.04f,1f);}}\n        // Final square catch basin: racers dump into this terminal box.\n        float[] e=sample(.985f);float[] red={.68f,.055f,.035f};\n        drawBox(e[0],e[1]-.38f,e[2],8.8f,.42f,8.8f,red,0,.20f,.32f,.04f,1f);\n        drawBox(e[0]-4.35f,e[1]+1.15f,e[2],.38f,2.8f,8.8f,red,0,.18f,.30f,.04f,.96f);\n        drawBox(e[0]+4.35f,e[1]+1.15f,e[2],.38f,2.8f,8.8f,red,0,.18f,.30f,.04f,.96f);\n        drawBox(e[0],e[1]+1.15f,e[2]+4.35f,8.8f,2.8f,.38f,red,0,.18f,.30f,.04f,.96f);\n        // Clear-ish top canopy so the marbles remain visible inside the finish catcher.\n        drawBox(e[0],e[1]+3.05f,e[2],8.9f,.16f,8.9f,new float[]{.72f,.86f,.95f},0,.05f,.08f,.02f,.32f);\n        // Bright finish portal/ring immediately before the catch box.\n        drawFinishRing(.965f,color);\n    }\n    private void drawLoopAt(float p,float radius,float[] color){float[] c=sample(p);for(int j=0;j<30;j++){float a=(float)(Math.PI*2*j/30.0);float x=c[0]+(float)Math.cos(a)*radius;float y=c[1]+radius+(float)Math.sin(a)*radius;drawSphereMaterial(x,y,c[2],.34f,color,.38f,.20f,.16f,.98f,0);float x2=c[0]+(float)Math.cos(a)*(radius+1.15f);float y2=c[1]+radius+(float)Math.sin(a)*(radius+1.15f);drawSphereMaterial(x2,y2,c[2],.22f,new float[]{.75f,.86f,.96f},.08f,.10f,.04f,.48f,0);}}\n    private void drawFinishRing(float p,float[] color){float[] c=sample(p);for(int j=0;j<24;j++){float a=(float)(Math.PI*2*j/24.0);drawSphereMaterial(c[0]+(float)Math.cos(a)*3.4f,c[1]+3.5f+(float)Math.sin(a)*3.4f,c[2],.30f,new float[]{.95f,.12f,.52f},.22f,.12f,.45f,.98f,.18f);}}\n    private void drawRail(float[] a,float[] b,float[] color,int side){'''
assert needle in s
s=s.replace(needle,helpers)
# Add a final directed dump into the catch basin while retaining hybrid physics.
needle='        if(in(p,.87f,.925f)&&rng.nextFloat()<dt*1.4f){r.laneVelocity+=(rng.nextFloat()-.5f)*1.25f;r.velocity*=.994f;}'
replace=needle+'\n        if(in(p,.94f,.985f)){r.velocity+=2.4f*dt;r.laneVelocity+=(-r.lane)*1.8f*dt;}\n        if(p>.985f)r.velocity=Math.max(r.velocity,2.2f);'
assert needle in s
s=s.replace(needle,replace)
s=s.replace('versionCode 7','versionCode 8').replace("versionName '0.7.0'","versionName '0.8.0'")
p.write_text(s)
b=Path('mm080/app/build.gradle');t=b.read_text().replace('versionCode 7','versionCode 8').replace("versionName '0.7.0'","versionName '0.8.0'");b.write_text(t)
