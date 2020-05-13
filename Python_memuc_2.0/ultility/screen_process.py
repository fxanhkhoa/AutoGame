import threading
import time
import subprocess
import os
import cv2
import numpy as np

class screen_process_class (threading.Thread):

    process_running = True
    running = False
    mode = ''
    flag_exist_GET_MORE = False
    flag_button_is_green = False
    check_capture_done = False

    @staticmethod
    def stop_thread():
        screen_process_class.process_running = False

    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
    
    def run(self):
        while (self.process_running):
            if (self.running):
                print("RUN THREAD", self.mode)
                p = subprocess.Popen("adb exec-out screencap -p", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                image_bytes = p.stdout.read().replace(b'\r\n', b'\n')
                nparr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                cv2.imwrite("currentIMG.png", image)
                # cv2.imshow("screen", image)
                # cv2.waitKey(0)
                # cv2.destroyWindow("")
                retval = p.wait()
                if (self.mode == ''):
                    pass
                elif (self.mode == 'CHECK_GET_MORE'):
                    mode = ''

                    # hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

                    # lower = np.uint8([60, 255, 92])
                    # upper = np.uint8([64, 255, 239])

                    # green_mask = cv2.inRange(hsv, lower, upper)
                    # result = cv2.bitwise_and(image, image, mask = green_mask)
                    # image in OpenCV x, y is swap, so to call x y need to write y x in code
                    for i in range(367, 504):
                        print(image[422][i])
                        if image[422][i][0] in range(25, 29) or image[422][i][1] in range(21, 26) or image[422][i][2] in range(21, 27):
                            self.flag_exist_GET_MORE = True
                            break

                    # cv2.imshow("screen", result)
                    # cv2.waitKey(0)
                    # cv2.destroyWindow("")
                    self.stop_process()
                elif (self.mode == 'CHECK_FIND_MATCH_IS_GREEN'):
                    mode = ''
                    flag_temp = False
                    for i in range(54, 180):
                        print(image[684][i])
                        if image[684][i][0] in range(1, 2) or image[684][i][1] in range(73, 76) or image[684][i][2] in range(2, 4):
                            flag_temp = True
                            break
                    if flag_temp:
                        self.flag_button_is_green = True
                    else:
                        self.flag_button_is_green = False
                    
                    self.check_capture_done = True
                    self.stop_process()
                elif (self.mode == 'CHECK_CONTINUE_IS_GREEN'):
                    mode = ''
                    
                    if (self.check_pattern_continue(image)):
                        self.flag_button_is_green = True
                    else: 
                        self.flag_button_is_green = False
                    
                    self.stop_process()
                elif (self.mode == 'CHECK_ACCEPT_IS_GREEN'):
                    mode = ''
                    
                    for i in range(1066, 1180):
                        print(image[694][i])
                        if image[694][i][0] in range(1, 2) or image[694][i][1] in range(73, 76) or image[694][i][2] in range(2, 4):
                            self.flag_button_is_green = True
                            break
                    
                    self.stop_process()
                elif (self.mode == 'CHECK_NEXT_FIGHT_IS_GREEN'):
                    mode = ''
                    if (self.check_pattern_view_matchup(image)):
                        self.flag_button_is_green = True
                    else:
                        self.flag_button_is_green = False
                    
                    self.stop_process()
                elif (self.mode == 'CHECK_HELP_IS_EXISTED'):
                    mode = ''
                    flag_temp = False
                    if (self.flag_exist_GET_MORE):
                        for i in range(562, 597):
                            print(image[99][i])
                            if image[99][i][0] in range(5, 8) or image[99][i][1] in range(98, 100) or image[99][i][2] in range(2, 5):
                                flag_temp = True
                                break
                    else:
                        for i in range(339, 384):
                            print(image[258][i])
                            if image[258][i][0] in range(5, 8) or image[258][i][1] in range(98, 100) or image[258][i][2] in range(2, 5):
                                flag_temp = True
                                break
                    if (flag_temp):
                        self.flag_button_is_green = True
                    else:
                        self.flag_button_is_green = False

                    self.stop_process()
                else:
                    pass



    def go_to_arena(self):
        # Click Menu Button
        p = subprocess.Popen("adb exec-out input tap 250 50", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(1.5)

        # Click Home
        p = subprocess.Popen("adb exec-out input tap 200 200", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(2)
        
        # Click Fight
        p = subprocess.Popen("adb exec-out input tap 400 200", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(2)

        # Click Arena
        p = subprocess.Popen("adb exec-out input tap 625 576", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(4)

    def go_to_arena_3_vs_3_and_fight(self):
        print("Execute function go_to_arena_3_vs_3")

        # Click Continue
        p = subprocess.Popen("adb exec-out input tap 400 631", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        # Check 1st position is hero or not
        self.mode = 'CHECK_GET_MORE'
        self.flag_exist_GET_MORE = False
        self.start_process()
        while self.running:
            pass

        # Check if need help Exist
        self.flag_button_is_green = False
        self.mode = 'CHECK_HELP_IS_EXISTED'
        self.start_process()

        while (self.flag_button_is_green):
            # Click Help
            if (self.flag_exist_GET_MORE):
                p = subprocess.Popen("adb exec-out input tap 582 279", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            else:
                p = subprocess.Popen("adb exec-out input tap 358 279", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            self.mode = 'CHECK_HELP_IS_EXISTED'
            self.start_process()

        # Check Find match is green
        self.flag_button_is_green = False
        while (not self.flag_button_is_green):
            # Pick 3 heros
            self.mode = 'CHECK_FIND_MATCH_IS_GREEN'
            self.start_process()
            if (self.check_capture_done):
                self.get_hero()
                self.check_capture_done = False
            time.sleep(1)
        
        # Click Find Match
        time.sleep(2)
        p = subprocess.Popen("adb exec-out input tap 121 669", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        # Check Continue is green
        self.flag_button_is_green = False
        while (not self.flag_button_is_green):
            self.mode = 'CHECK_CONTINUE_IS_GREEN'
            self.start_process()
            time.sleep(2)

        # Click Continue
        time.sleep(2)
        print("Click Continue")
        p = subprocess.Popen("adb exec-out input tap 1170 678", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        # Check Accept is green
        self.flag_button_is_green = False
        while (not self.flag_button_is_green):
            self.mode = 'CHECK_ACCEPT_IS_GREEN'
            self.start_process()
            time.sleep(2)

        # Click Accept
        time.sleep(2)
        print("Click Accept")
        p = subprocess.Popen("adb exec-out input tap 1127 678", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        # Check Continue is green
        self.flag_button_is_green = False
        while (not self.flag_button_is_green):
            self.mode = 'CHECK_CONTINUE_IS_GREEN'
            self.start_process()
            time.sleep(2)

        # Click Continue
        time.sleep(2)
        print("Click Continue")
        p = subprocess.Popen("adb exec-out input tap 1170 678", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        # Check Next Fight is green
        print("1ST FIGHT")
        self.flag_button_is_green = False
        while (not self.flag_button_is_green):
            # auto hit
            self.auto_hit()
            self.mode = 'CHECK_NEXT_FIGHT_IS_GREEN'
            self.start_process()

        # Click Next Fight
        time.sleep(2)
        p = subprocess.Popen("adb exec-out input tap 770 565", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        p = subprocess.Popen("adb exec-out input tap 770 454", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(2)

        # Check Final Fight is green
        print("2ND FIGHT")
        self.flag_button_is_green = False
        while (not self.flag_button_is_green):
            # auto hit
            self.auto_hit()
            self.mode = 'CHECK_NEXT_FIGHT_IS_GREEN'
            self.start_process()

        # Click Final Fight
        time.sleep(2)
        p = subprocess.Popen("adb exec-out input tap 770 565", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        p = subprocess.Popen("adb exec-out input tap 770 454", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(2)

        # Check Continue is green
        print("3RD FIGHT")
        self.flag_button_is_green = False
        while (not self.flag_button_is_green):
            # auto hit
            self.auto_hit()
            self.mode = 'CHECK_CONTINUE_IS_GREEN'
            self.start_process()

        # Click Next Series Fight
        p = subprocess.Popen("adb exec-out input tap 948 680", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def get_hero(self):
        # GET MORE Exist
        if (self.flag_exist_GET_MORE):
            # swipe hero 1
            p = subprocess.Popen("adb exec-out input swipe 655 357 191 129", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            # swipe hero 2
            p = subprocess.Popen("adb exec-out input swipe 655 357 185 233", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            # swipe hero 3
            p = subprocess.Popen("adb exec-out input swipe 655 357 184 337", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

        else :
            # swipe hero 1
            p = subprocess.Popen("adb exec-out input swipe 437 342 191 129", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            # swipe hero 2
            p = subprocess.Popen("adb exec-out input swipe 437 342 185 233", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            # swipe hero 3
            p = subprocess.Popen("adb exec-out input swipe 437 342 184 337", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()



    def auto_hit(self):
        # for i in range(0,0):
        p = subprocess.Popen('adb exec-out input swipe 800 300 1000 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        
        p = subprocess.Popen('adb exec-out input swipe 500 300 300 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        p = subprocess.Popen('adb exec-out input swipe 800 300 1000 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        p = subprocess.Popen('adb exec-out input tap 800 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        p = subprocess.Popen('adb exec-out input tap 800 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        p = subprocess.Popen('adb exec-out input tap 800 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        p = subprocess.Popen('adb exec-out input tap 800 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        p = subprocess.Popen('adb exec-out input tap 800 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        p = subprocess.Popen('adb exec-out input tap 800 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        p = subprocess.Popen('adb exec-out input tap 800 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        p = subprocess.Popen('adb exec-out input tap 800 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        p = subprocess.Popen('adb exec-out input swipe 500 300 300 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        p = subprocess.Popen('adb exec-out input swipe 800 300 1000 300', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        p = subprocess.Popen('adb exec-out input tap 200 650', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        p = subprocess.Popen('adb exec-out input tap 200 650', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        p = subprocess.Popen('adb exec-out input tap 200 650', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def check_pattern_view_matchup(self, image):

        res1 = True
        res2 = True

        arr = [[ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3]]

        for i in range(455, 505):
            if image[584][i][0] != arr[i - 455][0] or image[584][i][1] != arr[i - 455][1] or image[584][i][2] != arr[i - 455][2]:
                res1 = False
                break
        
        arr2 = [[ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3]]

        for i in range(455, 505):
            if image[472][i][0] != arr[i - 455][0] or image[472][i][1] != arr[i - 455][1] or image[472][i][2] != arr[i - 455][2]:
                res2 = False
                break

        print(res1, res2)
        return res1 or res2

    def check_pattern_continue(self, image):
        try:
            res = True

            arr = [[ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3]]

            #473
            for i in range(1136, 1186):
                if image[696][i][0] != arr[i - 1136][0] or image[696][i][1] != arr[i - 1136][1] or image[696][i][2] != arr[i - 1136][2]:
                    res = False
                    break
            
            print(res)
            return res
        except:
            return False

    def start_process(self):
        self.running = True

    def stop_process(self):
        self.mode = ''
        self.running = False