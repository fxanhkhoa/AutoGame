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

    def __init__(self, threadID, pic_folder, log_file, num_of_mode, device_name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.pic_folder = pic_folder
        self.log_file = log_file
        self.device_name = device_name
        self.try_count = 0
        self.try_count_when_auto_hit = 0

        self.num_of_mode = num_of_mode
        self.mode_arena = num_of_mode

        self.start_time = time.time()
        self.start_time_reset = time.time()

        # connect with emulator
        print("DEBUG === Connect to {}".format(self.device_name))
        cmd = 'nox_adb.exe connect {}"'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()

        self.check_match_done_thread = check_match_done(threadID, pic_folder)
        self.check_match_done_thread.start()
    
    def run(self):

        # Launch AR once
        # vm_manage.open_AR(self.threadID)
        # time.sleep(90)
        # vm_manage.close_AR(self.threadID)
        # time.sleep(40)
        # vm_manage.start_app(self.threadID)
        # while not self.check_TODAY_REWARD() and not self.check_FIGHT_BUTTON() and not self.check_FIGHT_RECOVER() and not self.check_INCURSIONS():
        #     self.go_to_home()

        while self.process_running:
            print(self.mode_arena)
            if time.time() - self.start_time > 3600:
                self.start_time = time.time()
                vm_manage.reboot_vm(self.threadID)
                time.sleep(90)
                vm_manage.start_app(self.threadID)
                time.sleep(2)

            if self.mode_arena < 0:
                self.mode_arena = self.num_of_mode

            if not self.process_running:
                return
            elif self.check_IN_FIGHTING() or self.check_NEXT_FIGHT():
                self.try_count_when_auto_hit = 0
                while not self.check_CONTINUE():
                    self.click_NEXT_FIGHT()
                    # self.auto_hit()
                    self.try_count_when_auto_hit = self.try_count_when_auto_hit + 1
                    if self.try_count_when_auto_hit > 40:
                        self.go_to_home()
                        break
                # if self.try_count_when_auto_hit < 15:
                self.click_NEXT_SERIES()
            elif self.check_RECONNECT():
                self.start_time = time.time() + 3601
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
            elif self.check_IN_CRYSTAL():
                self.mode_arena = self.mode_arena - 1
                self.go_to_home()
            elif self.check_MULTIVERSE_ARENAS():
                for i in range(self.mode_arena):
                    self.swipe_to_another_arena_mode()
                time.sleep(1)
                if (self.mode_arena == self.num_of_mode):
                    self.click_continue_arena_on_right()
                elif self.mode_arena == 0:
                    self.execute_cmd_swipe(500, 500, 400, 500)
                    self.click_continue_arena_3vs_3_3star()
                else:
                    self.click_continue_arena_3vs_3_3star()
                self.try_count = self.try_count + 1
                if (self.try_count > 2):
                    self.go_to_home()
                    self.mode_arena = self.mode_arena - 1
                    self.try_count = 0
                else:
                    self.try_count = 0
            elif self.check_WARNING():
                self.execute_cmd_tap(250, 50)
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
                if self.check_NO_MORE_HEROS() and self.check_FIND_MATCH():
                    self.click_find_match()
                elif self.check_NO_MORE_HEROS() and not self.check_FIND_MATCH():
                    self.mode_arena = self.mode_arena - 1
                    self.go_to_home() 
                elif not self.check_FIND_MATCH():
                    self.pick_hero()
                    self.try_count = self.try_count + 1
                    if self.try_count > 5:
                        self.mode_arena = self.mode_arena - 1
                        self.execute_cmd_tap(250, 50)
                        self.go_to_home()
                        self.try_count = 0
                    time.sleep(1)
                elif self.check_FIND_MATCH():
                    self.click_find_match()
            elif self.check_NEXT_FIGHT():
                self.click_NEXT_FIGHT()
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
        print("DEBUG === GO TO HOME {}".format(self.device_name))
        # Click Menu Button
        cmd = 'nox_adb.exe -s {} shell input tap 250 50'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
        time.sleep(3)

        # Click Home
        cmd = 'nox_adb.exe -s {} shell input tap 200 200'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        # time.sleep(3)
    
    def go_to_fight(self):
        if (self.try_count > 7):
            return
        print("DEBUG === GO TO FIGHT {}".format(self.device_name))
        cmd = 'nox_adb.exe -s {} shell input tap 400 200'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(3)

    def go_to_arena(self):
        if (self.try_count > 7):
            return
        print("DEBUG === GO TO ARENA {}".format(self.device_name))
        cmd = 'nox_adb.exe -s {} shell input tap 625 576'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(4)

    def click_continue_arena_3vs_3_3star(self):
        if (self.try_count > 7):
            return
        print("DEBUG === CONTINUE TO ARENA {}".format(self.device_name))
        cmd = 'nox_adb.exe -s {} shell input tap 306 456'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        time.sleep(3)

    def check_GET_MORE(self):
        print("DEBUG === check_GET_MORE")
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
                cmd = 'nox_adb.exe -s {} shell input tap 351 300'.format(self.device_name)
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                retval = p.wait()
                time.sleep(1)

                cmd = 'nox_adb.exe -s {} shell input tap 351 300'.format(self.device_name)
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                retval = p.wait()
                time.sleep(2)
            
            if not res1 and res2:
                cmd = 'nox_adb.exe -s {} shell input tap 351 300'.format(self.device_name)
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                retval = p.wait()
                time.sleep(2)
            
            if res1 and not res2:
                cmd = 'nox_adb.exe -s {} shell input tap 351 300'.format(self.device_name)
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                retval = p.wait()
                time.sleep(2)

            return res1 or res2
        except Exception as ex:
            print(ex)
            return False

    def pick_hero(self):
        if (self.try_count > 10):
            return
        print("DEBUG === PICK HERO")
        if self.flag_exist_GET_MORE:
            cmd = 'nox_adb.exe -s {} shell input swipe 655 357 191 129'.format(self.device_name)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            time.sleep(0.5)
            
            cmd = 'nox_adb.exe -s {} shell input swipe 655 357 185 233'.format(self.device_name)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            time.sleep(0.5)

            cmd = 'nox_adb.exe -s {} shell input swipe 655 357 184 337'.format(self.device_name)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            time.sleep(0.5)
        else:
            cmd = 'nox_adb.exe -s {} shell input swipe 437 342 191 129'.format(self.device_name)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()
            
            cmd = 'nox_adb.exe -s {} shell input swipe 437 342 185 233'.format(self.device_name)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

            cmd = 'nox_adb.exe -s {} shell input swipe 437 342 184 337'.format(self.device_name)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            retval = p.wait()

    def check_FIND_MATCH(self):
        print("DEBUG === check_FIND_MATCH")
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
        cmd = 'nox_adb.exe -s {} shell input tap 121 669'.format(self.device_name)
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
        cmd = 'nox_adb.exe -s {} shell input tap 1170 678'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    
    def click_CONTINUE_without_try(self):
        print("DEBUG === CLICK CONTINUE")
        cmd = 'nox_adb.exe -s {} shell input tap 1170 678'.format(self.device_name)
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
        cmd = 'nox_adb.exe -s {} shell input tap 1127 678'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def auto_hit(self):
        if (self.try_count_when_auto_hit > 17):
            return
        print("DEBUG === AUTO HIT")
        for i in range(0, 2):
            self.execute_cmd_swipe_no_wait(800, 300, 1000, 300)
            self.execute_cmd_swipe_no_wait(800, 300, 1000, 300)
            self.execute_cmd_swipe_no_wait(500, 300, 300, 300)
            self.execute_cmd_swipe_no_wait(500, 300, 300, 300)
            self.execute_cmd_swipe_no_wait(800, 300, 1000, 300)
            self.execute_cmd_swipe_no_wait(800, 300, 1000, 300)
            
            # 5 hit
            self.execute_cmd_tap_no_wait(800,300)
            self.execute_cmd_tap_no_wait(900,300)
            self.execute_cmd_tap_no_wait(800,300)
            self.execute_cmd_tap_no_wait(900,300)
            self.execute_cmd_tap_no_wait(800,300)
            self.execute_cmd_tap_no_wait(800,300)
            self.execute_cmd_tap_no_wait(900,300)
            
            ###
            self.execute_cmd_swipe_no_wait(500, 300, 300, 300)
            self.execute_cmd_swipe_no_wait(500, 300, 300, 300)
            self.execute_cmd_swipe_no_wait(800, 300, 1000, 300)
            self.execute_cmd_swipe_no_wait(800, 300, 1000, 300)

            # 5 hit

            self.execute_cmd_tap_no_wait(800,300)
            self.execute_cmd_tap_no_wait(900,300)
            self.execute_cmd_tap_no_wait(800,300)
            self.execute_cmd_tap_no_wait(900,300)
            self.execute_cmd_tap_no_wait(800,300)
            self.execute_cmd_tap_no_wait(800,300)
            self.execute_cmd_tap_no_wait(900,300)

            ### Skill
            self.execute_cmd_tap(200,650)
            self.execute_cmd_tap(205,645)
            self.execute_cmd_tap(202,652)

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
        print("DEBUG === CLICK NEXT FIGHT")
        # time.sleep(2)

        cmd = 'nox_adb.exe -s {} shell input tap 770 565'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        cmd = 'nox_adb.exe -s {} shell input tap 770 454'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        # time.sleep(2)

    def click_NEXT_SERIES(self):
        print("DEBUG === CLICK NEXT SERIES")
        cmd = 'nox_adb.exe -s {} shell input tap 948 680'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def check_FIGHT_BUTTON(self):
        try:
            print("DEBUG === check_FIGHT_BUTTON")
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

            arr = [[208, 177, 132], [219, 195, 160], [185, 138,  71], [190, 146,  85], [220, 197, 163], [208, 177, 132], [181, 131,  61], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [215, 188, 150], [228, 211, 186], [182, 132,  62], [182, 133,  64], [220, 197, 164], [215, 189, 151], [178, 127,  52], [175, 122,  45], [188, 143,  80], [218, 193, 158], [208, 177, 132], [181, 131,  61], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [181, 130,  60], [213, 186, 146], [217, 192, 157], [182, 133,  64], [175, 122,  45], [188, 143,  80], [218, 193, 158], [211, 182, 140], [182, 134,  65], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [195, 155,  99], [224, 203, 174], [200, 163, 111], [177, 126,  51], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [176, 123,  47], [195, 154,  98], [226, 208, 181], [198, 159, 105], [175, 122,  45], [175, 122,  45], [175, 122,  45], [198, 159, 105], [225, 206, 178], [198, 160, 107], [177, 125,  49], [175, 122,  45], [175, 122,  45], [175, 122,  45], [192, 150,  90], [230, 213, 190], [203, 167, 118], [175, 122,  45], [175, 122,  45], [196, 156, 101], [223, 202, 172], [195, 155,  99], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [205, 172, 125], [224, 203, 174], [187, 141,  77], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [175, 122,  45], [185, 138,  71], [221, 199, 167], [215, 188, 149]]

            res = True

            x = 403
            x1 = 503
            y = 104

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
        cmd = 'nox_adb.exe -s {} shell input tap 892 407'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def swipe_to_another_arena_mode(self):
        if (self.try_count > 7):
            return
        # Swipe to make 3vs3
        print("DEBUG === swipe_to_another_arena_mode")
        cmd = 'nox_adb.exe -s {} shell input swipe 500 500 250 500'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        print("DEBUG === swipe_to_another_arena_mode")
        cmd = 'nox_adb.exe -s {} shell input swipe 500 500 250 500'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def check_in_PICKING_PHASE(self):
        try:
            print("DEBUG === check_in_PICKING_PHASE")
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
            print("DEBUG === check_REQUIREMENT")
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
            print("DEBUG === check_NO_MORE_HEROS")
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[ 37,  43, 155], [149, 151, 197], [242, 241, 233], [172, 173, 205], [ 44,  51, 158], [ 22,  30, 153], [ 27,  35, 156], [ 27,  35, 156], [ 27,  35, 156], [ 27,  35, 156], [ 27,  35, 156], [ 27,  34, 155], [ 24,  32, 154], [ 58,  65, 164], [172, 174, 207], [235, 235, 230], [231, 230, 229], [228, 228, 228], [228, 228, 228], [230, 230, 229], [223, 223, 226], [148, 151, 197], [ 32,  38, 152], [ 82,  87, 172], [216, 216, 223], [216, 216, 223], [104, 109, 181], [ 18,  25, 150]]

            res = True

            x = 787
            x1 = 815
            y = 292

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False

    def check_IN_CRYSTAL(self):
        try:
            print("DEBUG === check_IN_CRYSTAL")
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[248, 242, 235], [209, 178, 133], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 123,  46], [177, 124,  47], [176, 123,  46], [176, 122,  45], [224, 203, 173], [238, 226, 210], [190, 146,  83], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [183, 134,  64], [248, 243, 236], [236, 224, 206], [176, 122,  45], [176, 122,  45], [176, 122,  45], [186, 139,  72], [230, 212, 187], [241, 232, 219], [201, 164, 112], [184, 136,  67], [225, 204, 175], [245, 239, 229], [200, 163, 109], [178, 125,  49], [176, 122,  45], [180, 129,  57], [250, 247, 242], [240, 229, 215], [182, 132,  61], [178, 125,  49], [176, 123,  46], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45]]

            res = True

            x = 300
            x1 = 350
            y = 137

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False

    def check_NEXT_FIGHT(self):
        try:
            print("DEBUG === check_NEXT_FIGHT")
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[ 7, 85,  9], [ 9, 86, 11], [ 67, 126,  69], [232, 239, 232], [254, 254, 254], [183, 206, 184], [ 50, 114,  51], [ 7, 85,  9], [ 81, 136,  82], [215, 228, 215], [255, 255, 255], [204, 220, 205], [25, 98, 27], [ 89, 141,  90], [255, 255, 255], [255, 255, 255], [248, 250, 248], [215, 228, 215], [211, 225, 212], [210, 224, 211], [209, 224, 210], [208, 223, 209], [208, 223, 209], [207, 222, 208], [152, 184, 153], [ 35, 104,  37], [ 7, 85,  9], [22, 95, 23], [232, 239, 232], [255, 255, 255], [228, 236, 228], [ 28, 100,  30], [22, 95, 23], [124, 165, 125], [255, 255, 255], [203, 220, 204], [ 81, 136,  82], [149, 182, 150], [251, 252, 251], [232, 239, 232], [ 62, 123,  64], [ 8, 86, 10], [ 86, 139,  87], [249, 251, 249], [252, 253, 252], [148, 182, 149], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9]]

            res = True

            x = 446
            x1 = 496
            y = 563

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False

    def check_RECONNECT(self):
        try:
            print("DEBUG === check_RECONNECT")
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [240, 245, 240], [199, 217, 200], [ 85, 138,  86], [14, 89, 16], [ 90, 142,  91], [249, 251, 249], [255, 255, 255], [253, 254, 253], [238, 244, 239], [237, 243, 238], [237, 243, 238], [237, 243, 238], [237, 243, 238], [237, 243, 238], [237, 243, 238], [181, 204, 181], [ 49, 114,  51], [ 80, 135,  82], [230, 238, 230], [255, 255, 255], [249, 251, 249], [ 6, 84,  8], [ 6, 84,  8], [ 6, 84,  8], [ 6, 84,  8], [ 6, 84,  8], [ 6, 84,  8], [ 6, 84,  8], [ 6, 84,  8], [ 64, 124,  65], [200, 217, 201], [255, 255, 255], [245, 248, 245], [ 46, 111,  48], [ 6, 84,  8], [ 6, 84,  8], [ 6, 84,  8], [ 6, 84,  8], [ 6, 84,  8], [18, 92, 20], [115, 159, 116], [255, 255, 255], [255, 255, 255], [148, 181, 148]]

            res = True

            x = 583
            x1 = 633
            y = 425

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
        cmd = 'nox_adb.exe -s {} shell input tap 640 522'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def click_X_TODAY_REWARD(self):
        print("DEBUG === click_X")
        cmd = 'nox_adb.exe -s {} shell input tap 954 84'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
    
    def click_X_INCURSION(self):
        print("DEBUG === click_X")
        cmd = 'nox_adb.exe -s {} shell input tap 883 42'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def click_continue_arena_on_right(self):
        print("DEBUG === click_continue_arena_on_right")
        cmd = 'nox_adb.exe -s {} shell input tap 854 450'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def capture_image_for_FREEZE(self):
        print("DEBUG === CAPTURE IMAGE")
        cmd = 'nox_adb.exe -s {} shell screencap -p /sdcard/Download/screen_for_frezze{}.png"'.format(self.device_name, self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        
    def capture_image(self):
        print("DEBUG === CAPTURE IMAGE")
        cmd = 'nox_adb.exe -s {} shell screencap -p /sdcard/Download/screen{}.png'.format(self.device_name, self.threadID)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def execute_cmd_tap(self, x, y):
        cmd = 'nox_adb.exe -s {} shell input tap {} {}'.format(self.device_name, x, y)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def execute_cmd_swipe(self, x, y, z, t):
        cmd = 'nox_adb.exe -s {} shell input swipe {} {} {} {}'.format(self.device_name, x, y, z, t)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def execute_cmd_tap_no_wait(self, x, y):
        cmd = 'nox_adb.exe -s {} shell input tap {} {}'.format(self.device_name, x, y)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def execute_cmd_swipe_no_wait(self, x, y, z, t):
        cmd = 'nox_adb.exe -s {} shell input swipe {} {} {} {}'.format(self.device_name, x, y, z, t)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def random_swipe_right(self):
        x = randrange()
        y = randrange()
        z = randrange()
        t = randrange()

        return x, y, z, t