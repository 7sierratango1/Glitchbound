package com.brokengeargaming.torquematch;

import android.animation.ValueAnimator;
import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.*;
import android.os.Handler;
import android.os.Looper;
import android.view.MotionEvent;
import android.view.View;
import android.view.animation.DecelerateInterpolator;

import java.util.*;

public class TorqueMatchView extends View {
    private static final int ROWS = 8, COLS = 8;
    private static final long SWAP_MS = 330;
    private static final long CLEAR_MS = 300;
    private static final long FALL_MS = 440;
    private static final long CASCADE_PAUSE_MS = 240;

    private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint text = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Random rng = new Random();
    private final SharedPreferences prefs;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final Tile[][] board = new Tile[ROWS][COLS];
    private final RectF startButton = new RectF();
    private final RectF nextButton = new RectF();

    private State state = State.MENU;
    private int level = 1, score = 0, moves = 22, target = 3000;
    private float boardLeft, boardTop, cell, width, height;

    private float downX, downY;
    private int dragR = -1, dragC = -1;
    private boolean swipeConsumed = false;
    private boolean inputLocked = false;

    private boolean swapAnimating = false;
    private int swapR1, swapC1, swapR2, swapC2;
    private float swapProgress = 0f;

    private final Set<Integer> clearing = new HashSet<>();
    private float clearProgress = 0f;
    private final Map<Long, Float> fallStartRows = new HashMap<>();
    private float fallProgress = 1f;

    private int cascadeDepth = 0;
    private String comboBanner = "";
    private long comboBannerUntil = 0;
    private long completeAnimStart = 0;
    private int levelStartMoves = 0;
    private static long nextTileId = 1;

    enum State { MENU, PLAYING, COMPLETE_ANIM, COMPLETE, FAILED }
    enum Kind { WHEEL, ROTOR, TURBO, SPARK, GEAR, PISTON }
    enum Special { NONE, ROW, COL, HYPER }

    static class Tile {
        final long id = nextTileId++;
        Kind kind;
        Special special = Special.NONE;
        Tile(Kind k) { kind = k; }
    }

    static class MatchInfo {
        final Set<Integer> cells = new HashSet<>();
        final List<Integer> runLengths = new ArrayList<>();
        int runCount = 0;
    }

    public TorqueMatchView(Context context) {
        super(context);
        setLayerType(View.LAYER_TYPE_SOFTWARE, null);
        prefs = context.getSharedPreferences("torque_match", Context.MODE_PRIVATE);
        level = Math.max(1, prefs.getInt("level", 1));
        text.setTypeface(Typeface.create("sans", Typeface.BOLD));
    }

