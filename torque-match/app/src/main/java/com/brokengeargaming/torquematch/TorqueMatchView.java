package com.brokengeargaming.torquematch;

import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.*;
import android.view.MotionEvent;
import android.view.View;

import java.util.*;

public class TorqueMatchView extends View {
    private static final int ROWS = 8, COLS = 8;
    private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint text = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Random rng = new Random();
    private final SharedPreferences prefs;
    private final Tile[][] board = new Tile[ROWS][COLS];
    private State state = State.MENU;
    private int level = 1, score = 0, moves = 22, target = 3000;
    private int selectedR = -1, selectedC = -1;
    private float boardLeft, boardTop, cell, width, height;
    private final RectF startButton = new RectF();
    private final RectF nextButton = new RectF();

    enum State { MENU, PLAYING, COMPLETE, FAILED }
    enum Kind { WHEEL, ROTOR, TURBO, SPARK, GEAR, PISTON }
    enum Special { NONE, ROW, COL, HYPER }

    static class Tile {
        Kind kind;
        Special special = Special.NONE;
        Tile(Kind k) { kind = k; }
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
        drawCentered(c, "Match parts. Build combos. Own the garage.", height*.58f, width*.038f, Color.LTGRAY);
        float bw = width*.70f, bh = height*.085f;
        startButton.set((width-bw)/2, height*.68f, (width+bw)/2, height*.68f+bh);
        drawButton(c, startButton, "PLAY LEVEL " + level);
        drawCentered(c, "Offline • No energy timer • No forced ads", height*.82f, width*.032f, Color.GRAY);
    }

    private void drawGame(Canvas c) {
        drawCentered(c, "LEVEL " + level, height*.06f, width*.048f, Color.WHITE);
        drawCentered(c, "SCORE " + score + " / " + target, height*.105f, width*.041f, Color.rgb(249,115,22));
        drawCentered(c, "MOVES  " + moves, height*.148f, width*.042f, moves <= 5 ? Color.rgb(239,68,68) : Color.LTGRAY);

        RectF tray = new RectF(boardLeft-8, boardTop-8, boardLeft+cell*COLS+8, boardTop+cell*ROWS+8);
        p.setColor(Color.rgb(22,22,26)); c.drawRoundRect(tray, 22,22,p);
        p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(3); p.setColor(Color.rgb(82,82,91)); c.drawRoundRect(tray,22,22,p); p.setStyle(Paint.Style.FILL);

        for (int r=0;r<ROWS;r++) for (int col=0;col<COLS;col++) drawTile(c,r,col,board[r][col]);
        if (state == State.COMPLETE || state == State.FAILED) drawResultOverlay(c);
    }

    private void drawTile(Canvas c, int r, int col, Tile t) {
        float x = boardLeft + col*cell, y = boardTop + r*cell;
        RectF box = new RectF(x+3,y+3,x+cell-3,y+cell-3);
        boolean sel = r==selectedR && col==selectedC;
        p.setColor(sel ? Color.rgb(80,60,30) : Color.rgb(39,39,45));
        c.drawRoundRect(box, cell*.20f, cell*.20f, p);
        if (t == null) return;
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
    }

