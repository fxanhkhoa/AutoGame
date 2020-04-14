package com.example.autogame;

import android.annotation.SuppressLint;
import android.app.Instrumentation;
import android.app.Service;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.graphics.Point;
import android.location.SettingInjectorService;
import android.os.Build;
import android.os.IBinder;
import android.os.SystemClock;
import android.util.Log;
import android.view.Display;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewTreeObserver;
import android.view.WindowManager;
import android.widget.ImageView;
import android.widget.RelativeLayout;

import androidx.annotation.Nullable;

import java.io.DataOutputStream;

public class AutoGameService extends Service {

    private WindowManager mWindowManager;
    private View mOverlayView;
    int mWidth;
    private ImageView counterFab, mButtonClose, autoHit;
    boolean activity_background;
    final Instrumentation m_Instrumentation = new Instrumentation();

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @SuppressLint("ClickableViewAccessibility")
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null) {
            activity_background = intent.getBooleanExtra("activity_background", false);
        }
        if (mOverlayView == null) {
            mOverlayView = LayoutInflater.from(this).inflate(R.layout.activity_main, null);

            int LAYOUT_FLAG;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                LAYOUT_FLAG = WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY;
            } else {
                LAYOUT_FLAG = WindowManager.LayoutParams.TYPE_PHONE;
            }

            final WindowManager.LayoutParams params = new WindowManager.LayoutParams(
                    WindowManager.LayoutParams.WRAP_CONTENT,
                    WindowManager.LayoutParams.WRAP_CONTENT,
                    LAYOUT_FLAG,
                    WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
                    PixelFormat.TRANSLUCENT);

            //Specify the view position
            params.gravity = Gravity.TOP | Gravity.LEFT;        //Initially view will be added to top-left corner
            params.x = 0;
            params.y = 100;

            mWindowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
            mWindowManager.addView(mOverlayView, params);

            Display display = mWindowManager.getDefaultDisplay();
            final Point size = new Point();
            display.getSize(size);

            counterFab = (ImageView) mOverlayView.findViewById(R.id.fabHead);
            mButtonClose = (ImageView) mOverlayView.findViewById(R.id.closeButton);
            autoHit = (ImageView) mOverlayView.findViewById(R.id.autoHit);

            final RelativeLayout layout = (RelativeLayout) mOverlayView.findViewById(R.id.layout);
            final ViewTreeObserver vto = layout.getViewTreeObserver();
            vto.addOnGlobalLayoutListener(new ViewTreeObserver.OnGlobalLayoutListener() {
                @Override
                public void onGlobalLayout() {
                    layout.getViewTreeObserver().removeOnGlobalLayoutListener(this);
                    int width = layout.getMeasuredWidth();

                    //To get the accurate middle of the screen we subtract the width of the floating widget.
                    mWidth = size.x - width;

                }
            });

            mButtonClose.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    stopSelf();
                }
            });

            autoHit.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
