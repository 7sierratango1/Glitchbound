import wave,math,random,os,struct
SR=44100; OUT='app/src/main/res/raw';os.makedirs(OUT,exist_ok=True)
def save(n,d,fn):
 x=[]
 for i in range(int(d*SR)):
  t=i/SR;p=i/(d*SR);v=max(-1,min(1,fn(t,p)))*(math.sin(math.pi*p)**.55);x.append(int(v*26000))
 with wave.open(f'{OUT}/{n}.wav','w') as w:w.setparams((1,2,SR,len(x),'NONE',''));w.writeframes(struct.pack('<'+'h'*len(x),*x))
def nz():return random.uniform(-1,1)
def metal(f):return lambda t,p:(.55*math.sin(2*math.pi*f*t)+.3*math.sin(2*math.pi*f*2.71*t)+.18*nz())*math.exp(-5*p)
def rev(lo,hi):return lambda t,p:.48*math.sin(2*math.pi*(lo+(hi-lo)*p)*t)+.22*math.sin(2*math.pi*(lo+(hi-lo)*p)*2*t)+.12*nz()
def squeal(t,p):return .45*math.sin(2*math.pi*(1250+500*math.sin(t*8))*t)+.35*nz()
def wrench(t,p):return (.6*nz()+.35*math.sin(2*math.pi*145*t))*(1 if (t*18)%1<.35 else .15)
def heavy(t,p):return .75*nz()*math.exp(-7*p)+.5*math.sin(2*math.pi*(95-55*p)*t)
def victory(t,p):return .42*math.sin(2*math.pi*(180+620*p)*t)+.22*nz()*(1-p)+.18*math.sin(2*math.pi*(360+900*p)*t)
def failure(t,p):return .55*math.sin(2*math.pi*(220-150*p)*t)+.2*nz()*(1-p)
for i,f in enumerate((410,520,650,780),1):save(f'match_metal_{i}',.18,metal(f))
for i,(a,b) in enumerate(((55,170),(70,230),(85,290)),1):save(f'engine_rev_{i}',1.25,rev(a,b))
for i in range(1,4):save(f'tire_squeal_{i}',.85+i*.08,squeal)
for i in range(1,4):save(f'impact_wrench_{i}',.52+i*.05,wrench)
save('booster_bomb',.8,heavy);save('booster_nitro',.9,lambda t,p:.45*nz()+.4*math.sin(2*math.pi*(300+1500*p)*t));save('booster_wrench',.55,wrench)
save('victory_big',2.5,victory);save('failure_big',2.1,failure)
