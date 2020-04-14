import threading
import time
import subprocess
import os
import cv2
import numpy as np

class screen_process_class (threading.Thread):

    running = False
    mode = ''

    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
    
    def run(self):
        while (self.running):
            p = subprocess.Popen("adb exec-out screencap -p", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            image_bytes = p.stdout.read().replace(b'\r\n', b'\n')
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # cv2.imshow("screen", image)
            # cv2.waitKey(0)
            # cv2.destroyWindow("")
            retval = p.wait()
            if (mode == ''):
                pass

    def go_to_arena(self):
        # Click Menu Button
        p = subprocess.Popen("adb exec-out input tap 200 50", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        # Click Home
        p = subprocess.Popen("adb exec-out input tap 200 200", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        
        # Click Fight
        p = subprocess.Popen("adb exec-out input tap 400 200", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()


        
    def start_process(self):
        self.running = True

    def stop_process(self):
        self.running = False