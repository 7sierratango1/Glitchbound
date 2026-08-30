package com.brokengeargaming.torquematch;

import android.animation.*;
import android.content.*;
import android.graphics.*;
import android.media.*;
import android.os.*;
import android.view.*;
import android.view.animation.DecelerateInterpolator;
import java.util.*;

public class TorqueMatchView extends View {
    static final int R=8,C=8;
    static final long SW=330,CL=320,FA=460,PA=250;
    Paint p=new Paint(Paint.ANTI_ALIAS_FLAG), tx=new Paint(Paint.ANTI_ALIAS_FLAG);
    Random rnd=new Random(); SharedPreferences pref; Handler h=new Handler(Looper.getMainLooper());
    Tile[][] b=new Tile[R][C]; RectF start=new RectF(),next=new RectF(); RectF[] boostBtns={new RectF(),new RectF(),new RectF(),new RectF()};
    State state=State.MENU; int level,score,moves,target,startMoves,stars,reward,totalCredits;
    int bombCount,wrenchCount,nitroCount,movesCount; String awardText=""; Booster armed=Booster.NONE; boolean nitroVertical=false;
    float left,top,cell,w,hh,downX,downY; int dr=-1,dc=-1; boolean used,locked,swapAnim; int r1,c1,r2,c2; float sp,cp,fp=1;
    Set<Integer> clearing=new HashSet<>(); Map<Long,Float> fall=new HashMap<>(); int chain; String banner=""; long bannerUntil,celebrateAt; static long nid=1;

    enum State{MENU,PLAYING,COMPLETE_ANIM,COMPLETE,FAILED}
    enum Kind{WHEEL,ROTOR,TURBO,SPARK,GEAR,PISTON}
    enum Special{NONE,ROW,COL,BOMB,SUPER}
    enum Booster{NONE,BOMB,WRENCH,NITRO,MOVES}
    static class Tile{final long id=nid++;Kind k;Special s=Special.NONE;Tile(Kind x){k=x;}}
    static class Run{boolean horizontal;int fixed,start,end,len;Kind kind;Set<Integer> cells=new HashSet<>();}
    static class MI{Set<Integer> cells=new HashSet<>();List<Integer> lens=new ArrayList<>();List<Run> runs=new ArrayList<>();int spawn=-1;Special make=Special.NONE;Kind spawnKind;}

    public TorqueMatchView(Context x){
        super(x);setLayerType(View.LAYER_TYPE_SOFTWARE,null);pref=x.getSharedPreferences("torque_match",0);
        level=Math.max(1,pref.getInt("level",1));totalCredits=pref.getInt("credits",0);
        if(!pref.getBoolean("boosters_initialized",false)){bombCount=wrenchCount=nitroCount=movesCount=1;saveBoosters();pref.edit().putBoolean("boosters_initialized",true).apply();}else loadBoosters();
        tx.setTypeface(Typeface.create("sans",Typeface.BOLD));
    }
    void loadBoosters(){bombCount=pref.getInt("boost_bomb",0);wrenchCount=pref.getInt("boost_wrench",0);nitroCount=pref.getInt("boost_nitro",0);movesCount=pref.getInt("boost_moves",0);}
    void saveBoosters(){pref.edit().putInt("boost_bomb",bombCount).putInt("boost_wrench",wrenchCount).putInt("boost_nitro",nitroCount).putInt("boost_moves",movesCount).apply();}

