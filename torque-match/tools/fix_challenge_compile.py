from pathlib import Path
p=Path('app/src/main/java/com/brokengeargaming/torquematch/TorqueMatchView.java')
s=p.read_text()
s=s.replace('double a=Math.PI/3*i-Math.PI/6;float px=cx+(float)Math.cos(a)*s*.8f,py=cy+(float)Math.sin(a)*s*.8f;', 'double ang=Math.PI/3*i-Math.PI/6;float px=cx+(float)Math.cos(ang)*s*.8f,py=cy+(float)Math.sin(ang)*s*.8f;')
p.write_text(s)
print('challenge compile fix applied')