    @Override protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        width = w; height = h;
        cell = Math.min((w - 32f) / COLS, (h * 0.62f) / ROWS);
        boardLeft = (w - cell * COLS) / 2f;
        boardTop = h * 0.24f;
    }

    @Override protected void onDraw(Canvas c) {
        super.onDraw(c);
        drawBackground(c);
        if (state == State.MENU) drawMenu(c); else drawGame(c);
        if (state == State.COMPLETE_ANIM) {
            drawCelebration(c);
            if (System.currentTimeMillis() - completeAnimStart < 1250) postInvalidateOnAnimation();
        }
    }

    private void drawBackground(Canvas c) {
        c.drawColor(Color.rgb(11, 11, 13));
        p.setColor(Color.rgb(31, 31, 36));
        for (int y = 0; y < height; y += 56) c.drawRect(0, y, width, y + 2, p);
        p.setColor(Color.rgb(60, 30, 15));
        c.drawRect(0, 0, width, 8, p);
    }

    private void drawMenu(Canvas c) {
        drawCentered(c, "TORQUE MATCH", height * .19f, width * .09f, Color.WHITE);
        drawCentered(c, "GARAGE MATCH-3", height * .245f, width * .043f, Color.rgb(249,115,22));
        drawWheelLogo(c, width/2f, height*.39f, Math.min(width,height)*.15f);
        drawCentered(c, "Swipe parts. Build combos. Own the garage.", height*.58f, width*.038f, Color.LTGRAY);
        float bw = width*.70f, bh = height*.085f;
        startButton.set((width-bw)/2, height*.68f, (width+bw)/2, height*.68f+bh);
        drawButton(c, startButton, "PLAY LEVEL " + level);
        drawCentered(c, "Offline • No energy timer • No forced ads", height*.82f, width*.032f, Color.GRAY);
    }

    private void drawGame(Canvas c) {
        drawCentered(c, "LEVEL " + level, height*.055f, width*.048f, Color.WHITE);
        drawCentered(c, "SCORE " + score + " / " + target, height*.102f, width*.041f, Color.rgb(249,115,22));
        drawCentered(c, "MOVES  " + moves, height*.145f, width*.042f, moves <= 5 ? Color.rgb(239,68,68) : Color.LTGRAY);

        if (!comboBanner.isEmpty() && System.currentTimeMillis() < comboBannerUntil) {
            drawCentered(c, comboBanner, height*.195f, width*.042f, Color.rgb(250,204,21));
            postInvalidateOnAnimation();
        }

        RectF tray = new RectF(boardLeft-8, boardTop-8, boardLeft+cell*COLS+8, boardTop+cell*ROWS+8);
        p.setColor(Color.rgb(22,22,26)); c.drawRoundRect(tray, 22,22,p);
        p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(3); p.setColor(Color.rgb(82,82,91)); c.drawRoundRect(tray,22,22,p); p.setStyle(Paint.Style.FILL);

        for (int r=0;r<ROWS;r++) for (int col=0;col<COLS;col++) {
            Tile t = board[r][col];
            if (t == null) continue;
            float drawR = r;
            float drawC = col;

            if (swapAnimating) {
                if (r == swapR1 && col == swapC1) {
                    drawR = lerp(swapR1, swapR2, swapProgress);
                    drawC = lerp(swapC1, swapC2, swapProgress);
                } else if (r == swapR2 && col == swapC2) {
                    drawR = lerp(swapR2, swapR1, swapProgress);
                    drawC = lerp(swapC2, swapC1, swapProgress);
                }
            } else if (fallProgress < 1f && fallStartRows.containsKey(t.id)) {
                drawR = lerp(fallStartRows.get(t.id), r, fallProgress);
            }

            float alpha = clearing.contains(r*COLS+col) ? 1f-clearProgress : 1f;
            drawTileAt(c, drawR, drawC, t, alpha);
        }

        if (state == State.COMPLETE || state == State.FAILED) drawResultOverlay(c);
    }

    private void drawTileAt(Canvas c, float row, float col, Tile t, float alpha) {
        float x = boardLeft + col*cell, y = boardTop + row*cell;
        RectF box = new RectF(x+3,y+3,x+cell-3,y+cell-3);
        int a = Math.max(0, Math.min(255, (int)(255*alpha)));
        p.setAlpha(a);
        p.setColor(Color.rgb(39,39,45));
        c.drawRoundRect(box, cell*.20f, cell*.20f, p);
        float cx=x+cell/2, cy=y+cell/2, s=cell*.29f;
        switch(t.kind) {
            case WHEEL: drawWheel(c,cx,cy,s); break;
            case ROTOR: drawRotor(c,cx,cy,s); break;
            case TURBO: drawTurbo(c,cx,cy,s); break;
            case SPARK: drawSpark(c,cx,cy,s); break;
            case GEAR: drawGear(c,cx,cy,s); break;
            case PISTON: drawPiston(c,cx,cy,s); break;
        }
        if (t.special != Special.NONE) {
            p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(4); p.setColor(Color.rgb(251,191,36));
            c.drawRoundRect(box, cell*.20f,cell*.20f,p); p.setStyle(Paint.Style.FILL);
            String mark = t.special==Special.ROW ? "↔" : t.special==Special.COL ? "↕" : "★";
            drawText(c,mark,x+cell*.73f,y+cell*.28f,cell*.23f,Color.WHITE,Paint.Align.CENTER);
        }
        p.setAlpha(255);
    }

    private void drawWheel(Canvas c,float x,float y,float s){ p.setColor(Color.rgb(18,18,20)); c.drawCircle(x,y,s,p); p.setColor(Color.rgb(161,161,170)); c.drawCircle(x,y,s*.72f,p); p.setColor(Color.rgb(40,40,44)); c.drawCircle(x,y,s*.25f,p); p.setStrokeWidth(s*.12f); p.setColor(Color.rgb(63,63,70)); for(int i=0;i<5;i++){ double a=i*Math.PI*2/5; c.drawLine(x+(float)Math.cos(a)*s*.25f,y+(float)Math.sin(a)*s*.25f,x+(float)Math.cos(a)*s*.65f,y+(float)Math.sin(a)*s*.65f,p); } }
    private void drawRotor(Canvas c,float x,float y,float s){ p.setColor(Color.rgb(203,213,225)); c.drawCircle(x,y,s,p); p.setColor(Color.rgb(239,68,68)); c.drawArc(new RectF(x-s*.9f,y-s*.9f,x+s*.9f,y+s*.9f),-30,70,true,p); p.setColor(Color.rgb(71,85,105)); c.drawCircle(x,y,s*.28f,p); }
    private void drawTurbo(Canvas c,float x,float y,float s){ p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(s*.24f); p.setColor(Color.rgb(56,189,248)); c.drawCircle(x,y,s*.72f,p); c.drawArc(new RectF(x-s,y-s,x+s,y+s),210,230,false,p); p.setStyle(Paint.Style.FILL); p.setColor(Color.rgb(14,116,144)); c.drawCircle(x,y,s*.22f,p); }
    private void drawSpark(Canvas c,float x,float y,float s){ p.setColor(Color.rgb(250,250,250)); c.drawRoundRect(new RectF(x-s*.23f,y-s*.8f,x+s*.23f,y+s*.35f),s*.12f,s*.12f,p); p.setColor(Color.rgb(59,130,246)); for(int i=0;i<3;i++) c.drawRect(x-s*.30f,y-s*.45f+i*s*.25f,x+s*.30f,y-s*.35f+i*s*.25f,p); p.setColor(Color.rgb(251,191,36)); c.drawRect(x-s*.09f,y+s*.30f,x+s*.09f,y+s*.85f,p); }
    private void drawGear(Canvas c,float x,float y,float s){ p.setColor(Color.rgb(249,115,22)); c.drawCircle(x,y,s*.74f,p); for(int i=0;i<8;i++){ double a=i*Math.PI/4; float tx=x+(float)Math.cos(a)*s*.82f, ty=y+(float)Math.sin(a)*s*.82f; c.save(); c.rotate(i*45,tx,ty); c.drawRect(tx-s*.16f,ty-s*.22f,tx+s*.16f,ty+s*.22f,p); c.restore(); } p.setColor(Color.rgb(39,39,42)); c.drawCircle(x,y,s*.28f,p); }
    private void drawPiston(Canvas c,float x,float y,float s){ p.setColor(Color.rgb(163,230,53)); c.drawRoundRect(new RectF(x-s*.55f,y-s*.65f,x+s*.55f,y-s*.05f),s*.12f,s*.12f,p); p.setStrokeWidth(s*.18f); c.drawLine(x,y,x,y+s*.62f,p); c.drawLine(x,y+s*.60f,x+s*.40f,y+s*.85f,p); }
    private void drawWheelLogo(Canvas c,float x,float y,float s){ drawWheel(c,x,y,s); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(7); p.setColor(Color.rgb(249,115,22)); c.drawCircle(x,y,s*1.18f,p); p.setStyle(Paint.Style.FILL); }

    private void drawCelebration(Canvas c) {
        long elapsed = System.currentTimeMillis() - completeAnimStart;
        float t = Math.min(1f, elapsed / 1250f);
        p.setColor(Color.argb((int)(170*(1f-t)), 249,115,22));
        c.drawCircle(width/2f, height*.48f, width*(.08f+.45f*t), p);
        for (int i=0;i<28;i++) {
            double a = i*2*Math.PI/28.0;
            float radius = width*(.12f+.62f*t);
            float x = width/2f + (float)Math.cos(a)*radius;
            float y = height*.46f + (float)Math.sin(a)*radius*.75f + t*t*height*.12f;
            int color = (i%3==0)?Color.rgb(249,115,22):(i%3==1?Color.rgb(250,204,21):Color.WHITE);
            p.setColor(color); p.setAlpha((int)(255*(1f-t*.65f)));
            c.drawCircle(x,y,7+(i%4)*2,p);
        }
        p.setAlpha(255);
        float pop = t < .35f ? t/.35f : 1f;
        drawCentered(c, "LEVEL COMPLETE!", height*.46f, width*(.045f+.025f*pop), Color.WHITE);
    }

    private void drawResultOverlay(Canvas c) {
        p.setColor(Color.argb(235,8,8,10)); c.drawRoundRect(new RectF(width*.07f,height*.28f,width*.93f,height*.73f),28,28,p);
        boolean win = state==State.COMPLETE;
        drawCentered(c, win?"GARAGE CLEARED!":"OUT OF MOVES", height*.385f,width*.060f, win?Color.rgb(163,230,53):Color.rgb(239,68,68));
        drawCentered(c,"FINAL SCORE",height*.445f,width*.034f,Color.LTGRAY);
        drawCentered(c,String.valueOf(score),height*.505f,width*.070f,Color.WHITE);
        if (win) {
            int stars = score >= target*2 ? 3 : score >= (int)(target*1.35f) ? 2 : 1;
            String starText = stars==3 ? "★ ★ ★" : stars==2 ? "★ ★ ☆" : "★ ☆ ☆";
            drawCentered(c,starText,height*.555f,width*.050f,Color.rgb(250,204,21));
        }
        float bw=width*.62f,bh=height*.075f;
        nextButton.set((width-bw)/2,height*.60f,(width+bw)/2,height*.60f+bh);
        drawButton(c,nextButton,win?"NEXT LEVEL":"TRY AGAIN");
    }

    private void drawButton(Canvas c, RectF r, String label) { p.setColor(Color.rgb(234,88,12)); c.drawRoundRect(r,25,25,p); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(3); p.setColor(Color.rgb(251,146,60)); c.drawRoundRect(r,25,25,p); p.setStyle(Paint.Style.FILL); drawText(c,label,r.centerX(),r.centerY()+textSize(width*.044f)*.34f,width*.044f,Color.WHITE,Paint.Align.CENTER); }
    private void drawCentered(Canvas c,String s,float y,float size,int color){ drawText(c,s,width/2f,y,size,color,Paint.Align.CENTER); }
    private void drawText(Canvas c,String s,float x,float y,float size,int color,Paint.Align align){ text.setTextSize(textSize(size)); text.setColor(color); text.setTextAlign(align); c.drawText(s,x,y,text); }
    private float textSize(float px){ return Math.max(12,px); }
    private float lerp(float a,float b,float t){ return a+(b-a)*t; }

    private void beginLevel() {
        handler.removeCallbacksAndMessages(null);
        state=State.PLAYING; score=0; moves=Math.max(16,24-(level-1)/3); levelStartMoves=moves;
        target=2800+(level-1)*950;
        dragR=dragC=-1; inputLocked=false; swapAnimating=false; clearing.clear(); fallStartRows.clear(); fallProgress=1f; comboBanner="";
        fillBoardNoMatches(); invalidate();
    }

    private void fillBoardNoMatches() {
        for(int r=0;r<ROWS;r++) for(int c=0;c<COLS;c++) {
            Kind k;
            do { k=randomKind(); } while((c>=2 && board[r][c-1]!=null && board[r][c-2]!=null && board[r][c-1].kind==k && board[r][c-2].kind==k) || (r>=2 && board[r-1][c]!=null && board[r-2][c]!=null && board[r-1][c].kind==k && board[r-2][c].kind==k));
            board[r][c]=new Tile(k);
        }
    }

    private Kind randomKind(){ return Kind.values()[rng.nextInt(Kind.values().length)]; }

    @Override public boolean onTouchEvent(MotionEvent e) {
        float x=e.getX(), y=e.getY();
        if(state==State.MENU){ if(e.getAction()==MotionEvent.ACTION_UP && startButton.contains(x,y)) beginLevel(); return true; }
        if(state==State.COMPLETE || state==State.FAILED){ if(e.getAction()==MotionEvent.ACTION_UP && nextButton.contains(x,y)){ if(state==State.COMPLETE){ level++; prefs.edit().putInt("level",level).apply(); } beginLevel(); } return true; }
        if(state!=State.PLAYING || inputLocked) return true;

        switch(e.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
                downX=x; downY=y; swipeConsumed=false;
                dragC=(int)((x-boardLeft)/cell); dragR=(int)((y-boardTop)/cell);
                if(dragR<0||dragR>=ROWS||dragC<0||dragC>=COLS){ dragR=dragC=-1; }
                return true;
            case MotionEvent.ACTION_MOVE:
                if(dragR<0 || swipeConsumed) return true;
                float dx=x-downX, dy=y-downY;
                float threshold=cell*.24f;
                if(Math.abs(dx)>=threshold || Math.abs(dy)>=threshold){
                    int nr=dragR, nc=dragC;
                    if(Math.abs(dx)>Math.abs(dy)) nc += dx>0?1:-1; else nr += dy>0?1:-1;
                    if(nr>=0&&nr<ROWS&&nc>=0&&nc<COLS){
                        swipeConsumed=true;
                        startSwap(dragR,dragC,nr,nc);
                    }
                }
                return true;
            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_CANCEL:
                dragR=dragC=-1;
                return true;
        }
        return true;
    }

    private void startSwap(int r1,int c1,int r2,int c2){
        inputLocked=true; swapAnimating=true; swapR1=r1;swapC1=c1;swapR2=r2;swapC2=c2;swapProgress=0f;
        animateFloat(0f,1f,SWAP_MS,v->{swapProgress=v;invalidate();},()->{
            swapAnimating=false;
            swap(r1,c1,r2,c2);
            MatchInfo info=findMatches();
            if(info.cells.isEmpty()) {
                // animate the rejected move back instead of snapping instantly
                swapAnimating=true; swapR1=r2;swapC1=c2;swapR2=r1;swapC2=c1;swapProgress=0f;
                animateFloat(0f,1f,SWAP_MS,v->{swapProgress=v;invalidate();},()->{
                    swapAnimating=false; swap(r1,c1,r2,c2); inputLocked=false; invalidate();
                });
                return;
            }
            moves--;
            cascadeDepth=1;
            Special created=detectSpecialAtSwap(r2,c2);
            resolveCascade(info,r2,c2,created);
        });
    }

    private void resolveCascade(MatchInfo info,int keepR,int keepC,Special create){
        Set<Integer> expanded=expandSpecials(info.cells);
        boolean keep=create!=Special.NONE && expanded.contains(keepR*COLS+keepC);
        if(keep) expanded.remove(keepR*COLS+keepC);

        int gained=calculateScore(info, expanded.size(), cascadeDepth);
        score += gained;
        String prefix = cascadeDepth>1 ? "COMBO x"+cascadeDepth+"  " : "";
        comboBanner = prefix + "+" + gained;
        comboBannerUntil = System.currentTimeMillis()+900;
        if(info.runCount>1) comboBanner = "MULTI MATCH x"+info.runCount+"  +"+gained;
        if(cascadeDepth>1 && info.runCount>1) comboBanner = "COMBO x"+cascadeDepth+" • MULTI x"+info.runCount+"  +"+gained;

        clearing.clear(); clearing.addAll(expanded); clearProgress=0f;
        animateFloat(0f,1f,CLEAR_MS,v->{clearProgress=v;invalidate();},()->{
            for(int pos:expanded){ int r=pos/COLS,c=pos%COLS; board[r][c]=null; }
            if(keep && board[keepR][keepC]!=null) board[keepR][keepC].special=create;
            clearing.clear(); clearProgress=0f;
            applyGravityAndPrepareFall();
            animateFloat(0f,1f,FALL_MS,v->{fallProgress=v;invalidate();},()->{
                fallProgress=1f; fallStartRows.clear(); invalidate();
                handler.postDelayed(()->{
                    MatchInfo next=findMatches();
                    if(!next.cells.isEmpty()) {
                        cascadeDepth++;
                        resolveCascade(next,-1,-1,Special.NONE);
                    } else {
                        finishTurn();
                    }
                },CASCADE_PAUSE_MS);
            });
        });
    }

    private int calculateScore(MatchInfo info,int clearedCount,int chain){
        int base=0;
        for(int len:info.runLengths) {
            if(len<=3) base += 300;
            else if(len==4) base += 650;
            else if(len==5) base += 1100;
            else base += 1100 + (len-5)*500;
        }
        // Reward intersections/special expansion without double-counting every line cell.
        base += Math.max(0, clearedCount-3*info.runCount)*70;
        float multiBonus = 1f + Math.max(0, info.runCount-1)*0.35f;
        float chainBonus = 1f + Math.max(0, chain-1)*0.55f;
        return Math.round(base*multiBonus*chainBonus);
    }

    private void finishTurn(){
        inputLocked=false;
        if(score>=target) {
            inputLocked=true;
            state=State.COMPLETE_ANIM;
            completeAnimStart=System.currentTimeMillis();
            invalidate();
            handler.postDelayed(()->{ state=State.COMPLETE; invalidate(); },1250);
        } else if(moves<=0) {
            state=State.FAILED; invalidate();
        }
    }

    private Special detectSpecialAtSwap(int r,int c){
        if(r<0||c<0||r>=ROWS||c>=COLS) return Special.NONE;
        Tile t=board[r][c]; if(t==null) return Special.NONE;
        int h=1,v=1; for(int x=c-1;x>=0&&board[r][x]!=null&&board[r][x].kind==t.kind;x--)h++; for(int x=c+1;x<COLS&&board[r][x]!=null&&board[r][x].kind==t.kind;x++)h++;
        for(int y=r-1;y>=0&&board[y][c]!=null&&board[y][c].kind==t.kind;y--)v++; for(int y=r+1;y<ROWS&&board[y][c]!=null&&board[y][c].kind==t.kind;y++)v++;
        if(h>=5||v>=5) return Special.HYPER; if(h>=4) return Special.ROW; if(v>=4) return Special.COL; return Special.NONE;
    }

    private Set<Integer> expandSpecials(Set<Integer> original){
        Set<Integer> expanded=new HashSet<>(original);
        boolean changed;
        do {
            changed=false;
            for(int pos:new HashSet<>(expanded)){
                int r=pos/COLS,c=pos%COLS; Tile t=board[r][c]; if(t==null) continue;
                int before=expanded.size();
                if(t.special==Special.ROW) for(int x=0;x<COLS;x++) expanded.add(r*COLS+x);
                else if(t.special==Special.COL) for(int y=0;y<ROWS;y++) expanded.add(y*COLS+c);
                else if(t.special==Special.HYPER){ Kind k=t.kind; for(int y=0;y<ROWS;y++) for(int x=0;x<COLS;x++) if(board[y][x]!=null&&board[y][x].kind==k) expanded.add(y*COLS+x); }
                if(expanded.size()!=before) changed=true;
            }
        } while(changed);
        return expanded;
    }

    private void applyGravityAndPrepareFall(){
        fallStartRows.clear();
        for(int c=0;c<COLS;c++) {
            int write=ROWS-1;
            for(int r=ROWS-1;r>=0;r--) {
                Tile t=board[r][c];
                if(t!=null) {
                    if(write!=r) {
                        board[write][c]=t; board[r][c]=null;
                        fallStartRows.put(t.id,(float)r);
                    }
                    write--;
                }
            }
            int spawnIndex=0;
            while(write>=0) {
                Tile t=new Tile(randomKind());
                board[write][c]=t;
                fallStartRows.put(t.id,-1f-spawnIndex);
                spawnIndex++; write--;
            }
        }
        fallProgress=0f;
    }

    private MatchInfo findMatches(){
        MatchInfo info=new MatchInfo();
        for(int r=0;r<ROWS;r++) {
            int c=0;
            while(c<COLS) {
                if(board[r][c]==null){c++;continue;}
                Kind k=board[r][c].kind; int end=c+1;
                while(end<COLS&&board[r][end]!=null&&board[r][end].kind==k) end++;
                int len=end-c;
                if(len>=3){ info.runCount++; info.runLengths.add(len); for(int x=c;x<end;x++) info.cells.add(r*COLS+x); }
                c=end;
            }
        }
        for(int c=0;c<COLS;c++) {
            int r=0;
            while(r<ROWS) {
                if(board[r][c]==null){r++;continue;}
                Kind k=board[r][c].kind; int end=r+1;
                while(end<ROWS&&board[end][c]!=null&&board[end][c].kind==k) end++;
                int len=end-r;
                if(len>=3){ info.runCount++; info.runLengths.add(len); for(int y=r;y<end;y++) info.cells.add(y*COLS+c); }
                r=end;
            }
        }
        return info;
    }

    private void swap(int r1,int c1,int r2,int c2){ Tile t=board[r1][c1]; board[r1][c1]=board[r2][c2]; board[r2][c2]=t; }

    private void animateFloat(float from,float to,long duration,final FloatUpdate update,final Runnable end){
        ValueAnimator a=ValueAnimator.ofFloat(from,to); a.setDuration(duration); a.setInterpolator(new DecelerateInterpolator());
        a.addUpdateListener(v->update.onUpdate((Float)v.getAnimatedValue()));
        a.addListener(new android.animation.AnimatorListenerAdapter(){ @Override public void onAnimationEnd(android.animation.Animator animation){ if(end!=null) end.run(); }});
        a.start();
    }

    interface FloatUpdate { void onUpdate(float value); }
}