    protected void onSizeChanged(int a,int z,int x,int y){w=a;hh=z;cell=Math.min((a-32f)/C,(z*.60f)/R);left=(a-cell*C)/2;top=z*.225f;}
    protected void onDraw(Canvas c){c.drawColor(Color.rgb(11,11,13));p.setColor(Color.rgb(31,31,36));for(int y=0;y<hh;y+=56)c.drawRect(0,y,w,y+2,p);if(state==State.MENU)menu(c);else game(c);if(state==State.COMPLETE_ANIM){celebrate(c);postInvalidateOnAnimation();}}
    void menu(Canvas c){center(c,"TORQUE MATCH",hh*.16f,w*.09f,Color.WHITE);center(c,"GARAGE MATCH-3",hh*.215f,w*.043f,0xffff7316);wheel(c,w/2,hh*.365f,Math.min(w,hh)*.14f);center(c,"Swipe parts. Build specials. Chain epic combos.",hh*.545f,w*.031f,Color.LTGRAY);float bw=w*.7f,bh=hh*.08f;start.set((w-bw)/2,hh*.635f,(w+bw)/2,hh*.635f+bh);button(c,start,"PLAY LEVEL "+level);center(c,"GARAGE CREDITS  "+totalCredits,hh*.755f,w*.037f,0xffffcc15);center(c,"BOOSTERS  BOMB "+bombCount+"   WRENCH "+wrenchCount+"   N2O "+nitroCount+"   +5 "+movesCount,hh*.805f,w*.027f,Color.LTGRAY);}
    void game(Canvas c){center(c,"LEVEL "+level,hh*.048f,w*.046f,Color.WHITE);center(c,"SCORE "+score+" / "+target,hh*.09f,w*.039f,0xffff7316);center(c,"MOVES  "+moves,hh*.13f,w*.040f,moves<=5?0xffef4444:Color.LTGRAY);if(!banner.isEmpty()&&System.currentTimeMillis()<bannerUntil){center(c,banner,hh*.177f,w*.037f,0xffffcc15);postInvalidateOnAnimation();}
        RectF tray=new RectF(left-8,top-8,left+cell*C+8,top+cell*R+8);p.setColor(0xff16161a);c.drawRoundRect(tray,22,22,p);
        for(int r=0;r<R;r++)for(int col=0;col<C;col++){Tile t=b[r][col];if(t==null)continue;float rr=r,cc=col;if(swapAnim){if(r==r1&&col==c1){rr=lerp(r1,r2,sp);cc=lerp(c1,c2,sp);}else if(r==r2&&col==c2){rr=lerp(r2,r1,sp);cc=lerp(c2,c1,sp);}}else if(fp<1&&fall.containsKey(t.id))rr=lerp(fall.get(t.id),r,fp);tile(c,rr,cc,t,clearing.contains(r*C+col)?1-cp:1);}
        if(state==State.PLAYING)drawBoosters(c);if(state==State.COMPLETE||state==State.FAILED)result(c);
    }
    void drawBoosters(Canvas c){float gap=8f,bw=(w-gap*5)/4f,y=hh*.865f,bh=hh*.085f;String[] labs={"BOMB\n"+bombCount,"WRENCH\n"+wrenchCount,(nitroVertical?"NITRO V\n":"NITRO H\n")+nitroCount,"+5 MOVES\n"+movesCount};Booster[] bs={Booster.BOMB,Booster.WRENCH,Booster.NITRO,Booster.MOVES};for(int i=0;i<4;i++){float x=gap+i*(bw+gap);boostBtns[i].set(x,y,x+bw,y+bh);boolean active=armed==bs[i];p.setColor(active?0xffff8a24:0xff303036);c.drawRoundRect(boostBtns[i],18,18,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(active?5:2);p.setColor(active?0xffffcc15:0xff62626b);c.drawRoundRect(boostBtns[i],18,18,p);p.setStyle(Paint.Style.FILL);String[] parts=labs[i].split("\n");centerAt(c,parts[0],boostBtns[i].centerX(),y+bh*.40f,w*.026f,Color.WHITE);centerAt(c,parts[1],boostBtns[i].centerX(),y+bh*.73f,w*.025f,active?0xfffff1a8:Color.LTGRAY);}if(armed!=Booster.NONE){String hint=armed==Booster.BOMB?"Tap a tile: clears 3x3":armed==Booster.WRENCH?"Tap a tile: precision remove":"Tap a tile: clears "+(nitroVertical?"column":"row");center(c,hint,hh*.845f,w*.028f,0xffffcc15);}}

    void tile(Canvas c,float r,float col,Tile t,float a){float x=left+col*cell,y=top+r*cell;p.setAlpha((int)(255*a));p.setColor(0xff27272d);c.drawRoundRect(new RectF(x+3,y+3,x+cell-3,y+cell-3),cell*.2f,cell*.2f,p);float cx=x+cell/2,cy=y+cell/2,s=cell*.29f;
        switch(t.k){case WHEEL:wheel(c,cx,cy,s);break;case ROTOR:p.setColor(0xffcbd5e1);c.drawCircle(cx,cy,s,p);p.setColor(0xffef4444);c.drawArc(new RectF(cx-s*.9f,cy-s*.9f,cx+s*.9f,cy+s*.9f),-30,70,true,p);break;case TURBO:p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(s*.24f);p.setColor(0xff38bdf8);c.drawCircle(cx,cy,s*.72f,p);p.setStyle(Paint.Style.FILL);break;case SPARK:p.setColor(Color.WHITE);c.drawRoundRect(new RectF(cx-s*.23f,cy-s*.8f,cx+s*.23f,cy+s*.35f),8,8,p);p.setColor(0xffffbf24);c.drawRect(cx-s*.09f,cy+s*.3f,cx+s*.09f,cy+s*.85f,p);break;case GEAR:p.setColor(0xffff7316);c.drawCircle(cx,cy,s*.74f,p);p.setColor(0xff27272a);c.drawCircle(cx,cy,s*.28f,p);break;case PISTON:p.setColor(0xffa3e635);c.drawRoundRect(new RectF(cx-s*.55f,cy-s*.65f,cx+s*.55f,cy-s*.05f),8,8,p);p.setStrokeWidth(s*.18f);c.drawLine(cx,cy,cx,cy+s*.7f,p);break;}
        if(t.s!=Special.NONE){p.setAlpha((int)(255*a));if(t.s==Special.SUPER){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(cell*.07f);p.setColor(0xffffcc15);c.drawCircle(cx,cy,s*1.18f,p);p.setColor(0xffff7316);c.drawCircle(cx,cy,s*.96f,p);p.setStyle(Paint.Style.FILL);for(int i=0;i<8;i++){double ang=i*Math.PI/4;float ax=cx+(float)Math.cos(ang)*s*1.25f,ay=cy+(float)Math.sin(ang)*s*1.25f;p.setColor(i%2==0?0xffffcc15:Color.WHITE);c.drawCircle(ax,ay,cell*.035f,p);}}
            else if(t.s==Special.BOMB){p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(cell*.065f);p.setColor(0xffff7316);c.drawCircle(cx,cy,s*1.1f,p);p.setStyle(Paint.Style.FILL);p.setColor(0xffffcc15);c.drawCircle(cx+s*.75f,cy-s*.8f,cell*.055f,p);}
            else{p.setColor(0xffffcc15);if(t.s==Special.ROW){c.drawRect(cx-s*1.15f,cy-cell*.045f,cx+s*1.15f,cy+cell*.045f,p);for(int i=-1;i<=1;i+=2){Path ar=new Path();ar.moveTo(cx+i*s*1.2f,cy);ar.lineTo(cx+i*s*.75f,cy-cell*.13f);ar.lineTo(cx+i*s*.75f,cy+cell*.13f);ar.close();c.drawPath(ar,p);}}else{c.drawRect(cx-cell*.045f,cy-s*1.15f,cx+cell*.045f,cy+s*1.15f,p);for(int i=-1;i<=1;i+=2){Path ar=new Path();ar.moveTo(cx,cy+i*s*1.2f);ar.lineTo(cx-cell*.13f,cy+i*s*.75f);ar.lineTo(cx+cell*.13f,cy+i*s*.75f);ar.close();c.drawPath(ar,p);}}}
        }p.setAlpha(255);
    }
    void wheel(Canvas c,float x,float y,float s){p.setColor(0xff121214);c.drawCircle(x,y,s,p);p.setColor(0xffa1a1aa);c.drawCircle(x,y,s*.72f,p);p.setColor(0xff28282c);c.drawCircle(x,y,s*.25f,p);}

    void celebrate(Canvas c){float t=Math.min(1,(System.currentTimeMillis()-celebrateAt)/1400f);for(int i=0;i<30;i++){double a=i*Math.PI*2/30;float rad=w*(.1f+.55f*t);p.setColor(i%2==0?0xffff7316:0xffffcc15);c.drawCircle(w/2+(float)Math.cos(a)*rad,hh*.45f+(float)Math.sin(a)*rad*.7f,8,p);}center(c,"LEVEL COMPLETE!",hh*.45f,w*.065f,Color.WHITE);}
    void result(Canvas c){p.setColor(0xeb08080a);c.drawRoundRect(new RectF(w*.05f,hh*.22f,w*.95f,hh*.79f),28,28,p);boolean win=state==State.COMPLETE;center(c,win?"GARAGE CLEARED!":"OUT OF MOVES",hh*.315f,w*.055f,win?0xffa3e635:0xffef4444);center(c,"FINAL SCORE  "+score,hh*.385f,w*.043f,Color.WHITE);if(win){String st=stars==3?"★ ★ ★":stars==2?"★ ★ ☆":"★ ☆ ☆";center(c,st,hh*.455f,w*.057f,0xffffcc15);center(c,"Moves left: "+moves+" / "+startMoves,hh*.505f,w*.032f,Color.LTGRAY);center(c,"+"+reward+" GARAGE CREDITS",hh*.555f,w*.035f,0xffffcc15);if(!awardText.isEmpty())center(c,awardText,hh*.602f,w*.030f,0xffa3e635);center(c,"BOOSTERS  BOMB "+bombCount+"  WRENCH "+wrenchCount+"  N2O "+nitroCount+"  +5 "+movesCount,hh*.645f,w*.025f,Color.LTGRAY);}float bw=w*.62f,bh=hh*.07f;next.set((w-bw)/2,hh*.69f,(w+bw)/2,hh*.69f+bh);button(c,next,win?"NEXT LEVEL":"TRY AGAIN");}
    int calcStars(){float remain=moves/(float)Math.max(1,startMoves);if(remain>=.50f)return 3;if(remain>=.25f)return 2;return 1;}int calcReward(){int base=100+level*15;return base+(stars-1)*75+moves*8;}

    void begin(){h.removeCallbacksAndMessages(null);state=State.PLAYING;score=0;moves=Math.max(16,24-(level-1)/3);startMoves=moves;target=2800+(level-1)*950;locked=false;armed=Booster.NONE;clearing.clear();fall.clear();fp=1;banner="";awardText="";fill();invalidate();}
    void fill(){for(int r=0;r<R;r++)for(int c=0;c<C;c++){Kind k;do{k=Kind.values()[rnd.nextInt(6)];}while((c>=2&&b[r][c-1].k==k&&b[r][c-2].k==k)||(r>=2&&b[r-1][c].k==k&&b[r-2][c].k==k));b[r][c]=new Tile(k);}}

    public boolean onTouchEvent(MotionEvent e){float x=e.getX(),y=e.getY();if(state==State.MENU){if(e.getAction()==MotionEvent.ACTION_UP&&start.contains(x,y))begin();return true;}if(state==State.COMPLETE||state==State.FAILED){if(e.getAction()==MotionEvent.ACTION_UP&&next.contains(x,y)){if(state==State.COMPLETE){level++;pref.edit().putInt("level",level).apply();}begin();}return true;}if(state!=State.PLAYING||locked)return true;
        if(e.getAction()==MotionEvent.ACTION_UP){for(int i=0;i<4;i++)if(boostBtns[i].contains(x,y)){handleBoosterButton(i);dr=dc=-1;return true;}if(armed!=Booster.NONE){int rr=(int)((y-top)/cell),cc=(int)((x-left)/cell);if(rr>=0&&rr<R&&cc>=0&&cc<C){useArmed(rr,cc);dr=dc=-1;return true;}}}
        if(e.getAction()==MotionEvent.ACTION_DOWN){downX=x;downY=y;used=false;dc=(int)((x-left)/cell);dr=(int)((y-top)/cell);if(dr<0||dr>=R||dc<0||dc>=C)dr=dc=-1;}
        else if(e.getAction()==MotionEvent.ACTION_MOVE&&dr>=0&&!used&&armed==Booster.NONE){float dx=x-downX,dy=y-downY;if(Math.abs(dx)>cell*.24||Math.abs(dy)>cell*.24){int nr=dr,nc=dc;if(Math.abs(dx)>Math.abs(dy))nc+=dx>0?1:-1;else nr+=dy>0?1:-1;if(nr>=0&&nr<R&&nc>=0&&nc<C){used=true;doSwap(dr,dc,nr,nc);}}}
        else if(e.getAction()==MotionEvent.ACTION_UP||e.getAction()==MotionEvent.ACTION_CANCEL)dr=dc=-1;return true;
    }
    void handleBoosterButton(int i){if(i==3){if(movesCount<=0){flash("NO +5 MOVES LEFT");return;}movesCount--;moves+=5;startMoves+=5;saveBoosters();sfx(8,1);flash("+5 MOVES!");invalidate();return;}Booster wanted=i==0?Booster.BOMB:i==1?Booster.WRENCH:Booster.NITRO;int count=i==0?bombCount:i==1?wrenchCount:nitroCount;if(count<=0){flash("NO "+(wanted==Booster.BOMB?"BOMBS":wanted==Booster.WRENCH?"WRENCHES":"NITRO")+" LEFT");return;}if(wanted==Booster.NITRO&&armed==Booster.NITRO){nitroVertical=!nitroVertical;flash(nitroVertical?"NITRO: COLUMN":"NITRO: ROW");}else{armed=(armed==wanted)?Booster.NONE:wanted;if(armed!=Booster.NONE)flash("SELECT A TILE");}invalidate();}
    void useArmed(int rr,int cc){Booster use=armed;armed=Booster.NONE;Set<Integer> cells=new HashSet<>();if(use==Booster.BOMB){for(int r=Math.max(0,rr-1);r<=Math.min(R-1,rr+1);r++)for(int c=Math.max(0,cc-1);c<=Math.min(C-1,cc+1);c++)cells.add(r*C+c);bombCount--;sfx(5,1);}else if(use==Booster.WRENCH){cells.add(rr*C+cc);wrenchCount--;sfx(6,1);}else if(use==Booster.NITRO){if(nitroVertical)for(int r=0;r<R;r++)cells.add(r*C+cc);else for(int c=0;c<C;c++)cells.add(rr*C+c);nitroCount--;sfx(7,1);}saveBoosters();directClear(cells,(use==Booster.BOMB?"ENGINE BOMB":use==Booster.WRENCH?"IMPACT WRENCH":"NITRO LINE"),cells.size()*80,false);}

    void doSwap(int a,int d,int z,int q){locked=true;swapAnim=true;r1=a;c1=d;r2=z;c2=q;sfx(0,1);anim(SW,v->{sp=v;invalidate();},()->{swapAnim=false;swap(a,d,z,q);Tile ta=b[a][d],tb=b[z][q];if(ta.s!=Special.NONE||tb.s!=Special.NONE){moves--;chain=1;specialSwap(a,d,z,q);return;}MI m=find(z*C+q,a*C+d);if(m.cells.isEmpty()){swapAnim=true;r1=z;c1=q;r2=a;c2=d;anim(SW,v->{sp=v;invalidate();},()->{swapAnim=false;swap(a,d,z,q);locked=false;invalidate();});}else{moves--;chain=1;resolve(m);}});}

    void specialSwap(int a,int d,int z,int q){int pa=a*C+d,pb=z*C+q;Tile A=b[a][d],B=b[z][q];Set<Integer> cells=new HashSet<>();String label="SPECIAL COMBO";int pts=900;
        if(A.s==Special.SUPER&&B.s==Special.SUPER){for(int i=0;i<R*C;i++)cells.add(i);label="SUPER + SUPER  BOARD WIPE!";pts=7000;sfx(4,1);}
        else if(A.s==Special.SUPER||B.s==Special.SUPER){Tile sup=A.s==Special.SUPER?A:B;Tile other=A.s==Special.SUPER?B:A;Special carry=other.s;for(int r=0;r<R;r++)for(int c=0;c<C;c++)if(b[r][c]!=null&&b[r][c].k==other.k){if(carry!=Special.NONE&&carry!=Special.SUPER)b[r][c].s=carry;cells.add(r*C+c);}cells.add(pa);cells.add(pb);label=carry==Special.NONE?"SUPER "+other.k+" CLEAR!":"SUPER SPECIAL STORM!";pts=2500;sfx(3,1);expandSpecials(cells,other.k);}
        else if(A.s!=Special.NONE&&B.s!=Special.NONE){cells.add(pa);cells.add(pb);if((A.s==Special.BOMB&&(B.s==Special.ROW||B.s==Special.COL))||(B.s==Special.BOMB&&(A.s==Special.ROW||A.s==Special.COL))){Tile line=A.s==Special.BOMB?B:A;int cr=A.s==Special.BOMB?a:z,cc=A.s==Special.BOMB?d:q;if(line.s==Special.ROW){for(int rr=Math.max(0,cr-1);rr<=Math.min(R-1,cr+1);rr++)for(int c=0;c<C;c++)cells.add(rr*C+c);}else{for(int c=Math.max(0,cc-1);c<=Math.min(C-1,cc+1);c++)for(int r=0;r<R;r++)cells.add(r*C+c);}label="BOMB + LINE BLAST!";pts=2200;}else if(A.s==Special.BOMB&&B.s==Special.BOMB){int cr=(a+z)/2,cc=(d+q)/2;for(int r=Math.max(0,cr-2);r<=Math.min(R-1,cr+2);r++)for(int c=Math.max(0,cc-2);c<=Math.min(C-1,cc+2);c++)cells.add(r*C+c);label="DOUBLE GARAGE BOMB!";pts=2600;}expandSpecials(cells,null);sfx(3,1);}
        else{int pos=A.s!=Special.NONE?pa:pb;cells.add(pos);expandSpecials(cells,null);label="SPECIAL ACTIVATED!";pts=1000;sfx(3,1);}
        directClear(cells,label,pts,true);
    }

    MI find(int preferred,int alternate){MI m=new MI();List<Run> hs=new ArrayList<>(),vs=new ArrayList<>();
        for(int r=0;r<R;r++){int c=0;while(c<C){if(b[r][c]==null){c++;continue;}Kind k=b[r][c].k;int e=c+1;while(e<C&&b[r][e]!=null&&b[r][e].k==k)e++;int len=e-c;if(len>=3){Run run=new Run();run.horizontal=true;run.fixed=r;run.start=c;run.end=e-1;run.len=len;run.kind=k;for(int x=c;x<e;x++){int pos=r*C+x;run.cells.add(pos);m.cells.add(pos);}m.lens.add(len);m.runs.add(run);hs.add(run);}c=e;}}
        for(int c=0;c<C;c++){int r=0;while(r<R){if(b[r][c]==null){r++;continue;}Kind k=b[r][c].k;int e=r+1;while(e<R&&b[e][c]!=null&&b[e][c].k==k)e++;int len=e-r;if(len>=3){Run run=new Run();run.horizontal=false;run.fixed=c;run.start=r;run.end=e-1;run.len=len;run.kind=k;for(int y=r;y<e;y++){int pos=y*C+c;run.cells.add(pos);m.cells.add(pos);}m.lens.add(len);m.runs.add(run);vs.add(run);}r=e;}}
        if(m.cells.isEmpty())return m;
        Set<Integer> intersections=new HashSet<>();for(Run hrun:hs)for(Run vrun:vs)for(int pos:hrun.cells)if(vrun.cells.contains(pos))intersections.add(pos);
        if(!intersections.isEmpty()){m.make=Special.BOMB;m.spawn=choose(intersections,preferred,alternate);}
        else{Run best=null;for(Run run:m.runs)if(run.len>=5&&(best==null||run.len>best.len))best=run;if(best!=null){m.make=Special.SUPER;m.spawn=choose(best.cells,preferred,alternate);}else{for(Run run:m.runs)if(run.len==4){best=run;break;}if(best!=null){m.make=best.horizontal?Special.ROW:Special.COL;m.spawn=choose(best.cells,preferred,alternate);}}}
        if(m.spawn>=0&&b[m.spawn/C][m.spawn%C]!=null)m.spawnKind=b[m.spawn/C][m.spawn%C].k;return m;
    }
    int choose(Set<Integer> set,int p1,int p2){if(set.contains(p1))return p1;if(set.contains(p2))return p2;int best=-1;for(int p:set){if(best<0)best=p;}return best;}

    void resolve(MI m){Set<Integer> ex=new HashSet<>(m.cells);Special made=m.make;int spawn=m.spawn;if(made!=Special.NONE&&spawn>=0){ex.remove(spawn);Tile st=b[spawn/C][spawn%C];if(st!=null)st.s=made;}
        expandSpecials(ex,null);int gain=points(m,chain)+Math.max(0,ex.size()-m.cells.size())*90;score+=gain;String madeText=made==Special.SUPER?"  SUPER "+(m.spawnKind==null?"PART":m.spawnKind.toString())+"!":made==Special.BOMB?"  GARAGE BOMB!":made==Special.ROW||made==Special.COL?"  LINE BLASTER!":"";banner=(chain>1?"WAVE x"+chain+"  ":"")+"+"+gain+madeText;bannerUntil=System.currentTimeMillis()+1100;
        if(made==Special.SUPER)sfx(3,1);else if(made!=Special.NONE)sfx(2,1);else sfx(chain>1?2:1,Math.min(1.5f,1f+(chain-1)*.08f));clearAnimate(ex,()->{MI n=find(-1,-1);if(!n.cells.isEmpty()){chain++;resolve(n);}else finish();});
    }
    int points(MI m,int ch){int base=0;for(int len:m.lens)base+=len==3?300:len==4?750:len==5?1600:1600+(len-5)*800;return Math.round(base*(1+Math.max(0,m.runs.size()-1)*.45f)*(1+Math.max(0,ch-1)*.65f));}

    void directClear(Set<Integer> cells,String label,int pts,boolean alreadyExpanded){Set<Integer> ex=new HashSet<>(cells);if(!alreadyExpanded)expandSpecials(ex,null);score+=pts+Math.max(0,ex.size()-cells.size())*90;flash(label+"  +"+(pts+Math.max(0,ex.size()-cells.size())*90));clearAnimate(ex,()->{MI n=find(-1,-1);if(!n.cells.isEmpty()){chain=1;resolve(n);}else finish();});}
    void clearAnimate(Set<Integer> ex,Runnable after){locked=true;clearing.clear();clearing.addAll(ex);cp=0;anim(CL,v->{cp=v;invalidate();},()->{for(int pos:ex)b[pos/C][pos%C]=null;clearing.clear();gravity();anim(FA,v->{fp=v;invalidate();},()->{fp=1;fall.clear();h.postDelayed(after,PA);});});}

    void expandSpecials(Set<Integer> cells,Kind superTarget){ArrayDeque<Integer> q=new ArrayDeque<>(cells);Set<Integer> seen=new HashSet<>();while(!q.isEmpty()){int pos=q.removeFirst();if(pos<0||pos>=R*C||seen.contains(pos))continue;seen.add(pos);Tile t=b[pos/C][pos%C];if(t==null||t.s==Special.NONE)continue;Set<Integer> add=new HashSet<>();int r=pos/C,c=pos%C;if(t.s==Special.ROW)for(int x=0;x<C;x++)add.add(r*C+x);else if(t.s==Special.COL)for(int y=0;y<R;y++)add.add(y*C+c);else if(t.s==Special.BOMB)for(int y=Math.max(0,r-1);y<=Math.min(R-1,r+1);y++)for(int x=Math.max(0,c-1);x<=Math.min(C-1,c+1);x++)add.add(y*C+x);else if(t.s==Special.SUPER){Kind k=superTarget!=null?superTarget:t.k;for(int y=0;y<R;y++)for(int x=0;x<C;x++)if(b[y][x]!=null&&b[y][x].k==k)add.add(y*C+x);}for(int a:add)if(cells.add(a))q.addLast(a);}}

    void finish(){locked=false;if(score>=target){stars=calcStars();reward=calcReward();totalCredits+=reward;awardBoosters();pref.edit().putInt("credits",totalCredits).apply();saveBoosters();sfx(9,1);state=State.COMPLETE_ANIM;celebrateAt=System.currentTimeMillis();invalidate();h.postDelayed(()->{state=State.COMPLETE;invalidate();},1400);}else if(moves<=0){state=State.FAILED;invalidate();}}
    void awardBoosters(){int awarded=stars==3?2:stars==2?1:0;if(level%5==0)awarded++;if(awarded==0){awardText="";return;}int[] got=new int[4];for(int i=0;i<awarded;i++){int k=rnd.nextInt(4);got[k]++;if(k==0)bombCount++;else if(k==1)wrenchCount++;else if(k==2)nitroCount++;else movesCount++;}StringBuilder s=new StringBuilder("BOOSTER REWARD  ");if(got[0]>0)s.append("BOMB x").append(got[0]).append(" ");if(got[1]>0)s.append("WRENCH x").append(got[1]).append(" ");if(got[2]>0)s.append("N2O x").append(got[2]).append(" ");if(got[3]>0)s.append("+5 x").append(got[3]);awardText=s.toString().trim();}

    void gravity(){fall.clear();for(int c=0;c<C;c++){int wr=R-1;for(int r=R-1;r>=0;r--)if(b[r][c]!=null){Tile t=b[r][c];if(wr!=r){b[wr][c]=t;b[r][c]=null;fall.put(t.id,(float)r);}wr--;}int si=0;while(wr>=0){Tile t=new Tile(Kind.values()[rnd.nextInt(6)]);b[wr][c]=t;fall.put(t.id,-1f-si++);wr--;}}fp=0;}

    void sfx(int type,float rate){new Thread(()->{try{int sr=22050,ms;double f1,f2,noise=0,vol;switch(type){case 0:ms=90;f1=240;f2=360;vol=.38;break;case 1:ms=170;f1=420;f2=720;vol=.42;break;case 2:ms=240;f1=600;f2=1050;vol=.46;break;case 3:ms=420;f1=520;f2=1500;vol=.52;break;case 4:ms=720;f1=1200;f2=90;vol=.65;noise=.22;break;case 5:ms=330;f1=170;f2=65;vol=.62;noise=.34;break;case 6:ms=120;f1=330;f2=230;vol=.40;break;case 7:ms=320;f1=500;f2=1250;vol=.48;break;case 8:ms=260;f1=760;f2=1200;vol=.42;break;default:ms=620;f1=520;f2=1320;vol=.55;break;}int n=sr*ms/1000;short[] pcm=new short[n];Random nr=new Random();for(int i=0;i<n;i++){double t=i/(double)sr,prog=i/(double)n,f=(f1+(f2-f1)*prog)*rate;double env=Math.sin(Math.PI*prog);double wave=Math.sin(2*Math.PI*f*t)+.28*Math.sin(2*Math.PI*f*1.51*t)+(nr.nextDouble()*2-1)*noise;pcm[i]=(short)(Math.max(-1,Math.min(1,wave))*env*vol*32767);}
            AudioTrack tr=new AudioTrack.Builder().setAudioAttributes(new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_GAME).setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build()).setAudioFormat(new AudioFormat.Builder().setEncoding(AudioFormat.ENCODING_PCM_16BIT).setSampleRate(sr).setChannelMask(AudioFormat.CHANNEL_OUT_MONO).build()).setTransferMode(AudioTrack.MODE_STATIC).setBufferSizeInBytes(pcm.length*2).build();tr.write(pcm,0,pcm.length);tr.play();Thread.sleep(ms+80);tr.release();}catch(Exception ignored){}}).start();}

