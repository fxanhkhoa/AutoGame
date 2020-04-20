import threading
import time
import subprocess
import os
import cv2
import numpy as np
from ultility.check_match_done import check_match_done

class memu_process_class (threading.Thread):
    
    process_running = True
    flag_exist_GET_MORE = False

    def __init__(self, threadID, pic_folder):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.pic_folder = pic_folder
        self.try_count = 0
        self.try_count_when_auto_hit = 0

        self.mode_arena = 2

        self.check_match_done_thread = check_match_done(threadID, pic_folder)
        self.check_match_done_thread.start()
    
    def run(self):
        while (self.process_running):
            if self.mode_arena == -2:
                self.mode_arena = 2
            print("DEBUG === MODE ARENA", self.mode_arena)
            self.try_count = 0
            # 1st time for open connect
            self.go_to_home()
            if not self.process_running:
                return
            ######### Opened
            self.go_to_home()
            if not self.process_running:
                return
            
            while not self.check_FIGHT_BUTTON():
                self.try_count = self.try_count + 1
                if (self.try_count > 7):
                    break
                if not self.process_running:
                    return

            self.go_to_fight()
            if not self.process_running:
                return

            while not self.check_PLAY_ARENA():
                self.try_count = self.try_count + 1
                if (self.try_count > 7):
                    break
                if not self.process_running:
                    return

            self.go_to_arena()
            if not self.process_running:
                return
            #### PART GO TO ARENA WITH MODE
            while not self.check_MULTIVERSE_ARENAS():
                self.try_count = self.try_count + 1
                if (self.try_count > 7):
                    break
                if not self.process_running:
                    return

            if (self.mode_arena == -1):
                self.click_continue_arena_3vs_3_3star()
                if not self.process_running:
                    return
            else:
                for i in range(0, self.mode_arena):
                    self.swipe_to_another_arena_mode()
                    self.swipe_to_another_arena_mode()
                time.sleep(1)
                self.click_continue_arena_3vs_3_3star()
                if not self.process_running:
                    return


            #### END ####

            self.check_GET_MORE()
            if not self.process_running:
                return
            
            while (self.check_GET_HELP_and_CLICK()):
                self.try_count = self.try_count + 1
                if (self.try_count > 7):
                    break
                if not self.process_running:
                    return
                time.sleep(0.5)

            while (not self.check_FIND_MATCH()):
                self.try_count = self.try_count + 1
                if (self.try_count > 7):
                    break
                self.pick_hero()
                if not self.process_running:
                    return
            
            self.click_find_match()
            if not self.process_running:
                return

            time.sleep(2)

            while (not self.check_CONTINUE()):
                self.try_count = self.try_count + 1
                if (self.try_count > 10):
                    break
                if not self.process_running:
                    return

            self.click_CONTINUE()
            if not self.process_running:
                return
            time.sleep(2)

            while (not self.check_ACCEPT):
                self.try_count = self.try_count + 1
                if (self.try_count > 10):
                    break
                if not self.process_running:
                    return

            self.click_ACCEPT()
            if not self.process_running:
                return
            time.sleep(2)

            while (not self.check_CONTINUE()):
                self.try_count = self.try_count + 1
                if (self.try_count > 10):
                    break
                if not self.process_running:
                    return

            self.click_CONTINUE()
            if not self.process_running:
                return
            time.sleep(2)

            # # 1st FIGHT
            # print("DEBUG === 1st FIGHT")
            # while (not self.check_VIEW_MATCHUP()):
            #     self.auto_hit()
            #     self.click_NEXT_SERIES()
            #     if not self.process_running:
            #         return
            
            # self.click_NEXT_FIGHT()
            # if not self.process_running:
            #     return

            # # 2nd FIGHT
            # print("DEBUG === 2nd FIGHT")
            # while (not self.check_VIEW_MATCHUP()):
            #     self.auto_hit()
            #     self.click_NEXT_SERIES()
            #     if not self.process_running:
            #         return

            # self.click_NEXT_FIGHT()
            # if not self.process_running:
            #     return

            # 3rd FIGHT ===> Some case stuck here because of cannot click next match
            if self.try_count < 7:
                self.try_count_when_auto_hit = 0
                print("DEBUG === 3rd FIGHT")
                self.check_match_done_thread.start_check()
                while (not self.check_match_done_thread.get_done_status()):
                    print(self.check_match_done_thread.get_done_status())
                    self.auto_hit()
                    self.click_NEXT_FIGHT()
                    self.try_count = self.try_count_when_auto_hit + 1
                    print("Try:", self.try_count_when_auto_hit)
                    if (self.try_count > 30):
                        break
                    if not self.process_running:
                        return
                
                time.sleep(1)
                self.click_NEXT_SERIES()
                if not self.process_running:
                    return

                self.click_claim_achive()
                time.sleep(1)
                
                time.sleep(1)
                self.click_CONTINUE()
                if not self.process_running:
                    return
            
            time.sleep(3)
            self.check_match_done_thread.stop_check()
            if self.try_count > 7:
                self.mode_arena = self.mode_arena - 1


    def stop_thread(self):
        self.process_running = False
        self.check_match_done_thread.stop_check()

    def go_to_home(self):
        if (self.try_count > 7):
            return
        print("DEBUG === GO TO HOME")
        # Click Menu Button
        cmd = 'memuc adb -i {} "shell input tap 250 50"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        time.sleep(3)

        # Click Home
        cmd = 'memuc adb -i {} "shell input tap 200 200"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(3)
    
    def go_to_fight(self):
        if (self.try_count > 7):
            return
        print("DEBUG === GO TO FIGHT")
        cmd = 'memuc adb -i {} "shell input tap 400 200"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(3)

    def go_to_arena(self):
        if (self.try_count > 7):
            return
        print("DEBUG === GO TO ARENA")
        cmd = 'memuc adb -i {} "shell input tap 625 576"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(4)

    def click_continue_arena_3vs_3_3star(self):
        if (self.try_count > 7):
            return
        print("DEBUG === CONTINUE TO ARENA")
        cmd = 'memuc adb -i {} "shell input tap 400 631"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(3)

    def check_GET_MORE(self):
        if (self.try_count > 7):
            return
        print("DEBUG === CHECK GET MORE")
        try:
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
        except:
            return False


    def check_GET_HELP_and_CLICK(self):
        print("DEBUG === CHECK GET HELP")
        try:
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            # arr = [[ 6, 99,  4], [  6, 100,   5], [  6, 101,   6], [  6, 102,   8], [  6, 103,  11], [  6, 105,  14], [  6, 106,  17], [  6, 108,  20], [  6, 111,  22], [  6, 112,  25]]

            res1 = True

            # x = 341
            # x1 = 351
            # y = 312
            

            # for i in range(x, x1):
            #     # print(image[y][i], arr[i - x])
            #     if image[y][i][0] != arr[i - x][0] or image[y][i][1] != arr[i - x][1] or image[y][i][2] != arr[i - x][2]:
            #         print(image[y][i], arr[i - x])
            #         res1 = False
            #         break
            
            print(image[291][348])
            if image[291][348][0] in range(241, 245) or image[291][348][1] in range(248, 251) or image[291][348][2] in range(245, 247):
                res1 = True
            else:
                res1 = False
            print(res1)

            # arr = [[  6, 103,  10], [  6, 104,  13], [  6, 106,  16], [  6, 108,  19], [  6, 110,  22], [  6, 112,  24], [  6, 113,  26], [  5, 115,  28], [  5, 116,  30], [  5, 117,  31]]

            res2 = True

            # x = 566
            # x1 = 576
            # y = 312

            # for i in range(x, x1):
            #     # print(image[y][i], arr[i - x])
            #     if image[y][i][0] != arr[i - x][0] or image[y][i][1] != arr[i - x][1] or image[y][i][2] != arr[i - x][2]:
            #         print(image[y][i], arr[i - x])
            #         res2 = False
            #         break

            print(image[291][570])
            if image[291][570][0] in range(241, 245) or image[291][570][1] in range(248, 251) or image[291][570][2] in range(245, 247):
                res2 = True
            else:
                res2 = False
            print(res2)

            if res1 and res2:
                cmd = 'memuc adb -i {} "shell input tap 351 300"'.format(self.threadID)
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                retval = p.wait()
                time.sleep(1)

                cmd = 'memuc adb -i {} "shell input tap 351 300"'.format(self.threadID)
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                retval = p.wait()
                time.sleep(1)
            
            if not res1 and res2:
                cmd = 'memuc adb -i {} "shell input tap 351 300"'.format(self.threadID)
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                retval = p.wait()
                time.sleep(1)
            
            if res1 and not res2:
                cmd = 'memuc adb -i {} "shell input tap 351 300"'.format(self.threadID)
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                retval = p.wait()
                time.sleep(1)

            return res1 or res2
        except Exception as ex:
            print(ex)
            return False

    def pick_hero(self):
        if (self.try_count > 10):
            return
        print("DEBUG === PICK HERO")
        if self.flag_exist_GET_MORE:
            cmd = 'memuc adb -i {} "shell input swipe 655 357 191 129"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            
            cmd = 'memuc adb -i {} "shell input swipe 655 357 185 233"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            cmd = 'memuc adb -i {} "shell input swipe 655 357 184 337"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
        else:
            cmd = 'memuc adb -i {} "shell input swipe 437 342 191 129"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            
            cmd = 'memuc adb -i {} "shell input swipe 437 342 185 233"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            cmd = 'memuc adb -i {} "shell input swipe 437 342 184 337"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

    def check_FIND_MATCH(self):
        print("DEBUG === CHECK FIND MATCH")
        try:
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            res = True
            
            arr = [[ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3]]

            x = 34
            x1 = 64
            y = 685

            for i in range(x, x1):
                if image[y][i][0] != arr[i - x][0] or image[y][i][1] != arr[i - x][1] or image[y][i][2] != arr[i - x][2]:
                    res = False
                    break

            return res
        except:
            return False

    def click_find_match(self):
        if (self.try_count > 7):
            return
        print("DEBUG === CLICK FIND MATCH")
        time.sleep(2)
        cmd = 'memuc adb -i {} "shell input tap 121 669"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def check_CONTINUE(self):
        print("DEBUG === CHECK CONTINUE")
        try:
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            res = True

            arr = [[ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3]]

            x = 1136
            x1 = 1186
            y =  696
            for i in range(x, x1):
                if image[y][i][0] != arr[i - x][0] or image[y][i][1] != arr[i - x][1] or image[y][i][2] != arr[i - x][2]:
                    res = False
                    break
            
            # print(res)

            arr = [[ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3]]

            res2 = True
            x = 854
            x1 = 904
            y =  695
            for i in range(x, x1):
                if image[y][i][0] != arr[i - x][0] or image[y][i][1] != arr[i - x][1] or image[y][i][2] != arr[i - x][2]:
                    res2 = False
                    break


            return res or res2
        except:
            return False

    def click_CONTINUE(self):
        if (self.try_count > 7):
            return
        print("DEBUG === CLICK CONTINUE")
        time.sleep(2)
        cmd = 'memuc adb -i {} "shell input tap 1170 678"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def check_ACCEPT(self):
        print("DEBUG === CHECK ACCEPT")
        try:
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            res = True
            arr = [[ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3]]

            x = 1073
            x1 = 1123
            y = 696

            for i in range(x, x1):
                if image[y][i][0] != arr[i - x][0] or image[y][i][1] != arr[i - x][1] or image[y][i][2] != arr[i - x][2]:
                    res = False
                    break
            
            return res
        except:
            return False

    def click_ACCEPT(self):
        if (self.try_count > 7):
            return
        print("DEBUG === CLICK ACCEPT")
        time.sleep(2)
        cmd = 'memuc adb -i {} "shell input tap 1127 678"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def auto_hit(self):
        if (self.try_count_when_auto_hit > 30):
            return
        print("DEBUG === AUTO HIT")
        for i in range(0, 2):
            cmd = 'memuc execcmd -i {} "input swipe 800 300 1000 300"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            cmd = 'memuc execcmd -i {} "input swipe 500 300 300 300"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            cmd = 'memuc execcmd -i {} "input swipe 800 300 1000 300"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            # 5 hit

            cmd = 'memuc execcmd -i {} "input tap 800 300"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            
            cmd = 'memuc execcmd -i {} "input tap 900 300"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            
            cmd = 'memuc execcmd -i {} "input tap 800 300"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            
            cmd = 'memuc execcmd -i {} "input tap 900 300"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            
            cmd = 'memuc execcmd -i {} "input tap 800 300"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            
            ###

            cmd = 'memuc execcmd -i {} "input swipe 500 300 300 300"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            cmd = 'memuc execcmd -i {} "input swipe 800 300 1000 300"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            # 5 hit

            cmd = 'memuc execcmd -i {} "input tap 800 300"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            
            cmd = 'memuc execcmd -i {} "input tap 900 300"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            
            cmd = 'memuc execcmd -i {} "input tap 800 300"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            
            cmd = 'memuc execcmd -i {} "input tap 900 300"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            
            cmd = 'memuc execcmd -i {} "input tap 800 300"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            ### Skill

            cmd = 'memuc execcmd -i {} "input tap 200 650"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # retval = p.wait()

            cmd = 'memuc execcmd -i {} "input tap 200 650"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # retval = p.wait()

            cmd = 'memuc execcmd -i {} "input tap 200 650"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # retval = p.wait()

    def check_VIEW_MATCHUP(self):
        print("DEBUG === CHECK MATCHUP")
        try:
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            res1 = True

            arr = [[ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3]]

            x = 455
            x1 = 505
            y = 584

            for i in range(x, x1):
                if image[y][i][0] != arr[i - x][0] or image[y][i][1] != arr[i - x][1] or image[y][i][2] != arr[i - x][2]:
                    res1 = False
                    break

            res2 = True

            arr = [[ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3]]

            x = 455
            x1 = 505
            y = 472

            for i in range(x, x1):
                if image[y][i][0] != arr[i - x][0] or image[y][i][1] != arr[i - x][1] or image[y][i][2] != arr[i - x][2]:
                    res2 = False
                    break
            print(res1, res2)
            return res1 or res2
        except:
            return False

    def click_NEXT_FIGHT(self):
        if (self.try_count_when_auto_hit > 30):
            return
        print("DEBUG === CLICK NEXT FIGHT")
        # time.sleep(2)

        cmd = 'memuc adb -i {} "shell input tap 770 565"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        cmd = 'memuc adb -i {} "shell input tap 770 454"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        # time.sleep(2)

    def click_NEXT_SERIES(self):
        if (self.try_count_when_auto_hit > 30):
            return
        print("DEBUG === CLICK NEXT SERIES")
        cmd = 'memuc adb -i {} "shell input tap 948 680"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def check_FIGHT_BUTTON(self):
        print("DEBUG === CHECK FIGHT BUTTON")
        try:
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))

            arr = [[ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6]]

            res = True

            x = 328
            x1 = 378
            y = 147

            for i in range(x, x1):
                if image[y][i][0] != arr[i - x][0] or image[y][i][1] != arr[i - x][1] or image[y][i][2] != arr[i - x][2]:
                    res = False
                    break
            print(res)
            return res
        except:
            return False

    def check_PLAY_ARENA(self):
        print("DEBUG === check_PLAY_ARENA")
        try:
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2]]

            res = True

            x = 558
            x1 = 608
            y = 596

            for i in range(x, x1):
                if image[y][i][0] != arr[i - x][0] or image[y][i][1] != arr[i - x][1] or image[y][i][2] != arr[i - x][2]:
                    res = False
                    break
            
            return res
        except:
            return False

    def check_MULTIVERSE_ARENAS(self):
        print("DEBUG === check_MULTIVERSE_ARENAS")
        try:
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))

            arr = [[176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45]]

            res = True

            x = 422
            x1 = 472
            y = 123

            for i in range(x, x1):
                if image[y][i][0] != arr[i - x][0] or image[y][i][1] != arr[i - x][1] or image[y][i][2] != arr[i - x][2]:
                    res = False
                    break
            
            return res
        except:
            return False

    def check_achived(self):
        arr = [[  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0]]

    def click_claim_achive(self):
        if (self.try_count_when_auto_hit > 30):
            return
        print("DEBUG === click_claim_achive")
        cmd = 'memuc execcmd -i {} "input tap 892 407"'.format(self.threadID, self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def swipe_to_another_arena_mode(self):
        if (self.try_count > 7):
            return
        # Swipe to make 3vs3
        print("DEBUG === swipe_to_another_arena_mode")
        cmd = 'memuc execcmd -i {} "input swipe 500 500 250 500"'.format(self.threadID, self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        print("DEBUG === swipe_to_another_arena_mode")
        cmd = 'memuc execcmd -i {} "input swipe 500 500 250 500"'.format(self.threadID, self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def capture_image(self):
        print("DEBUG === CAPTURE IMAGE")
        cmd = 'memuc execcmd -i {} "screencap -p /sdcard/Download/screen{}.png"'.format(self.threadID, self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()