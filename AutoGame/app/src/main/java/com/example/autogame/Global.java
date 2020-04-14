package com.example.autogame;

import android.app.Instrumentation;
import android.os.IBinder;
import android.os.SystemClock;
import android.util.Log;
import android.view.MotionEvent;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;

public class Global {
    public static Instrumentation m_Instrumentation = new Instrumentation();

    public static boolean done_flag = true;
    public static boolean result = false;

    public static Thread eventThr = new Thread(){
        @Override
        public void run() {
            m_Instrumentation.sendPointerSync(MotionEvent.obtain(
                    SystemClock.uptimeMillis(),
                    SystemClock.uptimeMillis(),
                    MotionEvent.ACTION_DOWN, 100,1300, 0));
            Log.d("ABC", "TOUCH DOWN ");
            m_Instrumentation.sendPointerSync(MotionEvent.obtain(
                    SystemClock.uptimeMillis(),
                    SystemClock.uptimeMillis(),
                    MotionEvent.ACTION_UP, 100,1300, 0));
            Log.d("ABC", "TOUCH UP ");

            try {
                this.wait();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    };

    public static void autoSwipe(final float x1, final float y1, final float x2, final float y2, final int duration, final boolean wait){
        Log.d("ABC", "Swipe " +  x1 + " " + y1 + " " + x2 + " " + y2);
        new Thread(new Runnable() {
            @Override
            public void run() {
                try{
                    while (done_flag == false);
                    Process process = Runtime.getRuntime().exec("su", null, null);
                    DataOutputStream os = new DataOutputStream(process.getOutputStream());
                    String cmd = "/system/bin/input touchscreen swipe " + x1 + " " + y1 + " " + x2 + " " + y2 + " " + duration + "\n";
                    os.writeBytes(cmd);
                    os.writeBytes("exit\n");
                    os.flush();
                    os.close();
                    if (wait == true){
                        process.waitFor();
                    }
                } catch (Exception ex){
                    Log.e("ERROR", ex.toString());
                }
                done_flag = true;
                return;
            }
        }).start();
    }

    public static void autoClickXY(final float x, final float y, final boolean wait){
        Log.d("ABC", "Clicked " + x + " " + y);
        new Thread(new Runnable() {
            @Override
            public void run() {
                try{
                    while (done_flag == false);
                    Process process = Runtime.getRuntime().exec("su", null, null);
                    DataOutputStream os = new DataOutputStream(process.getOutputStream());
                    String cmd = "/system/bin/input tap " + x + " " + y + "\n";
                    os.writeBytes(cmd);
                    os.writeBytes("exit\n");
                    os.flush();
                    os.close();
                    if (wait == true){
                        process.waitFor();
                    }
                } catch (Exception ex){
                    Log.e("ERROR", ex.toString());
                }
                done_flag = true;
                return;
            }
        }).start();

    }

    public static boolean captureScreen() {
        Log.d("ABC", "Capturing");

        new Thread(new Runnable() {
            @Override
            public void run() {
                try{
                    Process process = null;
                    // Check if folder exist or not
                    process = Runtime.getRuntime().exec("su", null, null);
                    DataOutputStream os = new DataOutputStream(process.getOutputStream());
                    String cmd = "/system/bin/ls /mnt/sdcard/ \n";
                    os.writeBytes(cmd);
                    os.writeBytes("exit\n");
                    os.flush();
                    os.close();
                    process.waitFor();
                    BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                    String line = "";
                    boolean hasAutoGameFolder = false;
                    while ((line = reader.readLine())!= null) {
                        Log.d("ABC", line);
                        if (line == "AutoGame"){
                            hasAutoGameFolder = true;
                            break;
                        }
                    }

                    // Create folder AutoGame If Not Exist
                    if (hasAutoGameFolder == false){
                        process = Runtime.getRuntime().exec("su", null, null);
                        os = new DataOutputStream(process.getOutputStream());
                        cmd = "/system/bin/mkdir /mnt/sdcard/AutoGame \n";
                        os.writeBytes(cmd);
                        os.writeBytes("exit\n");
                        os.flush();
                        os.close();
                        process.waitFor();
                    }

                    Log.d("ABC", "Created");

                    // Capture Screen
                    process = Runtime.getRuntime().exec("su", null, null);
                    os = new DataOutputStream(process.getOutputStream());
                    cmd = "/system/bin/screencap /mnt/sdcard/AutoGame/capture.png \n";
                    os.writeBytes(cmd);
                    os.writeBytes("exit\n");
                    os.flush();
                    os.close();
                    process.waitFor();

                    Log.d("ABC", "Captured");

                    result = true;
                } catch (Exception ex){
                    Log.e("ERROR", ex.toString());
                }
            }
        }).start();

        return result;
    }
}