    void flash(String s){banner=s;bannerUntil=System.currentTimeMillis()+1100;invalidate();}
    void swap(int a,int d,int z,int q){Tile t=b[a][d];b[a][d]=b[z][q];b[z][q]=t;}
    void anim(long dur,F f,Runnable end){ValueAnimator a=ValueAnimator.ofFloat(0,1);a.setDuration(dur);a.setInterpolator(new DecelerateInterpolator());a.addUpdateListener(v->f.u((Float)v.getAnimatedValue()));a.addListener(new AnimatorListenerAdapter(){public void onAnimationEnd(Animator x){end.run();}});a.start();}
    interface F{void u(float v);}float lerp(float a,float b,float t){return a+(b-a)*t;}
    void center(Canvas c,String s,float y,float size,int color){tx.setTextSize(Math.max(12,size));tx.setColor(color);tx.setTextAlign(Paint.Align.CENTER);c.drawText(s,w/2,y,tx);}void button(Canvas c,RectF r,String s){p.setColor(0xffea580c);c.drawRoundRect(r,25,25,p);centerAt(c,s,r.centerX(),r.centerY()+w*.015f,w*.044f,Color.WHITE);}void centerAt(Canvas c,String s,float x,float y,float size,int color){tx.setTextSize(size);tx.setColor(color);tx.setTextAlign(Paint.Align.CENTER);c.drawText(s,x,y,tx);}
}
