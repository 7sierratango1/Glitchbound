package com.brokengeargaming.torquematch;
import android.content.Context;
import android.media.MediaPlayer;
import java.util.Random;

public final class RealSoundManager {
  private final Context context; private final Random rnd=new Random();
  public RealSoundManager(Context c){context=c.getApplicationContext();}
  private void play(int id,float v){try{MediaPlayer m=MediaPlayer.create(context,id);if(m==null)return;m.setVolume(v,v);m.setOnCompletionListener(MediaPlayer::release);m.start();}catch(Exception ignored){}}
  private int pick(int[] ids,int salt){return ids[Math.floorMod(salt+rnd.nextInt(ids.length),ids.length)];}
  private static final int[] WHEEL={R.raw.wheel_1,R.raw.wheel_2,R.raw.wheel_3};
  private static final int[] ROTOR={R.raw.rotor_1,R.raw.rotor_2,R.raw.rotor_3};
  private static final int[] TURBO={R.raw.turbo_1,R.raw.turbo_2,R.raw.turbo_3};
  private static final int[] SPARK={R.raw.spark_1,R.raw.spark_2,R.raw.spark_3};
  private static final int[] GEAR={R.raw.gear_1,R.raw.gear_2,R.raw.gear_3};
  private static final int[] PISTON={R.raw.piston_1,R.raw.piston_2,R.raw.piston_3};
  public void levelStart(int l){play(pick(new int[]{R.raw.engine_rev_1,R.raw.engine_rev_2,R.raw.engine_rev_3},l),.62f);}
  public void swipe(){play(R.raw.swipe_part,.32f);}
  public void partMatch(TorqueMatchView.Kind k,int level,int chain,int length,TorqueMatchView.Special made){
    int[] bank; switch(k){case WHEEL:bank=WHEEL;break;case ROTOR:bank=ROTOR;break;case TURBO:bank=TURBO;break;case SPARK:bank=SPARK;break;case PISTON:bank=PISTON;break;default:bank=GEAR;}
    play(pick(bank,level+chain+length),Math.min(.58f+chain*.055f,.9f));
    if(length>=4) play(R.raw.match_four,.60f); if(length>=5) play(R.raw.match_five,.72f);
    if(chain>=2) play(chain>=4?R.raw.cascade_big:R.raw.cascade_small,Math.min(.42f+chain*.07f,.8f));
    if(made==TorqueMatchView.Special.ROW||made==TorqueMatchView.Special.COL)play(R.raw.line_special,.62f);
    else if(made==TorqueMatchView.Special.BOMB)play(R.raw.booster_bomb,.74f);
    else if(made==TorqueMatchView.Special.SUPER)play(R.raw.super_special,.82f);
  }
  public void special(){play(R.raw.super_special,.78f);} public void superCombo(){play(R.raw.super_combo,.95f);}
  public void bomb(){play(R.raw.booster_bomb,.95f);} public void nitro(){play(R.raw.booster_nitro,.9f);} public void wrench(){play(R.raw.booster_wrench,.9f);} public void extraMoves(){play(R.raw.extra_moves,.7f);}
  public void victory(int stars){play(stars>=3?R.raw.victory_three:R.raw.victory_big,1f);} public void failure(){play(R.raw.failure_big,.95f);}
}
