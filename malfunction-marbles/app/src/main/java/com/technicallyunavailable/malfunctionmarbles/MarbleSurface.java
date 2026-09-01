package com.technicallyunavailable.malfunctionmarbles;

import android.content.Context;
import android.opengl.GLSurfaceView;

public class MarbleSurface extends GLSurfaceView {
    public final GameRenderer renderer;
    public MarbleSurface(Context context) {
        super(context);
        setEGLContextClientVersion(3);
        renderer = new GameRenderer();
        setRenderer(renderer);
        setRenderMode(GLSurfaceView.RENDERMODE_CONTINUOUSLY);
        setPreserveEGLContextOnPause(true);
    }
}
