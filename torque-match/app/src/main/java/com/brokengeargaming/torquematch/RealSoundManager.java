package com.brokengeargaming.torquematch;
import android.content.Context;
import android.media.MediaPlayer;
public final class RealSoundManager {
  private final Context context;
  public RealSoundManager(Context c){context=c.getApplicationContext();}
  private void play(int id,float v){try{MediaPlayer m=MediaPlayer.create(context,id);if(m==null)return;m.setVolume(v,v);m.setOnCompletionListener(MediaPlayer::release);m.start();}catch(Exception ignored){}}
  public void levelStart(int l){int t=(l-1)%3;play(t==0?R.raw.engine_rev_1:t==1?R.raw.engine_rev_2:R.raw.engine_rev_3,.65f);}
  public void match(int l,int chain){int t=(l-1)%4;int id=t==0?R.raw.match_metal_1:t==1?R.raw.match_metal_2:t==2?R.raw.match_metal_3:R.raw.match_metal_4;play(id,Math.min(.55f+chain*.05f,.9f));if(chain>=3)play((l%2==0)?R.raw.tire_squeal_2:R.raw.tire_squeal_1,.42f);}
  public void fourMatch(int l){play((l%3==0)?R.raw.impact_wrench_3:R.raw.impact_wrench_1,.8f);}
  public void fiveMatch(int l){play((l%2==0)?R.raw.engine_rev_3:R.raw.engine_rev_2,.85f);}
  public void bomb(){play(R.raw.booster_bomb,.95f);} public void nitro(){play(R.raw.booster_nitro,.9f);} public void wrench(){play(R.raw.booster_wrench,.9f);}
  public void victory(){play(R.raw.victory_big,1f);} public void failure(){play(R.raw.failure_big,.95f);}
}