from pathlib import Path
p=Path('mm070/app/src/main/java/com/technicallyunavailable/malfunctionmarbles/GameRenderer.java')
s=p.read_text()
s=s.replace('if(stateTime>=5.15f){state=RUNNING;stateNs=System.nanoTime();stateTime=0;}','if(stateTime>=5.15f){for(Racer r:racers)r.velocity=Math.max(r.velocity,1.35f);state=RUNNING;stateNs=System.nanoTime();stateTime=0;}')
s=s.replace('float rollingResistance=.055f*9.81f*(float)Math.sqrt(Math.max(0f,1f-sinTheta*sinTheta));','float rollingResistance=.010f*9.81f*(float)Math.sqrt(Math.max(0f,1f-sinTheta*sinTheta));')
s=s.replace('float aeroDrag=.0065f*r.velocity*r.velocity;','float aeroDrag=.0018f*r.velocity*r.velocity;')
s=s.replace('float accel=gravityAccel-(r.velocity>0?rollingResistance:0f)-aeroDrag;','float accel=gravityAccel-(r.velocity>0?rollingResistance:0f)-aeroDrag;\n            // Hybrid track guidance: physics sets speed, track only prevents numerical stalls.\n            if(r.velocity<1.25f){float guide=1.10f*(1f-r.velocity/1.25f);accel+=Math.max(0f,guide);}')
s=s.replace('r.velocity=Math.max(.35f,r.velocity+accel*dt);','r.velocity=Math.max(.55f,r.velocity+accel*dt);')
old="private float worldDistanceToProgress(float distance,float p){float idx=clamp(p,0,1)*(POINTS-1);int i=Math.min(POINTS-2,Math.max(0,(int)idx));float target=cumulativeLength[i]+Math.max(0,distance);if(target>=trackLength)return 1f-p;int lo=i,hi=POINTS-1;while(lo+1<hi){int m=(lo+hi)>>>1;if(cumulativeLength[m]<target)lo=m;else hi=m;}float seg=Math.max(.001f,cumulativeLength[hi]-cumulativeLength[lo]);float q=(target-cumulativeLength[lo])/seg;float newP=(lo+q)/(POINTS-1f);return Math.max(0,newP-p);}"
new="private float worldDistanceToProgress(float distance,float p){float idx=clamp(p,0,1)*(POINTS-1);int i=Math.min(POINTS-2,Math.max(0,(int)idx));float frac=idx-i;float seg0=cumulativeLength[i],seg1=cumulativeLength[i+1];float currentArc=seg0+(seg1-seg0)*frac;float target=currentArc+Math.max(0,distance);if(target>=trackLength)return 1f-p;int lo=i,hi=POINTS-1;while(lo+1<hi){int m=(lo+hi)>>>1;if(cumulativeLength[m]<target)lo=m;else hi=m;}float seg=Math.max(.001f,cumulativeLength[hi]-cumulativeLength[lo]);float q=(target-cumulativeLength[lo])/seg;float newP=(lo+q)/(POINTS-1f);return Math.max(0,newP-p);}"
assert old in s
s=s.replace(old,new)
s=s.replace('drawBeam(a,b,3.7f,.40f,deck,.58f,.28f,.03f,.94f);','drawBeam(a,b,3.7f,.44f,deck,.62f,.24f,.035f,1f);')
s=s.replace('drawBeam(new float[]{a[0],a[1]+.43f,a[2]},new float[]{b[0],b[1]+.43f,b[2]},.78f,.045f,deckHi,.42f,.18f,.32f,.96f);','drawBeam(new float[]{a[0],a[1]+.47f,a[2]},new float[]{b[0],b[1]+.47f,b[2]},.82f,.055f,deckHi,.46f,.16f,.36f,1f);')
s=s.replace('drawBeam(aa,bb,.10f,1.05f,glass,.22f,.18f,.08f,.58f);','drawBeam(aa,bb,.12f,1.10f,glass,.28f,.16f,.10f,.86f);')
s=s.replace(',.30f,.26f,.06f,.82f);for(int row=0;',',.34f,.24f,.07f,.95f);for(int row=0;')
s=s.replace(',.30f,.2f,.04f,.74f);drawBox(bottom[0]',',.34f,.18f,.05f,.96f);drawBox(bottom[0]')
s=s.replace(',.30f,.2f,.04f,.74f);}',',.34f,.18f,.05f,.96f);}')
s=s.replace('draw(cube,color,.44f,.20f,.10f,.84f);','draw(cube,color,.48f,.18f,.12f,.94f);')
s=s.replace('drawSphereMaterial(c[0]+(float)Math.cos(rad)*radius,c[1]+.9f-(j/15f)*1.1f,c[2]+(float)Math.sin(rad)*radius,.23f,color,.38f,.21f,.12f,.88f,0);','drawSphereMaterial(c[0]+(float)Math.cos(rad)*radius,c[1]+.9f-(j/15f)*1.1f,c[2]+(float)Math.sin(rad)*radius,.24f,color,.42f,.18f,.14f,.96f,0);')
s=s.replace('versionCode 6','versionCode 7').replace("versionName '0.6.0'","versionName '0.7.0'")
p.write_text(s)
b=Path('mm070/app/build.gradle');t=b.read_text().replace('versionCode 6','versionCode 7').replace("versionName '0.6.0'","versionName '0.7.0'");b.write_text(t)
