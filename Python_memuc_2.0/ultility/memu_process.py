import threading
import time
import subprocess
import os
import cv2
import numpy as np
from ultility.check_match_done import check_match_done
from ultility.vm_management import vm_manage

class memu_process_class (threading.Thread):
    
    process_running = True
    flag_exist_GET_MORE = False

    def __init__(self, threadID, pic_folder, log_file, num_of_mode):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.pic_folder = pic_folder
        self.log_file = log_file
        self.try_count = 0
        self.try_count_when_auto_hit = 0

        self.num_of_mode = num_of_mode
        self.mode_arena = num_of_mode

        self.start_time = time.time()
        self.start_time_reset = time.time()

        self.check_match_done_thread = check_match_done(threadID, pic_folder)
        self.check_match_done_thread.start()
    
    def run(self):
        while self.process_running:

            if time.time() - self.start_time > 3600:
                self.start_time = time.time()
                vm_manage.stop_vm(self.threadID)
                time.sleep(2)
                vm_manage.start_vm(self.threadID)
                time.sleep(2)
                vm_manage.start_app(self.threadID)
                time.sleep(2)

            if (self.mode_arena < 0):
                self.mode_arena = self.num_of_mode

            if not self.process_running:
                return
            elif self.check_IN_FIGHTING():
                self.try_count_when_auto_hit = 0
                while self.try_count_when_auto_hit < 15 and not self.check_CONTINUE():
                    self.click_NEXT_FIGHT()
                    self.auto_hit()
                    self.try_count_when_auto_hit = self.try_count_when_auto_hit + 1
                if self.try_count_when_auto_hit < 15:
                    self.click_NEXT_SERIES()
            elif self.check_FIGHT_RECOVER():
                self.click_FIGHT_RECOVER()
            elif self.check_TODAY_REWARD():
                self.click_X_TODAY_REWARD()
            elif self.check_INCURSIONS():
                self.click_X_INCURSION()
            elif self.check_FIGHT_BUTTON():
                self.go_to_fight()
            elif self.check_PLAY_ARENA():
                self.go_to_arena()
            elif self.check_MULTIVERSE_ARENAS():
                for i in range(self.mode_arena):
                    self.swipe_to_another_arena_mode()
                time.sleep(1)
                if (self.mode_arena == self.num_of_mode):
                    self.click_continue_arena_on_right()
                else:
                    self.click_continue_arena_3vs_3_3star()
            elif self.check_WARNING():
                self.go_to_home()
                time.sleep(2)
                self.go_to_home()
                self.mode_arena = self.mode_arena - 1
            elif self.check_in_PICKING_PHASE():
                while self.check_GET_HELP_and_CLICK():
                    pass
                if self.check_GET_MORE():
                    self.flag_exist_GET_MORE = True
                elif not self.check_GET_MORE():
                    self.flag_exist_GET_MORE = False
                if not self.check_FIND_MATCH():
                    self.pick_hero()
                    time.sleep(1)
                elif self.check_FIND_MATCH():
                    self.click_find_match()
                elif self.check_NO_MORE_HEROS():
                    self.mode_arena = self.mode_arena - 1
                    self.go_to_home()
            elif self.check_CONTINUE():
                self.click_CONTINUE()
            elif self.check_ACCEPT():
                self.click_ACCEPT()
            else:
                self.go_to_home()
                
            


    def stop_thread(self):
        self.process_running = False
        self.check_match_done_thread.stop_check()

    def go_to_home(self):
        if (self.try_count > 7):
            return
        print("DEBUG === GO TO HOME {}".format(self.threadID))
        # Click Menu Button
        cmd = 'memuc execcmd -i {} "input tap 250 50"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        time.sleep(3)

        # Click Home
        cmd = 'memuc execcmd -i {} "input tap 200 200"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        # time.sleep(3)
    
    def go_to_fight(self):
        if (self.try_count > 7):
            return
        print("DEBUG === GO TO FIGHT {}".format(self.threadID))
        cmd = 'memuc execcmd -i {} "input tap 400 200"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(3)

    def go_to_arena(self):
        if (self.try_count > 7):
            return
        print("DEBUG === GO TO ARENA {}".format(self.threadID))
        cmd = 'memuc execcmd -i {} "input tap 625 576"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(4)

    def click_continue_arena_3vs_3_3star(self):
        if (self.try_count > 7):
            return
        print("DEBUG === CONTINUE TO ARENA {}".format(self.threadID))
        cmd = 'memuc execcmd -i {} "input tap 306 456"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(3)

    def check_GET_MORE(self):
        print("DEBUG === CHECK FIND MATCH")
        try:
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            res = True
            
            arr = [[ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [245, 249, 245], [185, 210, 186], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 27, 109,  28], [252, 253, 252], [147, 186, 148], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [186, 211, 187], [232, 241, 232], [ 27, 109,  28], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1]]

            x = 379
            x1 = 429
            y = 405

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break

            return res
        except:
            return False


    def check_GET_HELP_and_CLICK(self):
        print("DEBUG === CHECK GET HELP {}".format(self.threadID))
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
                cmd = 'memuc execcmd -i {} "input tap 351 300"'.format(self.threadID)
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                retval = p.wait()
                time.sleep(1)

                cmd = 'memuc execcmd -i {} "input tap 351 300"'.format(self.threadID)
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                retval = p.wait()
                time.sleep(1)
            
            if not res1 and res2:
                cmd = 'memuc execcmd -i {} "input tap 351 300"'.format(self.threadID)
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                retval = p.wait()
                time.sleep(1)
            
            if res1 and not res2:
                cmd = 'memuc execcmd -i {} "input tap 351 300"'.format(self.threadID)
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
            cmd = 'memuc execcmd -i {} "input swipe 655 357 191 129"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            
            cmd = 'memuc execcmd -i {} "input swipe 655 357 185 233"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            cmd = 'memuc execcmd -i {} "input swipe 655 357 184 337"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
        else:
            cmd = 'memuc execcmd -i {} "input swipe 437 342 191 129"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            
            cmd = 'memuc execcmd -i {} "input swipe 437 342 185 233"'.format(self.threadID)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            cmd = 'memuc execcmd -i {} "input swipe 437 342 184 337"'.format(self.threadID)
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
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
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
        cmd = 'memuc execcmd -i {} "input tap 121 669"'.format(self.threadID)
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
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            # print(res)

            arr = [[ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3]]

            res2 = True
            x = 854
            x1 = 904
            y =  695
            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
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
        cmd = 'memuc execcmd -i {} "input tap 1170 678"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    
    def click_CONTINUE_without_try(self):
        print("DEBUG === CLICK CONTINUE")
        time.sleep(2)
        cmd = 'memuc execcmd -i {} "input tap 1170 678"'.format(self.threadID)
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
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
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
        cmd = 'memuc execcmd -i {} "input tap 1127 678"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def auto_hit(self):
        if (self.try_count_when_auto_hit > 17):
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
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res1 = False
                    break

            res2 = True

            arr = [[ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3]]

            x = 455
            x1 = 505
            y = 472

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res2 = False
                    break
            print(res1, res2)
            return res1 or res2
        except:
            return False

    def click_NEXT_FIGHT(self):
        if (self.try_count_when_auto_hit > 17):
            return
        print("DEBUG === CLICK NEXT FIGHT")
        # time.sleep(2)

        cmd = 'memuc execcmd -i {} "input tap 770 565"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        cmd = 'memuc execcmd -i {} "input tap 770 454"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        # time.sleep(2)

    def click_NEXT_SERIES(self):
        if (self.try_count_when_auto_hit > 17):
            return
        print("DEBUG === CLICK NEXT SERIES")
        cmd = 'memuc execcmd -i {} "input tap 948 680"'.format(self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def check_FIGHT_BUTTON(self):
        try:
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))

            arr = [[ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6], [ 4, 79,  6]]

            res = True

            x = 328
            x1 = 378
            y = 147

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            # print(res)
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
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
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
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False

    def check_achived(self):
        arr = [[  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0]]

    def click_claim_achive(self):
        if (self.try_count_when_auto_hit > 17):
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

    def check_in_PICKING_PHASE(self):
        try:
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49]]

            res = True

            x = 24
            x1 = 124
            y = 535

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            # print("DEBUG === PICKING PHASE", res)
            return res
        except:
            return False

    def check_REQUIREMENT(self):
        try:
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3], [ 1, 74,  3]]

            res = True

            x = 534
            x1 = 584
            y = 568

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            print("DEBUG === REQUIREMENT ")
            return res
        except:
            return False

    def check_APP_FREZZE(self):
        try:
            self.capture_image()
            pic_1 = cv2.imread(self.pic_folder + "/screen_for_frezze{}.png".format(self.threadID))
            pic_2 = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))

            difference = cv2.subtract(pic_1, pic_2)
            result = not np.any(difference)
            if result:
                return True
            else:
                return False
        except:
            return False

    def check_FIGHT_RECOVER(self):
        try:
            print("DEBUG === check_FIGHT_RECOVER")
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))

            arr = [[255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [254, 254, 254], [215, 215, 216], [47, 47, 49], [47, 47, 49], [109, 109, 111], [233, 233, 233], [255, 255, 255], [255, 255, 255], [227, 227, 227], [96, 96, 98], [47, 47, 49], [71, 71, 72], [237, 237, 237], [255, 255, 255], [255, 255, 255], [250, 250, 250], [177, 177, 178], [47, 47, 49], [47, 47, 49], [66, 66, 68], [167, 167, 168], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [249, 249, 249], [70, 70, 72], [47, 47, 49], [47, 47, 49], [ 99,  99, 101], [233, 233, 233], [255, 255, 255], [255, 255, 255], [255, 255, 255]]

            res = True

            x = 509
            x1 = 559
            y = 161

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break

            return res
        except:
            return False

    def check_WARNING(self):
        try:
            print("DEBUG === check_WARNING")
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))

            arr = [[255, 255, 255], [228, 228, 228], [88, 88, 90], [47, 47, 49], [122, 122, 123], [251, 251, 251], [255, 255, 255], [246, 246, 246], [143, 143, 144], [47, 47, 49], [69, 69, 71], [170, 170, 171], [255, 255, 255], [255, 255, 255], [234, 234, 234], [111, 111, 112], [48, 48, 50], [ 98,  98, 100], [231, 231, 232], [255, 255, 255], [255, 255, 255], [219, 219, 219], [53, 53, 55], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [96, 96, 98], [208, 208, 208], [255, 255, 255], [255, 255, 255], [210, 210, 210], [81, 81, 83], [47, 47, 49], [47, 47, 49], [47, 47, 49], [70, 70, 72], [234, 234, 234], [255, 255, 255], [255, 255, 255], [225, 225, 226], [117, 117, 118], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [168, 168, 169], [247, 247, 247], [255, 255, 255], [255, 255, 255]]

            res = True

            x = 604
            x1 = 654
            y = 114

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break

            return res
        except:
            return False

    def check_TODAY_REWARD(self):
        try:
            print("DEBUG === check_TODAY_REWARD")
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            arr = [[255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [242, 242, 242], [176, 176, 176], [82, 82, 83], [47, 47, 49], [81, 81, 82], [218, 218, 218], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [204, 204, 204], [85, 85, 87], [47, 47, 49], [47, 47, 49], [77, 77, 79], [243, 243, 243], [255, 255, 255], [248, 248, 248], [159, 159, 160], [47, 47, 49], [90, 90, 92], [215, 215, 215], [255, 255, 255], [227, 227, 227], [113, 113, 114], [48, 48, 50], [169, 169, 170], [247, 247, 247], [255, 255, 255], [213, 213, 213], [54, 54, 56], [51, 51, 53]]

            res = True

            x = 636
            x1 = 686
            y = 81

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False

    def check_INCURSIONS(self):
        try:
            print("DEBUG === check_INCURSIONS")
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            arr = [[187, 186, 184], [67, 63, 58], [33, 28, 22], [123, 120, 117], [243, 243, 243], [255, 255, 255], [252, 252, 252], [168, 166, 164], [32, 27, 21], [74, 70, 65], [224, 223, 222], [255, 255, 255], [255, 255, 255], [205, 204, 202], [85, 81, 77], [32, 27, 21], [55, 51, 46], [211, 210, 208], [255, 255, 255], [255, 255, 255], [255, 255, 255], [175, 173, 171], [32, 27, 21], [32, 27, 21], [32, 27, 21], [32, 27, 21], [32, 27, 21], [32, 27, 21], [32, 27, 21], [32, 27, 21], [32, 27, 21], [32, 27, 21], [32, 27, 21], [32, 27, 21], [32, 27, 21], [32, 27, 21], [232, 232, 231], [255, 255, 255], [255, 255, 255], [227, 226, 225], [103, 100,  95], [32, 27, 21], [32, 27, 21], [32, 27, 21], [32, 27, 21], [32, 27, 21], [32, 27, 21], [32, 27, 21], [55, 51, 45], [235, 235, 234]]

            res = True

            x = 469
            x1 = 519
            y = 239

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False
    
    def check_IN_FIGHTING(self):
        try:
            print("DEBUG === check_IN_FIGHTING")
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[ 5, 76,  7], [ 5, 79,  7], [ 6, 80,  7], [ 6, 81,  8], [ 5, 81,  7], [ 6, 82,  7], [ 5, 82,  7], [ 5, 82,  7], [134, 168, 134], [155, 185, 156], [155, 185, 156], [155, 185, 156], [155, 185, 156], [155, 185, 156], [ 5, 82,  7], [ 5, 82,  7], [ 5, 82,  7], [ 5, 81,  7], [ 5, 81,  7], [ 6, 82,  7], [155, 186, 156], [155, 185, 156], [155, 186, 156], [155, 186, 156], [155, 185, 156], [144, 178, 145], [ 6, 81,  7], [ 6, 81,  7], [ 6, 81,  7], [ 5, 81,  7], [ 5, 81,  8], [ 5, 81,  7], [ 6, 79,  7]]

            res = True

            x = 623
            x1 = 656
            y = 36

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False

    def check_NO_MORE_HEROS(self):
        try:
            print("DEBUG === check_IN_FIGHTING")
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[197, 199, 219], [ 65,  71, 168], [ 19,  27, 153], [ 28,  36, 158], [ 27,  36, 158], [ 27,  36, 158], [ 27,  36, 158], [ 27,  36, 158], [ 27,  35, 158], [ 24,  32, 156], [ 76,  82, 173], [208, 209, 222], [239, 239, 234], [231, 231, 231], [231, 231, 231], [231, 231, 231], [235, 235, 233], [218, 218, 226], [114, 119, 186], [ 24,  32, 152], [110, 115, 185]]

            res = True

            x = 790
            x1 = 811
            y = 277

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False

    def click_FIGHT_RECOVER(self):
        if (self.try_count > 7):
            return
        print("DEBUG === click_FIGHT_RECOVER")
        cmd = 'memuc execcmd -i {} "input tap 640 522"'.format(self.threadID, self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def click_X_TODAY_REWARD(self):
        print("DEBUG === click_X")
        cmd = 'memuc execcmd -i {} "input tap 954 84"'.format(self.threadID, self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
    
    def click_X_INCURSION(self):
        print("DEBUG === click_X")
        cmd = 'memuc execcmd -i {} "input tap 883 42"'.format(self.threadID, self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def click_continue_arena_on_right(self):
        print("DEBUG === click_continue_arena_on_right")
        cmd = 'memuc execcmd -i {} "input tap 854 450"'.format(self.threadID, self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def capture_image_for_FREEZE(self):
        print("DEBUG === CAPTURE IMAGE")
        cmd = 'memuc execcmd -i {} "screencap -p /sdcard/Download/screen_for_frezze{}.png"'.format(self.threadID, self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        
    def capture_image(self):
        print("DEBUG === CAPTURE IMAGE")
        cmd = 'memuc execcmd -i {} "screencap -p /sdcard/Download/screen{}.png"'.format(self.threadID, self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()