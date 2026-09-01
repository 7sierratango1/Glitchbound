package com.technicallyunavailable.malfunctionmarbles;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;

public class MainActivity extends Activity {
    private MarbleSurface gameView;
    private TextView positionText;
    private TextView mapText;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);

        FrameLayout root = new FrameLayout(this);
        gameView = new MarbleSurface(this);
        root.addView(gameView, new FrameLayout.LayoutParams(-1, -1));

        positionText = hudText("1st / 10", 27);
        FrameLayout.LayoutParams pos = new FrameLayout.LayoutParams(-2, -2);
        pos.gravity = Gravity.TOP | Gravity.LEFT; pos.leftMargin = 28; pos.topMargin = 22;
        root.addView(positionText, pos);

        mapText = hudText("01 • Ember Run", 18);
        FrameLayout.LayoutParams map = new FrameLayout.LayoutParams(-2, -2);
        map.gravity = Gravity.TOP | Gravity.RIGHT; map.rightMargin = 28; map.topMargin = 24;
        root.addView(mapText, map);

        LinearLayout controls = new LinearLayout(this);
        controls.setOrientation(LinearLayout.HORIZONTAL);
        controls.setGravity(Gravity.CENTER);
        Button prev = button("◀ MAP");
        Button race = button("RACE / RESTART");
        Button next = button("MAP ▶");
        controls.addView(prev); controls.addView(race); controls.addView(next);
        FrameLayout.LayoutParams cp = new FrameLayout.LayoutParams(-2, -2);
        cp.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL; cp.bottomMargin = 22;
        root.addView(controls, cp);

        prev.setOnClickListener(v -> gameView.queueEvent(() -> gameView.renderer.selectRelative(-1)));
        next.setOnClickListener(v -> gameView.queueEvent(() -> gameView.renderer.selectRelative(1)));
        race.setOnClickListener(v -> gameView.queueEvent(() -> gameView.renderer.restartRace()));
        gameView.renderer.listener = (place, total, mapName, mapIndex) -> runOnUiThread(() -> {
            positionText.setText(ordinal(place) + " / " + total);
            mapText.setText(String.format("%02d • %s", mapIndex + 1, mapName));
        });
        setContentView(root);
    }

    private TextView hudText(String s, int sp) {
        TextView t = new TextView(this); t.setText(s); t.setTextColor(Color.WHITE); t.setTextSize(sp);
        t.setShadowLayer(7, 0, 2, Color.BLACK); t.setPadding(12, 7, 12, 7); return t;
    }
    private Button button(String s) {
        Button b = new Button(this); b.setText(s); b.setTextColor(Color.WHITE); b.setTextSize(13);
        b.setBackgroundResource(com.technicallyunavailable.malfunctionmarbles.R.drawable.button_bg);
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-2, -2); p.setMargins(8, 0, 8, 0); b.setLayoutParams(p); return b;
    }
    private static String ordinal(int n) {
        int m=n%100; if(m>=11&&m<=13)return n+"th"; switch(n%10){case 1:return n+"st";case 2:return n+"nd";case 3:return n+"rd";default:return n+"th";}
    }
    @Override protected void onResume(){super.onResume();gameView.onResume();}
    @Override protected void onPause(){gameView.onPause();super.onPause();}
}
