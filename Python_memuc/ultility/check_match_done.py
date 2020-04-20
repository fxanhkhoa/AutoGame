import threading
import time
import subprocess
import os
import cv2
import numpy as np

class check_match_done (threading.Thread):
    
    process_running = False
    

    def __init__(self, threadID, pic_folder):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.pic_folder = pic_folder
        self.try_count = 0
        self.match_is_done = False
    
    def run(self):
        while True:
            if self.process_running:
                if (self.check_CONTINUE()):
                    self.match_is_done = True
                    self.stop_check()
                else:
                    self.match_is_done = False

    def get_done_status(self):
        return self.match_is_done
    
    def check_CONTINUE(self):
        print("DEBUG === CHECK CONTINUE IN SUB THREAD")
        try:
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            res = True

            arr = [[ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3]]

            x = 1201
            x1 = 1251
            y =  696
            for i in range(x, x1):
                if image[y][i][0] != arr[i - x][0] or image[y][i][1] != arr[i - x][1] or image[y][i][2] != arr[i - x][2]:
                    res = False
                    break
            
            arr = [[ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3]]

            res2 = True
            # Né 822 -> 883
            x = 971
            x1 = 1021
            y =  695
            for i in range(x, x1):
                if image[y][i][0] != arr[i - x][0] or image[y][i][1] != arr[i - x][1] or image[y][i][2] != arr[i - x][2]:
                    res2 = False
                    break


            res3 = True

            arr = [[255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [217, 217, 217], [110, 110, 111], [53, 53, 55], [47, 47, 49], [91, 91, 93], [249, 249, 249], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [188, 188, 188], [60, 60, 62], [47, 47, 49], [47, 47, 49], [77, 77, 79], [244, 244, 244], [255, 255, 255], [241, 241, 241], [149, 149, 150], [47, 47, 49], [130, 130, 131], [237, 237, 237], [255, 255, 255], [201, 201, 201], [78, 78, 79], [48, 48, 50], [183, 183, 183], [253, 253, 253], [254, 254, 254], [213, 213, 214], [49, 49, 51], [76, 76, 78], [197, 197, 198], [255, 255, 255], [252, 252, 252], [155, 155, 156], [54, 54, 56], [47, 47, 49], [47, 47, 49], [47, 47, 49], [58, 58, 60], [220, 220, 220], [254, 254, 254], [253, 253, 253], [174, 174, 174], [48, 48, 50], [47, 47, 49], [48, 48, 50], [103, 103, 104], [221, 221, 221], [255, 255, 255], [252, 252, 252], [148, 148, 149], [60, 60, 62], [47, 47, 49], [47, 47, 49], [70, 70, 72], [249, 249, 249], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [209, 209, 209], [94, 94, 95], [50, 50, 52], [47, 47, 49], [48, 48, 50], [92, 92, 93], [255, 255, 255], [255, 255, 255], [235, 235, 235], [136, 136, 137], [47, 47, 49], [47, 47, 49], [47, 47, 49]]
            
            x = 579
            x1 = 679
            y =  230
            for i in range(x, x1):
                if image[y][i][0] != arr[i - x][0] or image[y][i][1] != arr[i - x][1] or image[y][i][2] != arr[i - x][2]:
                    res3 = False
                    break
            print(res, res2, res3)
            
            return (res or res2) and res3
        except:
            return False

    def capture_image(self):
        print("DEBUG === CAPTURE IMAGE")
        cmd = 'memuc adb -i {} "shell screencap -p /sdcard/Download/screen{}.png"'.format(self.threadID, self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def start_check(self):
        self.set_match_is_done(False)
        self.process_running = True

    def stop_check(self):
        self.process_running = False

    def set_match_is_done(self, value):
        self.match_is_done = value