    private void drawWheel(Canvas c,float x,float y,float s){
        p.setColor(Color.rgb(18,18,20)); c.drawCircle(x,y,s,p);
        p.setColor(Color.rgb(161,161,170)); c.drawCircle(x,y,s*.72f,p);
        p.setColor(Color.rgb(40,40,44)); c.drawCircle(x,y,s*.25f,p);
        p.setStrokeWidth(s*.12f); p.setColor(Color.rgb(63,63,70));
        for(int i=0;i<5;i++){ double a=i*Math.PI*2/5; c.drawLine(x+(float)Math.cos(a)*s*.25f,y+(float)Math.sin(a)*s*.25f,x+(float)Math.cos(a)*s*.65f,y+(float)Math.sin(a)*s*.65f,p); }
    }
    private void drawRotor(Canvas c,float x,float y,float s){ p.setColor(Color.rgb(203,213,225)); c.drawCircle(x,y,s,p); p.setColor(Color.rgb(239,68,68)); c.drawArc(new RectF(x-s*.9f,y-s*.9f,x+s*.9f,y+s*.9f),-30,70,true,p); p.setColor(Color.rgb(71,85,105)); c.drawCircle(x,y,s*.28f,p); }
    private void drawTurbo(Canvas c,float x,float y,float s){ p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(s*.24f); p.setColor(Color.rgb(56,189,248)); c.drawCircle(x,y,s*.72f,p); c.drawArc(new RectF(x-s,y-s,x+s,y+s),210,230,false,p); p.setStyle(Paint.Style.FILL); p.setColor(Color.rgb(14,116,144)); c.drawCircle(x,y,s*.22f,p); }
    private void drawSpark(Canvas c,float x,float y,float s){ p.setColor(Color.rgb(250,250,250)); c.drawRoundRect(new RectF(x-s*.23f,y-s*.8f,x+s*.23f,y+s*.35f),s*.12f,s*.12f,p); p.setColor(Color.rgb(59,130,246)); for(int i=0;i<3;i++) c.drawRect(x-s*.30f,y-s*.45f+i*s*.25f,x+s*.30f,y-s*.35f+i*s*.25f,p); p.setColor(Color.rgb(251,191,36)); c.drawRect(x-s*.09f,y+s*.30f,x+s*.09f,y+s*.85f,p); }
    private void drawGear(Canvas c,float x,float y,float s){ p.setColor(Color.rgb(249,115,22)); c.drawCircle(x,y,s*.74f,p); for(int i=0;i<8;i++){ double a=i*Math.PI/4; float tx=x+(float)Math.cos(a)*s*.82f, ty=y+(float)Math.sin(a)*s*.82f; c.save(); c.rotate(i*45,tx,ty); c.drawRect(tx-s*.16f,ty-s*.22f,tx+s*.16f,ty+s*.22f,p); c.restore(); } p.setColor(Color.rgb(39,39,42)); c.drawCircle(x,y,s*.28f,p); }
    private void drawPiston(Canvas c,float x,float y,float s){ p.setColor(Color.rgb(163,230,53)); c.drawRoundRect(new RectF(x-s*.55f,y-s*.65f,x+s*.55f,y-s*.05f),s*.12f,s*.12f,p); p.setStrokeWidth(s*.18f); c.drawLine(x,y,x,y+s*.62f,p); c.drawLine(x,y+s*.60f,x+s*.40f,y+s*.85f,p); }
    private void drawWheelLogo(Canvas c,float x,float y,float s){ drawWheel(c,x,y,s); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(7); p.setColor(Color.rgb(249,115,22)); c.drawCircle(x,y,s*1.18f,p); p.setStyle(Paint.Style.FILL); }

    private void drawResultOverlay(Canvas c) {
        p.setColor(Color.argb(225,8,8,10)); c.drawRoundRect(new RectF(width*.08f,height*.30f,width*.92f,height*.70f),28,28,p);
        boolean win = state==State.COMPLETE;
        drawCentered(c, win?"GARAGE CLEARED!":"OUT OF MOVES", height*.41f,width*.060f, win?Color.rgb(163,230,53):Color.rgb(239,68,68));
        drawCentered(c,"Score: " + score,height*.48f,width*.045f,Color.WHITE);
        float bw=width*.62f,bh=height*.075f;
        nextButton.set((width-bw)/2,height*.56f,(width+bw)/2,height*.56f+bh);
        drawButton(c,nextButton,win?"NEXT LEVEL":"TRY AGAIN");
    }

    private void drawButton(Canvas c, RectF r, String label) {
        p.setColor(Color.rgb(234,88,12)); c.drawRoundRect(r,25,25,p);
        p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(3); p.setColor(Color.rgb(251,146,60)); c.drawRoundRect(r,25,25,p); p.setStyle(Paint.Style.FILL);
        drawText(c,label,r.centerX(),r.centerY()+textSize(width*.044f)*.34f,width*.044f,Color.WHITE,Paint.Align.CENTER);
    }

    private void drawCentered(Canvas c,String s,float y,float size,int color){ drawText(c,s,width/2f,y,size,color,Paint.Align.CENTER); }
    private void drawText(Canvas c,String s,float x,float y,float size,int color,Paint.Align align){ text.setTextSize(textSize(size)); text.setColor(color); text.setTextAlign(align); c.drawText(s,x,y,text); }
    private float textSize(float px){ return Math.max(12,px); }

    private void beginLevel() {
        state=State.PLAYING; score=0; moves=Math.max(16,24-(level-1)/3); target=2800+(level-1)*950;
        selectedR=selectedC=-1;
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
        if(e.getAction()!=MotionEvent.ACTION_UP) return true;
        float x=e.getX(), y=e.getY();
        if(state==State.MENU){ if(startButton.contains(x,y)) beginLevel(); return true; }
        if(state==State.COMPLETE || state==State.FAILED){ if(nextButton.contains(x,y)){ if(state==State.COMPLETE){ level++; prefs.edit().putInt("level",level).apply(); } beginLevel(); } return true; }
        int c=(int)((x-boardLeft)/cell), r=(int)((y-boardTop)/cell);
        if(r<0||r>=ROWS||c<0||c>=COLS) return true;
        if(selectedR<0){ selectedR=r; selectedC=c; invalidate(); return true; }
        int dist=Math.abs(selectedR-r)+Math.abs(selectedC-c);
        if(dist==1){ attemptSwap(selectedR,selectedC,r,c); selectedR=selectedC=-1; invalidate(); }
        else { selectedR=r; selectedC=c; invalidate(); }
        return true;
    }

