from pathlib import Path
p=Path('app/src/main/java/com/brokengeargaming/torquematch/TorqueMatchView.java')
s=p.read_text()
s=s.replace('Random rnd=new Random(); SharedPreferences pref; Handler h=new Handler(Looper.getMainLooper());','Random rnd=new Random(); SharedPreferences pref; Handler h=new Handler(Looper.getMainLooper()); RealSoundManager snd;')
s=s.replace('tx.setTypeface(Typeface.create("sans",Typeface.BOLD));','tx.setTypeface(Typeface.create("sans",Typeface.BOLD));snd=new RealSoundManager(x);')
s=s.replace('void begin(){h.removeCallbacksAndMessages(null);state=State.PLAYING;score=0;moves=Math.max(16,24-(level-1)/3);startMoves=moves;target=2800+(level-1)*950;locked=false;armed=Booster.NONE;clearing.clear();fall.clear();fp=1;banner="";awardText="";fill();invalidate();}','void begin(){h.removeCallbacksAndMessages(null);state=State.PLAYING;score=0;moves=Math.max(16,24-(level-1)/3);startMoves=moves;target=2800+(level-1)*950;locked=false;armed=Booster.NONE;clearing.clear();fall.clear();fp=1;banner="";awardText="";fill();snd.levelStart(level);invalidate();}')
s=s.replace('movesCount--;moves+=5;startMoves+=5;saveBoosters();sfx(8,1);flash("+5 MOVES!");','movesCount--;moves+=5;startMoves+=5;saveBoosters();snd.extraMoves();flash("+5 MOVES!");')
s=s.replace('bombCount--;sfx(5,1);','bombCount--;snd.bomb();').replace('wrenchCount--;sfx(6,1);','wrenchCount--;snd.wrench();').replace('nitroCount--;sfx(7,1);','nitroCount--;snd.nitro();')
s=s.replace('doSwap(int a,int d,int z,int q){locked=true;swapAnim=true;r1=a;c1=d;r2=z;c2=q;sfx(0,1);','doSwap(int a,int d,int z,int q){locked=true;swapAnim=true;r1=a;c1=d;r2=z;c2=q;snd.swipe();')
old='if(made==Special.SUPER)sfx(3,1);else if(made!=Special.NONE)sfx(2,1);else sfx(chain>1?2:1,Math.min(1.5f,1f+(chain-1)*.08f));clearAnimate(ex,()->{MI n=find(-1,-1);if(!n.cells.isEmpty()){chain++;resolve(n);}else finish();});'
new='Kind soundKind=!m.runs.isEmpty()?m.runs.get(0).kind:(m.spawnKind!=null?m.spawnKind:Kind.GEAR);int longest=3;for(int len:m.lens)if(len>longest)longest=len;snd.partMatch(soundKind,level,chain,longest,made);clearAnimate(ex,()->{MI n=find(-1,-1);if(!n.cells.isEmpty()){chain++;resolve(n);}else finish();});'
s=s.replace(old,new)
s=s.replace('sfx(4,1);','snd.superCombo();').replace('sfx(3,1);','snd.special();')
s=s.replace('saveBoosters();sfx(9,1);state=State.COMPLETE_ANIM;','saveBoosters();snd.victory(stars);state=State.COMPLETE_ANIM;')
s=s.replace('}else if(moves<=0){state=State.FAILED;invalidate();}}','}else if(moves<=0){snd.failure();state=State.FAILED;invalidate();}}')
start=s.find('    void sfx(int type,float rate){')
if start!=-1:
    end=s.find('\n\n    void flash(',start)
    if end!=-1:s=s[:start]+s[end+2:]
if 'snd.partMatch(soundKind' not in s: raise SystemExit('part-specific match audio hook failed')
p.write_text(s)
