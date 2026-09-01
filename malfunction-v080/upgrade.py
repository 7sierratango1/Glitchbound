from pathlib import Path
p=Path('mm080/app/src/main/java/com/technicallyunavailable/malfunctionmarbles/GameRenderer.java')
s=p.read_text()
s=s.replace('float[] deck={.10f+.28f*theme[0],.11f+.22f*theme[1],.14f+.18f*theme[2]};','float[] deck={.12f+.38f*theme[0],.12f+.30f*theme[1],.15f+.25f*theme[2]};')
s=s.replace('float[] deckHi={.18f+.42f*theme[0],.18f+.34f*theme[1],.20f+.26f*theme[2]};','float[] deckHi={.28f+.55f*theme[0],.24f+.48f*theme[1],.30f+.38f*theme[2]};')
s=s.replace('drawBeam(aa,bb,.12f,1.10f,glass,.28f,.16f,.10f,.86f);','drawBeam(aa,bb,.13f,1.16f,glass,.28f,.16f,.10f,.68f);')
# Put reference-inspired structures into the existing world pass.
needle='        drawStartFinish(theme);'
assert needle in s
s=s.replace(needle,needle+'\n        drawArcadeShowpieces(theme);',1)
# Add geometry helpers before drawStartFinish.
anchor='    private void drawStartFinish(float[] theme){'
assert anchor in s
helpers='''    private void drawArcadeShowpieces(float[] color){\n        drawLoopAt(.105f,5.3f,color);drawLoopAt(.405f,6.2f,color);\n        float[] arena=sample(.735f);for(int row=-2;row<=2;row++)for(int col=-2;col<=2;col++)if(((row+col)&1)==0)drawBox(arena[0]+col*1.25f,arena[1]+1.05f,arena[2]+row*1.25f,.72f,1.85f,.72f,new float[]{.78f,.08f,.06f},0,.18f,.26f,.04f,1f);\n        float[] e=sample(.985f);float[] red={.68f,.055f,.035f};drawBox(e[0],e[1]-.38f,e[2],8.8f,.42f,8.8f,red,0,.20f,.32f,.04f,1f);drawBox(e[0]-4.35f,e[1]+1.15f,e[2],.38f,2.8f,8.8f,red,0,.18f,.30f,.04f,.96f);drawBox(e[0]+4.35f,e[1]+1.15f,e[2],.38f,2.8f,8.8f,red,0,.18f,.30f,.04f,.96f);drawBox(e[0],e[1]+1.15f,e[2]+4.35f,8.8f,2.8f,.38f,red,0,.18f,.30f,.04f,.96f);drawBox(e[0],e[1]+3.05f,e[2],8.9f,.16f,8.9f,new float[]{.72f,.86f,.95f},0,.05f,.08f,.02f,.32f);drawFinishRing(.965f,color);\n    }\n    private void drawLoopAt(float p,float radius,float[] color){float[] c=sample(p);for(int j=0;j<30;j++){float a=(float)(Math.PI*2*j/30.0);drawSphereMaterial(c[0]+(float)Math.cos(a)*radius,c[1]+radius+(float)Math.sin(a)*radius,c[2],.34f,color,.38f,.20f,.16f,.98f,0);drawSphereMaterial(c[0]+(float)Math.cos(a)*(radius+1.15f),c[1]+radius+(float)Math.sin(a)*(radius+1.15f),c[2],.22f,new float[]{.75f,.86f,.96f},.08f,.10f,.04f,.48f,0);}}\n    private void drawFinishRing(float p,float[] color){float[] c=sample(p);for(int j=0;j<24;j++){float a=(float)(Math.PI*2*j/24.0);drawSphereMaterial(c[0]+(float)Math.cos(a)*3.4f,c[1]+3.5f+(float)Math.sin(a)*3.4f,c[2],.30f,new float[]{.95f,.12f,.52f},.22f,.12f,.45f,.98f,.18f);}}\n'''
s=s.replace(anchor,helpers+anchor,1)
# Strong final approach into the catch basin while keeping hybrid physics.
needle='        if(in(p,.87f,.925f)&&rng.nextFloat()<dt*1.4f){r.laneVelocity+=(rng.nextFloat()-.5f)*1.25f;r.velocity*=.994f;}'
assert needle in s
s=s.replace(needle,needle+'\n        if(in(p,.94f,.985f)){r.velocity+=2.4f*dt;r.laneVelocity+=(-r.lane)*1.8f*dt;}\n        if(p>.985f)r.velocity=Math.max(r.velocity,2.2f);',1)
p.write_text(s)
b=Path('mm080/app/build.gradle');t=b.read_text().replace('versionCode 7','versionCode 8').replace("versionName '0.7.0'","versionName '0.8.0'");b.write_text(t)