    private void attemptSwap(int r1,int c1,int r2,int c2){
        swap(r1,c1,r2,c2);
        Set<Integer> matches=findMatches();
        if(matches.isEmpty()){ swap(r1,c1,r2,c2); return; }
        moves--;
        Special created = detectSpecialAtSwap(r2,c2);
        resolve(matches,r2,c2,created);
        if(score>=target) state=State.COMPLETE; else if(moves<=0) state=State.FAILED;
    }

    private Special detectSpecialAtSwap(int r,int c){
        Tile t=board[r][c]; if(t==null) return Special.NONE;
        int h=1,v=1; for(int x=c-1;x>=0&&board[r][x]!=null&&board[r][x].kind==t.kind;x--)h++; for(int x=c+1;x<COLS&&board[r][x]!=null&&board[r][x].kind==t.kind;x++)h++;
        for(int y=r-1;y>=0&&board[y][c]!=null&&board[y][c].kind==t.kind;y--)v++; for(int y=r+1;y<ROWS&&board[y][c]!=null&&board[y][c].kind==t.kind;y++)v++;
        if(h>=5||v>=5) return Special.HYPER; if(h>=4) return Special.ROW; if(v>=4) return Special.COL; return Special.NONE;
    }

    private void resolve(Set<Integer> matches,int keepR,int keepC,Special create){
        boolean keep=create!=Special.NONE && matches.contains(keepR*COLS+keepC);
        Set<Integer> expanded=new HashSet<>(matches);
        for(int pos:matches){ int r=pos/COLS,c=pos%COLS; Tile t=board[r][c]; if(t==null)continue; if(t.special==Special.ROW) for(int x=0;x<COLS;x++) expanded.add(r*COLS+x); else if(t.special==Special.COL) for(int y=0;y<ROWS;y++) expanded.add(y*COLS+c); else if(t.special==Special.HYPER){ Kind k=t.kind; for(int y=0;y<ROWS;y++) for(int x=0;x<COLS;x++) if(board[y][x]!=null&&board[y][x].kind==k) expanded.add(y*COLS+x); }}
        for(int pos:expanded){ int r=pos/COLS,c=pos%COLS; if(keep&&r==keepR&&c==keepC) continue; if(board[r][c]!=null){ board[r][c]=null; score+=100; }}
        if(keep && board[keepR][keepC]!=null){ board[keepR][keepC].special=create; score += create==Special.HYPER?500:250; }
        collapseAndRefill();
        Set<Integer> more=findMatches();
        int chain=0;
        while(!more.isEmpty() && chain++<12){ for(int pos:more){int r=pos/COLS,c=pos%COLS;if(board[r][c]!=null){board[r][c]=null;score+=125+chain*25;}} collapseAndRefill(); more=findMatches(); }
    }

    private void collapseAndRefill(){
        for(int c=0;c<COLS;c++){
            int write=ROWS-1;
            for(int r=ROWS-1;r>=0;r--) if(board[r][c]!=null) board[write--][c]=board[r][c];
            while(write>=0) board[write--][c]=new Tile(randomKind());
        }
    }

    private Set<Integer> findMatches(){
        Set<Integer> out=new HashSet<>();
        for(int r=0;r<ROWS;r++){ int start=0; while(start<COLS){ int end=start+1; while(end<COLS&&board[r][start]!=null&&board[r][end]!=null&&board[r][start].kind==board[r][end].kind)end++; if(end-start>=3) for(int c=start;c<end;c++) out.add(r*COLS+c); start=end; }}
        for(int c=0;c<COLS;c++){ int start=0; while(start<ROWS){ int end=start+1; while(end<ROWS&&board[start][c]!=null&&board[end][c]!=null&&board[start][c].kind==board[end][c].kind)end++; if(end-start>=3) for(int r=start;r<end;r++) out.add(r*COLS+c); start=end; }}
        return out;
    }

    private void swap(int r1,int c1,int r2,int c2){ Tile t=board[r1][c1]; board[r1][c1]=board[r2][c2]; board[r2][c2]=t; }
}