//                    autoHit(10);
                    Global.captureScreen();
                }
            });

            counterFab.setOnTouchListener(new View.OnTouchListener() {

                private int initialX;
                private int initialY;
                private float initialTouchX;
                private float initialTouchY;

                @Override
                public boolean onTouch(View v, MotionEvent event) {
                    switch (event.getAction()) {
                        case MotionEvent.ACTION_DOWN:

                            //remember the initial position.
                            initialX = params.x;
                            initialY = params.y;


                            //get the touch location
                            initialTouchX = event.getRawX();
                            initialTouchY = event.getRawY();


                            return true;
                        case MotionEvent.ACTION_UP:

                            //Only start the activity if the application is in background. Pass the current badge_count to the activity
//                            if(activity_background){
//                                float xDiff = event.getRawX() - initialTouchX;
//                                float yDiff = event.getRawY() - initialTouchY;
//
//                                if ((Math.abs(xDiff) < 5) && (Math.abs(yDiff) < 5)) {
//                                    Intent intent = new Intent(getBaseContext(), PostInputActivity.class);
//                                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
////                                    startActivity(intent);
//                                    Log.d("ABC", "Clicked " + xDiff + " " + yDiff);
//                                    //close the service and remove the fab view
//                                }
//                                stopSelf();
//                            }

                            //Logic to auto-position the widget based on where it is positioned currently w.r.t middle of the screen.
                            int middle = mWidth / 2;
                            float nearestXWall = params.x >= middle ? mWidth : 0;
                            params.x = (int) nearestXWall;


                            mWindowManager.updateViewLayout(mOverlayView, params);

//                            Global.eventThr.start();

//                            new Thread(new Runnable() {
//                                @Override
//                                public void run() {
//                                    try{
//                                        m_Instrumentation.sendPointerSync(MotionEvent.obtain(
//                                                SystemClock.uptimeMillis(),
//                                                SystemClock.uptimeMillis(),
//                                                MotionEvent.ACTION_DOWN, 100,1300, 0));
//                                        Log.d("ABC", "TOUCH DOWN ");
//                                        m_Instrumentation.sendPointerSync(MotionEvent.obtain(
//                                                SystemClock.uptimeMillis(),
//                                                SystemClock.uptimeMillis(),
//                                                MotionEvent.ACTION_UP, 100,1300, 0));
//                                        Log.d("ABC", "TOUCH UP ");
//                                    } catch (Exception ex){
//                                        Log.e("ABC", ex.toString());
//                                    }
//
//                                    return;
//                                }
//                            }).start();


//                            mOverlayView.getRootView().dispatchTouchEvent(MotionEvent.obtain(
//                                    SystemClock.uptimeMillis(),
//                                    SystemClock.uptimeMillis(),
//                                    MotionEvent.ACTION_DOWN, 100,1000, 0));
//
//                            mOverlayView.getRootView().dispatchTouchEvent(MotionEvent.obtain(
//                                    SystemClock.uptimeMillis(),
//                                    SystemClock.uptimeMillis(),
//                                    MotionEvent.ACTION_UP, 100,1000, 0));

//                            new Thread(new Runnable() {
//                                @Override
//                                public void run() {
//                                    try {
//                                        Thread.sleep(1000);
//                                        Global.autoClickXY(100, 1300, true);
//                                    } catch (InterruptedException e) {
//                                        Log.e("ERROR", e.toString());
//                                    }
//                                }
//                            }).start();

                            try {
                                // Click Game Icon
//                                params.x = 100;
////                                params.y = 1300;
////                                mWindowManager.updateViewLayout(mOverlayView, params);
////                                Global.autoClickXY(100, 1300, true);
////                                Thread.sleep(120000);

//                                 Claim Reward
//                                params.x = 966;
//                                params.y = 1012;
//                                mWindowManager.updateViewLayout(mOverlayView, params);
//                                autoClickXY(966, 1012);
//                                Log.d("ABC", "Click 966 1012");
//                                Thread.sleep(10000);


                                // Click Fight
                                params.x = 523;
                                params.y = 127;
                                mWindowManager.updateViewLayout(mOverlayView, params);
                                Global.autoClickXY(523, 127, true);
                                Thread.sleep(6000);

                                // Click Play Arena
                                params.x = 908;
                                params.y = 867;
                                mWindowManager.updateViewLayout(mOverlayView, params);
                                Global.autoClickXY(908, 867, true);
                                Thread.sleep(16000);

                                // Click Continue arena 3vs3
                                params.x = 254;
                                params.y = 966;
                                mWindowManager.updateViewLayout(mOverlayView, params);
                                Global.autoClickXY(254, 966,true);
                                Thread.sleep(12000);

//                                // Click Filter
//                                params.x = 254;
//                                params.y = 966;
//                                mWindowManager.updateViewLayout(mOverlayView, params);
//                                autoClickXY(1836, 982);
//                                Thread.sleep(8000);
//
//                                // Click Availability
//                                params.x = 1769;
//                                params.y = 913;
//                                mWindowManager.updateViewLayout(mOverlayView, params);
//                                autoClickXY(1769, 913);
//                                Thread.sleep(8000);
//
//                                // Click Filter Again
//                                params.x = 1455;
//                                params.y = 973;
//                                mWindowManager.updateViewLayout(mOverlayView, params);
//                                autoClickXY(1455, 973);
//                                Thread.sleep(8000);

                                // Swipe 1st Character
                                params.x = 295;
                                params.y = 168;
                                mWindowManager.updateViewLayout(mOverlayView, params);
                                Global.autoSwipe(1008, 551, 295, 168, 1000,true);
                                Thread.sleep(5000);

                                // Swipe 2nd Character
                                params.x = 254;
                                params.y = 966;
                                mWindowManager.updateViewLayout(mOverlayView, params);
                                Global.autoSwipe(1008, 551, 329, 362, 1000, true);
                                Thread.sleep(5000);

                                // Swipe 3rd Character
                                params.x = 254;
                                params.y = 966;
                                mWindowManager.updateViewLayout(mOverlayView, params);
                                Global.autoSwipe(1008, 551, 303, 508, 1000, true);
                                Thread.sleep(3000);

                                // Click Find Match
                                params.x = 254;
                                params.y = 966;
                                mWindowManager.updateViewLayout(mOverlayView, params);
                                Global.autoClickXY(254, 966, true);
                                Thread.sleep(8000);

                                // Click Find Match
                                params.x = 200;
                                params.y = 1017;
                                mWindowManager.updateViewLayout(mOverlayView, params);
                                Global.autoClickXY(200, 1017,true);
                                Thread.sleep(8000);

                                // Click Continue
                                params.x = 1750;
                                params.y = 1035;
                                mWindowManager.updateViewLayout(mOverlayView, params);
                                Global.autoClickXY(1750, 1035, true);
                                Thread.sleep(8000);

                                // Click Accept
                                params.x = 1722;
                                params.y = 1041;
                                mWindowManager.updateViewLayout(mOverlayView, params);
                                Global.autoClickXY(1722, 1041, true);
                                Thread.sleep(8000);

                                // Click Continue
                                params.x = 1761;
                                params.y = 1048;
                                mWindowManager.updateViewLayout(mOverlayView, params);
                                Global.autoClickXY(1761, 1048, true);
                                Thread.sleep(15000);

                                // Game play Here
                                gamePlay();
                                Thread.sleep(5000);

                                // Click Next Fight
                                params.x = 1151;
                                params.y = 858;
//                                mWindowManager.updateViewLayout(mOverlayView, params);
                                Global.autoClickXY(1151, 858, true);
                                Thread.sleep(1000);
                                Global.autoClickXY(1168, 707, true);
                                Thread.sleep(12000);

                                // Game play Here
                                gamePlay();
                                Thread.sleep(5000);

                                // Click Final Fight
                                params.x = 1151;
                                params.y = 858;
//                                mWindowManager.updateViewLayout(mOverlayView, params);
                                Global.autoClickXY(1151, 858, true);
                                Thread.sleep(1000);
                                Global.autoClickXY(1168, 707, true);
                                Thread.sleep(12000);

                                // Game play Here
                                gamePlay();
                                Thread.sleep(5000);

                                // Tap anywhere to continue
                                params.x = 1018;
                                params.y = 941;
                                mWindowManager.updateViewLayout(mOverlayView, params);
                                Global.autoClickXY(1018, 941, true);
                                Thread.sleep(10000);

                                // Tap Next Series
                                params.x = 1443;
                                params.y = 1033;
                                mWindowManager.updateViewLayout(mOverlayView, params);
                                Global.autoClickXY(1443, 1033, true);
                                Thread.sleep(20000);

                            } catch (InterruptedException e) {
                                e.printStackTrace();
                            }


                            Log.d("ABC", "UP ");

                            return true;
                        case MotionEvent.ACTION_MOVE:


                            int xDiff2 = Math.round(event.getRawX() - initialTouchX);
                            int yDiff2 = Math.round(event.getRawY() - initialTouchY);


                            //Calculate the X and Y coordinates of the view.
                            params.x = initialX + xDiff2;
                            params.y = initialY + yDiff2;

                            //Update the layout with new X & Y coordinates
                            mWindowManager.updateViewLayout(mOverlayView, params);

                            Log.d("ABC", event.getRawX() + " " + event.getRawY());

                            return true;
                    }
                    return false;
                }
            });
        }
        return super.onStartCommand(intent, flags, startId);
    }

    @Override
    public void onCreate() {
        super.onCreate();
        setTheme(R.style.AppTheme);
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (mOverlayView != null)
            mWindowManager.removeView(mOverlayView);
    }


    private void gamePlay(){
        for (int i = 0 ; i < 35; i++)
        {
            try{
                Log.d("ABC", String.valueOf(i));
                // ** Swipe 3 times;
                Global.autoSwipe(1561, 484, 1650, 484, 200, false);
                Global.autoSwipe(1561, 484, 1650, 484, 200, false);
                Global.autoSwipe(1561, 484, 1650, 484, 200, false);
                Thread.sleep(700);

                // ** Hit 4 times
                Global.autoClickXY(1636, 544, false);
                Global.autoClickXY(1398, 566, false);
                Global.autoClickXY(1662, 684, false);
                Global.autoClickXY(1398, 566, false);
                Global.autoClickXY(1662, 684, false);
                Global.autoClickXY(1662, 684, false);
                Global.autoClickXY(1398, 566, false);
                Global.autoClickXY(1662, 684, false);
                Thread.sleep(700);

                // ** Swipe left 1 time
                Global.autoSwipe(552, 544, 333, 572, 200, false);
                Thread.sleep(700);

                // ** Swipe 3 times;
                Global.autoSwipe(1561, 484, 1650, 484, 200, false);
                Global.autoSwipe(1561, 484, 1650, 484, 200, false);
                Thread.sleep(700);

                // ** Skill
                Global.autoClickXY(293, 996, false);
                Global.autoClickXY(293, 996, false);
                Global.autoClickXY(293, 996, false);
                Thread.sleep(1000);
            } catch (Exception ex){
                Log.e("ERROR",ex.toString());
            }
        }
    }

    private void autoHit(int times){
        for (int i = 0 ; i < times; i++)
        {
            try{
                Log.d("ABC", String.valueOf(i));
                // ** Swipe 3 times;
                Global.autoSwipe(1561, 484, 1650, 484, 200, false);
                Global.autoSwipe(1561, 484, 1650, 484, 200, false);
                Global.autoSwipe(1561, 484, 1650, 484, 200, false);

                // ** Hit 4 times
                Global.autoClickXY(1636, 544, false);
                Global.autoClickXY(1398, 566, false);
                Global.autoClickXY(1662, 684, false);
                Global.autoClickXY(1398, 566, false);
                Global.autoClickXY(1398, 566, false);

                // ** Swipe left 1 time
                Global.autoSwipe(552, 544, 333, 572, 200, false);

                // ** Swipe 3 times;
                Global.autoSwipe(1561, 484, 1650, 484, 200, false);
                Global.autoSwipe(1561, 484, 1650, 484, 200, false);

                // ** Skill
                Global.autoClickXY(293, 996, false);
                Global.autoClickXY(293, 996, false);
                Global.autoClickXY(293, 996, false);
                Thread.sleep(2000);
            } catch (Exception ex){
                Log.e("ERROR",ex.toString());
            }
        }
    }

}
