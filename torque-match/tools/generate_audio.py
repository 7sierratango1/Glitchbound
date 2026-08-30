import wave,math,random,os,struct
SR=44100;OUT='app/src/main/res/raw';os.makedirs(OUT,exist_ok=True)
def save(n,d,fn,v=.8):
 x=[];N=int(d*SR)
 for i in range(N):
  t=i/SR;p=i/max(1,N-1);a=(math.sin(math.pi*p)**.45);z=max(-1,min(1,fn(t,p)))*a*v;x.append(int(z*32767))
 with wave.open(f'{OUT}/{n}.wav','w') as w:w.setparams((1,2,SR,len(x),'NONE',''));w.writeframes(struct.pack('<'+'h'*len(x),*x))
def nz():return random.uniform(-1,1)
def wheel(v):return lambda t,p:.48*math.sin(2*math.pi*(650+v*90+430*math.sin(t*11))*t)+.38*nz()*(1-.45*p)
def rotor(v):return lambda t,p:(.45*math.sin(2*math.pi*(2100+v*250)*t)+.35*math.sin(2*math.pi*(3700-v*200)*t)+.25*nz())*math.exp(-2.8*p)
def turbo(v):return lambda t,p:.48*math.sin(2*math.pi*(700+v*180+2600*p)*t)+.18*math.sin(2*math.pi*(1400+4300*p)*t)+.20*nz()*(1-p)
def spark(v):return lambda t,p:(.7*nz() if (t*(55+v*8))%1<.09 else .06*nz())+.24*math.sin(2*math.pi*(3600+v*500)*t)*math.exp(-10*p)
def gear(v):return lambda t,p:(.58*math.sin(2*math.pi*(390+v*80)*t)+.31*math.sin(2*math.pi*(1120+v*130)*t)+.16*nz())*math.exp(-6*p)
def piston(v):return lambda t,p:(.62*math.sin(2*math.pi*(95+v*18)*t)+.27*math.sin(2*math.pi*(190+v*25)*t)+.18*nz())*math.exp(-4.5*p)
def rev(lo,hi):return lambda t,p:.5*math.sin(2*math.pi*(lo+(hi-lo)*p)*t)+.24*math.sin(2*math.pi*(lo+(hi-lo)*p)*2*t)+.12*nz()
def wrench(t,p):return (.64*nz()+.30*math.sin(2*math.pi*145*t))*(1 if (t*20)%1<.28 else .12)
def heavy(t,p):return .72*nz()*math.exp(-7*p)+.52*math.sin(2*math.pi*(92-45*p)*t)
def rise(t,p):return .40*math.sin(2*math.pi*(220+1250*p)*t)+.24*nz()*(1-p)
def fail(t,p):return .52*math.sin(2*math.pi*(210-135*p)*t)+.20*nz()*(1-p)
for i in range(1,4):
 save(f'wheel_{i}',.30+.03*i,wheel(i),.66);save(f'rotor_{i}',.22+.02*i,rotor(i),.62);save(f'turbo_{i}',.45+.03*i,turbo(i),.68);save(f'spark_{i}',.18+.02*i,spark(i),.58);save(f'gear_{i}',.20+.02*i,gear(i),.66);save(f'piston_{i}',.26+.02*i,piston(i),.70)
for i,(a,b) in enumerate(((55,170),(70,230),(85,290)),1):save(f'engine_rev_{i}',1.2,rev(a,b),.55)
save('swipe_part',.09,lambda t,p:.22*nz()+.18*math.sin(2*math.pi*(240+160*p)*t),.45);save('match_four',.28,wrench,.56);save('match_five',.55,rev(90,260),.56);save('cascade_small',.42,rise,.52);save('cascade_big',.72,lambda t,p:rise(t,p)+.20*nz(),.62);save('line_special',.35,lambda t,p:.38*nz()+.34*math.sin(2*math.pi*(300+1600*p)*t),.62);save('super_special',.72,lambda t,p:rise(t,p)+.22*math.sin(2*math.pi*(650+2300*p)*t),.68);save('super_combo',1.05,lambda t,p:rise(t,p)+.32*nz()*(1-p),.78);save('booster_bomb',.8,heavy,.78);save('booster_nitro',.9,lambda t,p:.42*nz()+.38*math.sin(2*math.pi*(300+1800*p)*t),.66);save('booster_wrench',.56,wrench,.74);save('extra_moves',.45,lambda t,p:.40*math.sin(2*math.pi*(520+700*p)*t)+.12*nz(),.58);save('victory_big',2.5,lambda t,p:.40*math.sin(2*math.pi*(180+620*p)*t)+.20*nz()*(1-p)+.18*math.sin(2*math.pi*(360+900*p)*t),.66);save('victory_three',3.0,lambda t,p:.42*math.sin(2*math.pi*(190+780*p)*t)+.24*math.sin(2*math.pi*(380+1200*p)*t)+.18*nz()*(1-p),.72);save('failure_big',2.2,fail,.70)
