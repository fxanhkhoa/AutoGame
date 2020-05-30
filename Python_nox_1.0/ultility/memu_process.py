import threading
import time
import subprocess
import os
import cv2
import numpy as np
import datetime
from ultility.check_match_done import check_match_done
from ultility.vm_management import vm_manage

class memu_process_class (threading.Thread):
    
    process_running = True
    flag_exist_GET_MORE = False

    def __init__(self, threadID, pic_folder, log_file, num_of_mode, device_name, account_name, account_password, time_to_reset_nox, claim_reward, claim_help, time_get_reward_and_help_from, time_get_reward_and_help_to, time_check_freeze, time_to_wait_then_reconnect):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.pic_folder = pic_folder
        self.log_file = log_file
        self.device_name = device_name
        self.try_count = 0
        self.try_count_when_auto_hit = 0

        self.arr_mode = num_of_mode
        self.mode_arena = len(num_of_mode) - 1

        self.start_time = time.time()
        self.start_time_reset = time.time()
        self.freeze_time = time.time()
        self.flag_check_loading = False

        self.time_to_reset_nox = time_to_reset_nox
        self.claim_reward = claim_reward
        self.claim_help = claim_help

        self.time_get_reward_and_help_from = time_get_reward_and_help_from
        self.time_get_reward_and_help_to = time_get_reward_and_help_to
        self.time_check_freeze = time_check_freeze
        self.time_to_wait_then_reconnect = time_to_wait_then_reconnect

        self.account_name = account_name
        self.account_password = account_password

        self.pause_signal = False

        self.claim_and_help_once_session = False

        # connect with emulator
        print("DEBUG === Connect to {}".format(self.device_name))
        cmd = 'nox_adb.exe connect {}"'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()

        self.check_match_done_thread = check_match_done(threadID, pic_folder)
        self.check_match_done_thread.start()
    
    def run(self):

        # Launch AR once
        vm_manage.open_AR(self.threadID)
        time.sleep(60)
        # Check Login AR
        self.execute_cmd_swipe(800, 400, 800, 20)
        self.capture_image()
        if self.check_AR_LOGGED_OUT():
            print("DEBUG === click username field")
            self.execute_cmd_tap(141, 76)
            print("DEBUG === input username: {}".format(self.account_name))
            self.execute_cmd_input_text(self.account_name)
            print("DEBUG === click password field")
            self.execute_cmd_tap(112, 247)
            print("DEBUG === input username: {}".format(self.account_password))
            self.execute_cmd_input_text(self.account_password)
            print("DEBUG === click Login")
            self.execute_cmd_tap(415, 354)
            time.sleep(5)

        # Close AR and go to game
        vm_manage.close_AR(self.threadID)
        time.sleep(40)
        vm_manage.start_app(self.threadID)
        while not self.check_TODAY_REWARD() and not self.check_FIGHT_BUTTON() and not self.check_FIGHT_RECOVER() and not self.check_INCURSIONS():
            vm_manage.start_app(self.threadID)
            self.capture_image()
            self.go_to_home()

       
        while self.process_running:
            if self.pause_signal:
                continue
            print(self.mode_arena)
            if time.time() - self.start_time > self.time_to_reset_nox:
                self.start_time = time.time()
                self.freeze_time = time.time()
                self.flag_check_loading = False
                self.claim_and_help_once_session = False
                vm_manage.reboot_vm(self.threadID)
                time.sleep(90)
                vm_manage.start_app(self.threadID)
                time.sleep(2)

            print("DEBUG === Claim reward yet? {}".format(self.claim_and_help_once_session))
            if not self.claim_and_help_once_session:
                # Time Process
                timeCheck_from = int(self.time_get_reward_and_help_from.split(':')[0])
                timeCheck_to = int(self.time_get_reward_and_help_to.split(':')[0])
                now = datetime.datetime.now()
                print(now.year, now.month, now.day, now.hour, now.minute, now.second)
                print("DEBUG === IN time claim? {}".format(self.claim_reward and int(now.hour) > timeCheck_from and int(now.hour) < timeCheck_to))
                # Claim all reward
                if (self.claim_reward and int(now.hour) >= timeCheck_from and int(now.hour) <= timeCheck_to):
                    self.execute_cmd_tap(183, 23)
                    time.sleep(2)
                    print("DEBUG === Click Inventory")
                    self.execute_cmd_tap(605, 83)
                    time.sleep(2)
                    print("DEBUG === Click Items")
                    self.execute_cmd_tap(529, 250)
                    time.sleep(2)
                    print("DEBUG === Click Box")
                    self.execute_cmd_tap(810, 77)
                    time.sleep(2)
                    print("DEBUG === Click Rewards")
                    self.execute_cmd_tap(167, 72)
                    time.sleep(2)
                    while self.check_CLAIM_REWARD_LEFT():
                        self.execute_cmd_tap(647, 205)
                        time.sleep(1.5)
                    time.sleep(1)
                    self.go_to_home()

                # Alliance
                if (self.claim_help and int(now.hour) > timeCheck_from and int(now.hour) < timeCheck_to):
                    self.execute_cmd_tap(183, 23)
                    time.sleep(1)
                    print("DEBUG === Click Alliance")
                    self.execute_cmd_tap(324, 89)
                    time.sleep(5)
                    print("DEBUG === Click Help")
                    self.execute_cmd_tap(474, 129)
                    time.sleep(2)
                    while self.check_HELP():
                        if self.check_HELP_IS_FULL():
                            break
                        self.execute_cmd_tap(688, 174)
                        time.sleep(1.5)
                    time.sleep(1)
                    self.go_to_home()
                
                self.claim_and_help_once_session = True

            if self.check_file_is_not_modified_in_10mins():
                self.start_time = time.time() + 3601

            if self.mode_arena < 0:
                self.mode_arena = len(self.arr_mode) - 1

            # Get one Image
            self.capture_image()

            if not self.process_running:
                return
            elif self.check_IN_FIGHTING() or self.check_NEXT_FIGHT():
                self.try_count_when_auto_hit = 0
                while not self.check_CONTINUE():
                    if self.pause_signal:
                        continue
                    self.capture_image()
                    self.click_NEXT_FIGHT()
                    if self.check_ULTIMATE_SKILL():
                        print("DEBUG === Click ULTIMATE SKILL")
                        self.execute_cmd_tap(126, 431)
                    # self.auto_hit()
                    elif self.check_IN_DIALY_QUEST():
                        self.go_to_home()
                        time.sleep(1)
                        break
                    elif self.check_RECONNECT():
                        time.sleep(self.time_to_wait_then_reconnect)
                        self.start_time = time.time() - 3601
                        break
                    elif self.check_IN_LOADING():
                        print("IN LOADING +++++++++ {}".format(time.time() - self.freeze_time))
                        if not self.flag_check_loading:
                            self.freeze_time = time.time()
                            self.flag_check_loading = True
                        elif time.time() - self.freeze_time > self.time_check_freeze:
                            self.start_time = time.time() + 3601
                            break
                    elif self.check_achived():
                        self.click_claim_achive()
                        self.click_NEXT_SERIES()
                        break
                    self.try_count_when_auto_hit = self.try_count_when_auto_hit + 1
                    print("try_count_when_auto_hit {}".format(self.try_count_when_auto_hit))
                    if self.try_count_when_auto_hit > 100:
                        # self.go_to_home()
                        break
                # if self.try_count_when_auto_hit < 15:
                self.click_NEXT_SERIES()
                self.click_CONTINUE()
                self.freeze_time = time.time()
            elif self.check_FIGHT_BUTTON():
                self.freeze_time = time.time()
                self.go_to_fight()
            elif self.check_PLAY_ARENA():
                self.freeze_time = time.time()
                self.go_to_arena()
            elif self.check_IN_CRYSTAL():
                self.mode_arena = self.mode_arena - 1
                self.go_to_home()
            elif self.check_MULTIVERSE_ARENAS():
                number = self.arr_mode[self.mode_arena]
                self.execute_cmd_swipe(180, 283, 50, 283)
                print(number)
                for i in range(number):
                    self.swipe_to_another_arena_mode()
                time.sleep(1)
                if self.mode_arena == len(self.arr_mode) - 1:
                    self.click_continue_arena_on_right()
                elif self.mode_arena == 0:
                    # self.execute_cmd_swipe(200, 100, 100, 100)
                    self.click_continue_arena_3vs_3_3star()
                else:
                    self.click_continue_arena_3vs_3_3star()
                self.try_count = self.try_count + 1
                print("TRY:", self.try_count)
                if (self.try_count >= 5):
                    self.execute_cmd_tap(80, 36)
                    time.sleep(1.5)
                    self.mode_arena = self.mode_arena - 1
                    self.try_count = 0
            elif self.check_IN_LOADING():
                print("IN LOADING +++++++++ {}".format(time.time() - self.freeze_time))
                if not self.flag_check_loading:
                    self.freeze_time = time.time()
                    self.flag_check_loading = True
                elif time.time() - self.freeze_time > self.time_check_freeze:
                    self.start_time = time.time() - 3601
            elif self.check_NEXT_FIGHT():
                self.click_NEXT_FIGHT()
            elif self.check_CONTINUE():
                self.click_CONTINUE()
            elif self.check_ACCEPT():
                self.click_ACCEPT()
            elif self.check_in_PICKING_PHASE():
                self.try_count = 0
                self.freeze_time = time.time()
                while self.check_GET_HELP_and_CLICK():
                    time.sleep(1)
                    self.capture_image()
                self.capture_image()
                if self.check_FIND_MATCH():
                    self.click_find_match()
                elif self.check_GET_MORE():
                    self.flag_exist_GET_MORE = True
                elif not self.check_GET_MORE():
                    self.flag_exist_GET_MORE = False
                if self.check_NO_MORE_HEROS() and self.check_FIND_MATCH():
                    self.click_find_match()
                elif self.check_NO_MORE_HEROS() and not self.check_FIND_MATCH():
                    self.mode_arena = self.mode_arena - 1
                    self.go_to_home()
                elif not self.check_FIND_MATCH():
                    if self.pause_signal:
                        continue
                    self.capture_image()
                    while self.check_GET_HELP_and_CLICK():
                        self.capture_image()
                    time.sleep(1)
                    self.pick_hero()
                    time.sleep(1)
                    self.click_find_match()
                    time.sleep(1.5)
                    self.click_CONTINUE()
                    time.sleep(1.5)
                    self.click_ACCEPT()
                    time.sleep(1.5)
                    self.click_CONTINUE()
                    time.sleep(1.5)
                    self.click_CONTINUE()
                    time.sleep(1.5)
                    self.click_ACCEPT()
                    time.sleep(1.5)
                    self.click_CONTINUE()
                    # self.try_count = self.try_count + 1
                    # if self.try_count > 7:
                    #     self.mode_arena = self.mode_arena - 1
                    #     self.execute_cmd_tap(183, 23)
                    #     self.go_to_home()
                    #     self.try_count = 0
                    time.sleep(1)
                
            elif self.check_PICK_HERO_FAIL():
                self.execute_cmd_tap(329, 120)
            elif self.check_X_SUMMONER_PROFILE():
                self.execute_cmd_tap(706, 40)
            elif self.check_VIEW_MATCHUP():
                self.click_NEXT_FIGHT()
            elif self.check_UNIT_STORE():
                self.go_to_home()
            elif self.check_WARNING():
                self.execute_cmd_tap(250, 50)
                time.sleep(2)
                self.go_to_home()
                self.mode_arena = self.mode_arena - 1
            elif self.check_WARNING_NETWORK():
                self.execute_cmd_tap(427, 279)
            elif self.check_RECONNECT():
                time.sleep(self.time_to_wait_then_reconnect)
                self.start_time = time.time() - 3601
            elif self.check_FIGHT_RECOVER():
                self.click_FIGHT_RECOVER()
            elif self.check_TODAY_REWARD():
                self.click_X_TODAY_REWARD()
            elif self.check_INCURSIONS():
                self.click_X_INCURSION()
            elif self.check_X_EXIST():
                self.execute_cmd_tap(678, 109)
            elif self.check_X_HERO_EXIST():
                self.execute_cmd_tap(553, 156)
            elif self.check_X_CHAT_EXIST():
                self.execute_cmd_tap(831, 20)
            elif self.check_REQUIREMENT_NOT_MEET() or self.check_WARNING_10K_BC():
                self.execute_cmd_tap(624, 76)
                time.sleep(0.3)
                self.click_continue_arena_3vs_3_3star()
                self.try_count = self.try_count + 1
                if (self.try_count > 5):
                    self.mode_arena = self.mode_arena - 1
                    self.go_to_home()
                    time.sleep(1)
            elif self.check_CrashApp():
                vm_manage.open_AR(self.threadID)
                time.sleep(60)
                # Check Login AR
                self.execute_cmd_swipe(800, 400, 800, 20)
                self.capture_image()
                if self.check_AR_LOGGED_OUT():
                    print("DEBUG === click username field")
                    self.execute_cmd_tap(141, 76)
                    print("DEBUG === input username: {}".format(self.account_name))
                    self.execute_cmd_input_text(self.account_name)
                    print("DEBUG === click password field")
                    self.execute_cmd_tap(112, 247)
                    print("DEBUG === input username: {}".format(self.account_password))
                    self.execute_cmd_input_text(self.account_password)
                    print("DEBUG === click Login")
                    self.execute_cmd_tap(415, 354)
                    time.sleep(5)

                # Close AR and go to game
                vm_manage.close_AR(self.threadID)
                time.sleep(40)
                vm_manage.start_app(self.threadID)
            elif self.check_IN_DIALY_QUEST():
                self.go_to_home()
                time.sleep(1)
            else:
                self.execute_cmd_tap(694, 4)
                pass
                
            


    def stop_thread(self):
        self.process_running = False
        self.check_match_done_thread.stop_check()

    def toggle_thread(self):
        print(self.pause_signal)
        if self.pause_signal:
            self.pause_signal = False
        else:
            self.pause_signal = True

    def go_to_home(self):
        print("DEBUG === GO TO HOME {}".format(self.device_name))
        # Click Menu Button
        self.execute_cmd_tap(183, 23)
        time.sleep(2)

        # Click Home
        self.execute_cmd_tap(147, 86)
        time.sleep(2)
    
    def go_to_fight(self):
        print("DEBUG === GO TO FIGHT {}".format(self.device_name))
        self.execute_cmd_tap(233, 89)
        time.sleep(1)

    def go_to_arena(self):
        print("DEBUG === GO TO ARENA {}".format(self.device_name))
        self.execute_cmd_tap(415, 248)
        time.sleep(4)

    def click_continue_arena_3vs_3_3star(self):
        print("DEBUG === CONTINUE TO ARENA {}".format(self.device_name))
        self.execute_cmd_tap(186, 289)
        time.sleep(1)

    def check_GET_MORE(self):
        print("DEBUG === check_GET_MORE")
        try:
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            res = True
            
            arr = [[ 0, 92,  1], [227, 237, 227], [ 0, 92,  1], [ 0, 92,  1], [ 49, 123,  50], [106, 160, 107], [106, 160, 107], [148, 187, 148], [236, 243, 236], [ 20, 105,  21], [228, 238, 228], [ 17, 103,  18], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [ 0, 92,  1], [205, 223, 205], [ 55, 127,  56], [ 0, 92,  1], [ 0, 92,  1]]

            x = 257
            x1 = 281
            y = 272

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
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[242, 248, 244], [242, 248, 244], [242, 249, 245], [242, 249, 245]]

            res1 = True

            x = 231
            x1 = 235
            y = 193
            

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 10, arr[i - x][0] + 10) or image[y][i][1] not in range(arr[i - x][1] - 10, arr[i - x][1] + 10) or image[y][i][2] not in range(arr[i - x][2] - 10, arr[i - x][2] + 10):
                    res1 = False
                    break
            
            print(res1)

            arr = [[  6, 113,  26], [  5, 115,  31], [  5, 117,  34], [  5, 119,  35], [  5, 120,  37], [  5, 121,  39], [  5, 121,  39], [  5, 121,  40], [  5, 121,  40], [  5, 121,  39], [  5, 120,  38], [  5, 119,  35]]

            res2 = True

            x = 380
            x1 = 392
            y = 207

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res2 = False
                    break

            print(res2)

            arr = [[244, 251, 249], [136, 197, 172], [  0, 255,   0], [  0, 255,   0]]

            res3 = True

            x = 385
            x1 = 389
            y = 183

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res3 = False
                    break

            print(res3)

            arr = [[244, 251, 249], [136, 197, 172]]

            res4 = True

            x = 385
            x1 = 387
            y = 183

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res4 = False
                    break

            print(res4)

            res2 = res2 or res3

            if res1 and res2:
                self.execute_cmd_tap(240, 197)
                time.sleep(1)

                self.execute_cmd_tap(240, 197)
                time.sleep(1)
            
            if not res1 and res2:
                self.execute_cmd_tap(388, 196)
                time.sleep(1)
            
            if res1 and not res2:
                self.execute_cmd_tap(240, 197)
                time.sleep(1)

            return res1 or res2
        except Exception as ex:
            print(ex)
            return False

    def pick_hero(self):
        if (self.try_count > 10):
            return
        print("DEBUG === PICK HERO")
        if not self.flag_exist_GET_MORE:
            self.execute_cmd_swipe(300, 231, 128, 226)
            
            self.execute_cmd_swipe(300, 231, 128, 226)

            self.execute_cmd_swipe(300, 231, 128, 226)
        else:
            self.execute_cmd_swipe(428, 237, 128, 226)
            
            self.execute_cmd_swipe(428, 237, 128, 226)

            self.execute_cmd_swipe(428, 237, 128, 226)

    def check_FIND_MATCH(self):
        print("DEBUG === check_FIND_MATCH")
        try:
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            res = True
            
            arr = [[ 35, 109,  36], [ 35, 109,  36], [ 35, 109,  36], [162, 193, 162], [255, 255, 255], [110, 159, 111], [ 47, 117,  48], [ 47, 117,  48], [ 47, 117,  48], [ 47, 117,  48], [ 40, 112,  41], [144, 181, 144], [255, 255, 255], [138, 177, 138], [ 35, 109,  36], [188, 210, 188], [255, 255, 255], [168, 197, 168], [251, 252, 251], [101, 153, 102], [ 51, 119,  51], [238, 244, 238], [222, 233, 222], [ 35, 109,  36], [120, 165, 120], [255, 255, 255], [129, 171, 130], [ 35, 109,  36], [ 35, 109,  36], [ 35, 109,  36], [108, 158, 109], [254, 254, 254], [161, 193, 161], [ 35, 109,  36], [ 35, 109,  36], [ 35, 109,  36], [ 35, 109,  36], [ 35, 109,  36], [ 48, 118,  49], [227, 236, 227], [218, 230, 218], [240, 245, 240], [184, 208, 185], [ 35, 109,  36], [ 37, 110,  38], [215, 229, 215], [233, 240, 233], [208, 224, 209], [235, 242, 235], [ 44, 115,  45]]

            x = 42
            x1 = 92
            y = 435

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
        self.execute_cmd_tap(81, 445)

        time.sleep(1)

    def check_CONTINUE(self):
        print("DEBUG === CHECK CONTINUE")
        try:
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            res = True

            arr = [[255, 255, 255], [247, 250, 247], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 56, 118,  57], [255, 255, 255], [233, 240, 233], [16, 91, 18], [168, 196, 169], [255, 255, 255], [ 81, 136,  82], [204, 220, 205], [242, 246, 242], [ 38, 106,  40], [159, 189, 159], [255, 255, 255], [ 95, 145,  96], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [167, 195, 168], [252, 253, 252], [ 72, 130,  74], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [137, 174, 138], [255, 255, 255], [137, 174, 138], [ 7, 85,  9], [193, 212, 193], [243, 247, 243], [ 56, 118,  57], [215, 228, 215], [238, 244, 239], [ 28, 100,  30], [184, 206, 185], [255, 255, 255], [ 75, 132,  77], [ 7, 85,  9], [195, 214, 195], [242, 246, 242], [ 46, 112,  48], [ 7, 85,  9]]

            x = 754
            x1 = 800
            y =  450
            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            # print(res)

            arr = [[ 7, 85,  9], [178, 202, 179], [255, 255, 255], [198, 216, 198], [255, 255, 255], [199, 216, 199], [14, 90, 16], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 36, 105,  38], [255, 255, 255], [237, 242, 237], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [104, 152, 105], [255, 255, 255], [199, 216, 199], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [100, 149, 102], [255, 255, 255], [167, 195, 168], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [25, 98, 27], [243, 247, 243], [221, 232, 221], [10, 87, 12], [ 99, 148, 101], [255, 255, 255], [152, 184, 153], [ 8, 86, 10], [ 7, 85,  9], [128, 168, 129], [255, 255, 255], [202, 218, 202], [155, 186, 156], [156, 187, 157], [175, 200, 176], [247, 250, 247], [239, 244, 240], [ 42, 109,  44], [158, 188, 159], [255, 255, 255], [234, 240, 234], [216, 228, 216]]

            res2 = True
            x = 584
            x1 = 644
            y =  450

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res2 = False
                    break


            return res or res2
        except:
            return False

    def click_CONTINUE(self):
        print("DEBUG === CLICK CONTINUE")
        self.execute_cmd_tap(777, 451)
        time.sleep(1)

    
    def click_CONTINUE_without_try(self):
        print("DEBUG === CLICK CONTINUE")
        cmd = 'nox_adb.exe -s {} shell input tap 1170 678'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        time.sleep(1)

    def check_ACCEPT(self):
        print("DEBUG === CHECK ACCEPT")
        try:
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            res = True
            arr = [[153, 185, 154], [ 7, 85,  9], [177, 202, 178], [248, 250, 248], [ 64, 124,  66], [ 7, 85,  9], [ 88, 140,  89], [255, 255, 255], [229, 237, 229], [ 9, 86, 11], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 69, 128,  71], [255, 255, 255], [253, 254, 253], [10, 87, 12], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 50, 114,  51], [255, 255, 255], [255, 255, 255], [219, 230, 219], [215, 228, 215], [214, 227, 214], [213, 226, 214], [212, 226, 213], [ 95, 145,  96], [ 7, 85,  9], [191, 211, 191], [247, 250, 247], [ 99, 148, 101], [ 66, 126,  68], [ 68, 127,  70], [125, 166, 126], [255, 255, 255], [250, 252, 250], [ 48, 113,  50], [ 7, 85,  9], [ 7, 85,  9], [ 98, 148, 100], [255, 255, 255], [160, 190, 160], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9]]

            x = 729
            x1 = 779
            y = 450

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False

    def click_ACCEPT(self):
        print("DEBUG === CLICK ACCEPT")
        self.execute_cmd_tap(751, 450)

        time.sleep(1)

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
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            res1 = True

            arr = [[255, 255, 255], [174, 200, 175], [ 63, 124,  65], [255, 255, 255], [255, 255, 255], [194, 213, 194], [189, 210, 189], [187, 208, 187], [186, 208, 187], [184, 206, 185], [ 60, 122,  62], [ 9, 86, 11], [186, 208, 187], [252, 253, 252], [ 40, 108,  42], [ 29, 100,  31], [254, 254, 254], [184, 206, 185], [ 99, 148, 101], [255, 255, 255], [108, 154, 109], [14, 90, 16], [202, 218, 202], [234, 240, 234], [25, 98, 27], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [ 7, 85,  9], [144, 179, 145], [255, 255, 255], [128, 168, 129], [245, 248, 245], [141, 177, 142], [ 7, 85,  9], [104, 152, 105], [255, 255, 255], [ 91, 142,  92], [235, 241, 235], [224, 234, 224], [ 7, 85,  9], [ 7, 85,  9], [12, 88, 14], [241, 246, 241], [217, 229, 217], [10, 87, 12], [169, 196, 170], [255, 255, 255]]

            x = 304
            x1 = 354
            y = 375

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res1 = False
                    break

            res2 = True

            arr = [[ 6, 84,  8], [ 94, 144,  95], [254, 254, 254], [166, 194, 167], [ 8, 85, 10], [189, 209, 189], [249, 251, 249], [ 67, 126,  68], [ 6, 84,  8], [111, 156, 113], [255, 255, 255], [174, 199, 175], [ 70, 128,  72], [255, 255, 255], [255, 255, 255], [231, 238, 231], [230, 238, 230], [230, 238, 230], [230, 238, 230], [230, 238, 230], [ 74, 131,  76], [ 6, 84,  8], [104, 151, 105], [255, 255, 255], [138, 175, 139], [ 79, 134,  81], [255, 255, 255], [114, 158, 116], [ 55, 118,  56], [246, 249, 246], [165, 193, 166], [25, 97, 26], [234, 241, 235], [196, 215, 197], [12, 88, 14]]

            x = 294
            x1 = 329
            y = 301

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

        self.execute_cmd_tap(511, 376)
        self.execute_cmd_tap(508, 302)

        time.sleep(1)

    def click_NEXT_SERIES(self):
        print("DEBUG === CLICK NEXT SERIES")
        self.execute_cmd_tap(636, 451)

        time.sleep(1)

    def check_FIGHT_BUTTON(self):
        try:
            print("DEBUG === check_FIGHT_BUTTON")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))

            arr = [[ 2, 76,  4], [194, 212, 195], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [23, 91, 25], [196, 214, 197], [ 2, 76,  4], [17, 87, 19], [189, 208, 189], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 65, 120,  66], [129, 166, 130], [132, 168, 133], [136, 171, 137], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [158, 186, 159], [ 42, 104,  43], [ 2, 76,  4], [ 2, 76,  4], [109, 152, 110], [166, 192, 166], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [210, 223, 211], [24, 91, 26], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4], [ 2, 76,  4]]

            res = True

            x = 220
            x1 = 270
            y = 104

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
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[199, 219, 199], [169, 200, 170], [169, 200, 170], [166, 198, 167], [141, 182, 142], [ 60, 130,  62], [ 0, 92,  2], [ 0, 92,  2], [214, 229, 214], [ 78, 142,  79], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [197, 218, 197], [ 71, 137,  72], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [220, 233, 220], [ 28, 110,  30], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 85, 146,  86], [182, 208, 183], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 14, 101,  16], [220, 233, 220], [ 55, 127,  57], [ 0, 92,  2], [ 0, 92,  2], [ 19, 104,  21], [232, 240, 232], [ 22, 106,  24], [ 0, 92,  2], [ 62, 132,  64], [245, 249, 245], [137, 180, 138], [126, 173, 127], [126, 173, 127], [136, 179, 137], [207, 224, 207], [192, 215, 192], [ 8, 97, 10], [ 25, 108,  27], [209, 226, 209]]

            res = True

            x = 373
            x1 = 430
            y = 388

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
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))

            arr = [[183, 135,  65], [226, 205, 177], [177, 124,  48], [176, 122,  45], [225, 204, 175], [180, 129,  56], [176, 122,  45], [211, 181, 138], [200, 162, 108], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [221, 197, 164], [186, 139,  72], [176, 122,  45], [211, 181, 138], [204, 168, 118], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [221, 198, 164], [188, 142,  77], [176, 122,  45], [176, 122,  45], [176, 122,  45], [181, 130,  57], [228, 209, 183], [191, 147,  85], [176, 122,  45], [176, 122,  45], [189, 144,  80], [229, 212, 187], [179, 127,  53], [178, 125,  50], [220, 197, 163], [196, 156,  99], [176, 122,  45], [179, 127,  53], [230, 213, 188], [189, 144,  80], [179, 127,  53], [179, 127,  53], [179, 127,  53], [179, 127,  52], [177, 123,  47], [176, 122,  45], [229, 211, 186], [212, 183, 141]]

            res = True

            x = 275
            x1 = 330
            y = 71

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False

    def check_achived(self):
        print("DEBUG === check_achived")
        try:
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))

            arr = [[  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0], [  0, 123,   0]]

            res = True

            x = 233
            x1 = 283
            y = 286

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False
    def click_claim_achive(self):
        print("DEBUG === click_claim_achive")
        self.execute_cmd_tap(597, 273)

    def swipe_to_another_arena_mode(self):
        if (self.try_count > 7):
            return
        # Swipe to make 3vs3
        # print("DEBUG === swipe_to_another_arena_mode")
        # self.execute_cmd_swipe(340, 283, 50, 283)

        print("DEBUG === swipe_to_another_arena_mode")
        self.execute_cmd_swipe(340, 283, 245, 283)
        self.execute_cmd_swipe(340, 283, 245, 283)
        self.execute_cmd_swipe(340, 283, 245, 283)
        self.execute_cmd_swipe(340, 283, 245, 283)


    def check_in_PICKING_PHASE(self):
        try:
            print("DEBUG === check_in_PICKING_PHASE")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[  0, 105,  30], [  0, 105,  30], [  0, 105,  30], [  0, 105,  30], [ 25, 120,  52], [242, 247, 244], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [225, 237, 229], [ 16, 114,  44], [  0, 105,  30], [  0, 105,  30], [  0, 105,  30], [  0, 105,  30], [  7, 109,  36], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [246, 250, 247], [ 51, 135,  75], [  0, 105,  30], [  0, 105,  30], [  0, 105,  30], [  0, 105,  30]]

            res = True

            x = 811
            x1 = 841
            y = 76

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            # print("DEBUG === PICKING PHASE", res)
            return res
        except:
            return False

    def check_REQUIREMENT_NOT_MEET(self):
        try:
            print("DEBUG === check_REQUIREMENT_NOT_MEET")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[255, 255, 255], [255, 255, 255], [24, 97, 25], [ 33, 104,  35], [174, 200, 175], [174, 200, 175], [174, 200, 175], [174, 200, 175], [ 38, 107,  40], [170, 197, 171], [255, 255, 255], [208, 223, 209], [179, 203, 180], [177, 202, 178], [176, 201, 177], [175, 201, 176], [129, 169, 130], [ 7, 86,  9], [ 7, 86,  9], [ 7, 86,  9], [ 98, 148, 100], [255, 255, 255], [160, 190, 160], [ 7, 86,  9], [ 7, 86,  9], [ 7, 86,  9], [ 7, 86,  9], [ 7, 86,  9], [ 7, 86,  9], [ 7, 86,  9], [16, 92, 18], [205, 221, 206], [255, 255, 255], [ 44, 111,  46], [ 7, 86,  9], [ 7, 86,  9], [ 7, 86,  9], [ 7, 86,  9], [ 7, 86,  9], [ 67, 127,  69], [255, 255, 255], [234, 240, 234], [181, 205, 182], [181, 205, 182], [181, 205, 182], [239, 244, 240], [255, 255, 255], [ 59, 121,  60], [ 7, 86,  9], [10, 88, 12]]

            res = True

            x = 370
            x1 = 420
            y = 366

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            return res
        except:
            return False

    def check_APP_FREZZE(self):
        try:
            # self.capture_image()
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
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))

            arr = [[241, 241, 241], [241, 241, 241], [236, 236, 236], [47, 47, 49], [64, 64, 66], [244, 244, 244], [255, 255, 255], [215, 215, 215], [47, 47, 49], [89, 89, 91], [255, 255, 255], [255, 255, 255], [215, 215, 215], [47, 47, 49], [52, 52, 54], [195, 195, 196], [238, 238, 238], [238, 238, 238], [241, 241, 241], [255, 255, 255], [255, 255, 255], [200, 200, 201], [49, 49, 51], [47, 47, 49], [223, 223, 223], [255, 255, 255], [253, 253, 253], [239, 239, 239], [238, 238, 238], [238, 238, 238], [238, 238, 238], [240, 240, 240], [253, 253, 253], [255, 255, 255], [234, 234, 234], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [53, 53, 55], [210, 210, 211], [255, 255, 255], [255, 255, 255], [73, 73, 75], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49]]

            res = True

            x = 346
            x1 = 400
            y = 108

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
            # self.capture_image()
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
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            arr = [[47, 47, 49], [169, 169, 169], [255, 255, 255], [219, 219, 219], [47, 47, 49], [47, 47, 49], [47, 47, 49], [52, 52, 54], [208, 208, 208], [255, 255, 255], [239, 239, 239], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [90, 90, 92], [255, 255, 255], [255, 255, 255], [151, 151, 152], [47, 47, 49], [164, 164, 165], [255, 255, 255], [208, 208, 208], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [184, 184, 185], [255, 255, 255], [216, 216, 216], [47, 47, 49], [47, 47, 49], [159, 159, 160], [255, 255, 255], [178, 178, 179], [47, 47, 49], [97, 97, 98], [254, 254, 254], [255, 255, 255], [101, 101, 102], [47, 47, 49], [47, 47, 49], [47, 47, 49], [48, 48, 50], [209, 209, 209], [255, 255, 255], [255, 255, 255], [248, 248, 249], [108, 108, 110], [47, 47, 49]]

            res = True

            x = 348
            x1 = 400
            y = 25

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
            # self.capture_image()
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
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[ 7, 83,  8], [ 6, 83,  8], [ 6, 84,  8], [155, 186, 156], [155, 187, 156], [155, 187, 156], [155, 186, 156], [ 7, 82,  9], [ 7, 83,  8], [ 6, 83,  8], [ 6, 84,  8], [156, 187, 156], [155, 187, 156], [155, 186, 156], [156, 186, 157], [ 6, 83,  8], [ 6, 84,  8]]

            res = True

            x = 418
            x1 = 435
            y = 23

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
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[ 26,  33, 151]]

            res = True

            x = 386
            x1 = 387
            y = 197

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 10, arr[i - x][0] + 10) or image[y][i][1] not in range(arr[i - x][1] - 10, arr[i - x][1] + 10) or image[y][i][2] not in range(arr[i - x][2] - 10, arr[i - x][2] + 10):
                    res = False
                    break
            print(res)

            arr = [[ 0, 255, 0]]

            res2 = True

            x = 523
            x1 = 524
            y = 194

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 10, arr[i - x][0] + 10) or image[y][i][1] not in range(arr[i - x][1] - 10, arr[i - x][1] + 10) or image[y][i][2] not in range(arr[i - x][2] - 10, arr[i - x][2] + 10):
                    res2 = False
                    break
            print(res2)

            arr = [[ 27,  35, 155]]

            res3 = True

            x = 532
            x1 = 533
            y = 187

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 10, arr[i - x][0] + 10) or image[y][i][1] not in range(arr[i - x][1] - 10, arr[i - x][1] + 10) or image[y][i][2] not in range(arr[i - x][2] - 10, arr[i - x][2] + 10):
                    res3 = False
                    break
            print(res3)

            return res or res2 or res3
        except:
            return False

    def check_IN_CRYSTAL(self):
        try:
            print("DEBUG === check_IN_CRYSTAL")
            # self.capture_image()
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
            # self.capture_image()
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
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[ 7, 86,  9], [ 7, 86,  9], [166, 194, 166], [255, 255, 255], [117, 161, 118], [ 60, 122,  62], [ 61, 123,  63], [ 93, 144,  94], [242, 246, 242], [245, 248, 245], [25, 97, 26], [200, 217, 200], [255, 255, 255], [138, 175, 139], [104, 152, 105], [103, 152, 105], [103, 152, 105], [102, 151, 104], [ 68, 128,  70], [ 41, 109,  43], [255, 255, 255], [255, 255, 255], [26, 99, 28], [ 7, 86,  9], [ 7, 86,  9], [ 7, 86,  9], [ 7, 86,  9], [ 31, 103,  33], [238, 244, 239], [253, 254, 253], [22, 96, 23], [ 7, 86,  9], [ 7, 86,  9], [ 7, 86,  9], [ 46, 113,  48], [255, 255, 255], [253, 254, 253], [18, 93, 20], [119, 162, 120], [255, 255, 255], [135, 173, 136], [196, 215, 196], [228, 236, 228], [ 27, 100,  29], [ 93, 144,  94], [255, 255, 255], [150, 183, 151], [ 7, 86,  9], [119, 162, 120], [255, 255, 255]]

            res = True

            x = 385
            x1 = 435
            y = 282

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            print(res)
            return res
        except:
            return False

    def check_PICK_HERO_FAIL(self):
        try:
            print("DEBUG === check_PICK_HERO_FAIL")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[ 6, 83,  7], [ 6, 83,  7], [123, 164, 124], [255, 255, 255], [247, 250, 247], [156, 187, 157], [ 6, 83,  7], [ 47, 111,  48], [181, 204, 181], [255, 255, 255], [199, 217, 200], [ 64, 123,  64], [ 7, 84,  8], [102, 149, 102], [232, 239, 232], [251, 252, 251], [114, 158, 115], [168, 195, 168], [255, 255, 255], [234, 241, 235], [ 84, 137,  85], [ 6, 83,  7], [ 55, 117,  56], [194, 213, 195], [255, 255, 255], [213, 226, 213], [135, 172, 135], [108, 153, 108], [108, 153, 108], [108, 153, 108], [108, 153, 108], [108, 153, 108], [108, 153, 108], [103, 150, 103], [ 40, 107,  41], [121, 163, 122], [255, 255, 255], [254, 254, 254], [160, 190, 161], [14, 88, 15], [ 6, 83,  7], [ 6, 83,  7], [ 6, 83,  7], [ 6, 83,  7], [ 6, 83,  7], [ 69, 127,  70], [243, 247, 243], [255, 255, 255], [238, 244, 238], [21, 93, 22]]

            res = True

            x = 615
            x1 = 665
            y = 443

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False

    def check_X_EXIST(self):
        try:
            print("DEBUG === check_X_EXIST")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[47, 47, 49], [47, 47, 49], [77, 77, 79], [112, 112, 114], [112, 112, 114], [112, 112, 114], [112, 112, 114], [112, 112, 114], [112, 112, 114], [73, 73, 75], [47, 47, 49], [47, 47, 49]]

            res = True

            x = 672
            x1 = 684
            y = 110

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False

    def check_X_CHAT_EXIST(self):
        try:
            print("DEBUG === check_X_CHAT_EXIST")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[49, 49, 50], [49, 49, 50], [52, 52, 53], [114, 114, 114], [114, 114, 114], [114, 114, 114], [114, 114, 114], [114, 114, 114], [114, 114, 114], [113, 113, 114], [51, 51, 52], [49, 49, 50]]

            res = True

            x = 826
            x1 = 838
            y = 21

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False

    def check_CLAIM_REWARD_LEFT(self):
        try:
            print("DEBUG === check_X_CHAT_EXIST")
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[ 19, 104,  21], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [214, 229, 214], [ 78, 142,  79], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 62, 132,  64], [237, 243, 237], [ 27, 109,  29], [ 0, 92,  2], [182, 208, 183], [129, 174, 130], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 65, 134,  66], [195, 217, 195], [ 0, 92,  2], [ 0, 92,  2], [161, 195, 162], [ 91, 150,  92], [ 66, 134,  67], [239, 245, 239], [ 29, 111,  31], [ 0, 92,  2], [ 0, 92,  2], [106, 160, 107], [217, 231, 217], [ 7, 96,  9], [211, 227, 211], [ 44, 120,  46], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2]]

            res = True

            x = 628
            x1 = 678
            y = 206

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False

    def check_HELP(self):
        try:
            print("DEBUG === check_HELP")
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2]]

            res = True

            x = 655
            x1 = 685
            y = 228

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            print(res)

            res2 = True

            arr = [[ 0, 92,  2], [ 0, 92,  2], [201, 220, 201], [229, 238, 229], [221, 233, 221], [221, 233, 221], [221, 233, 221], [221, 233, 221], [223, 235, 223], [250, 252, 250], [ 77, 141,  78], [ 28, 110,  30], [249, 251, 249], [227, 237, 227], [227, 237, 227], [227, 237, 227], [227, 237, 227], [199, 219, 199], [ 0, 92,  2], [ 96, 153,  97], [198, 219, 198], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [ 0, 92,  2], [203, 222, 203], [ 86, 147,  87], [ 40, 118,  42], [ 40, 118,  42], [ 41, 118,  43], [ 83, 145,  84], [241, 246, 241], [ 63, 132,  65], [ 0, 92,  2]]

            x = 657
            x1 = 693
            y = 287

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res2 = False
                    break
            print(res2)

            return res or res2
        except:
            return False

    def check_HELP_IS_FULL(self):
        try:
            print("DEBUG === check_HELP_IS_FULL")
            self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[47, 47, 49], [40, 80, 36], [ 26, 149,  10], [46, 52, 47], [41, 75, 38], [ 28, 138,  14], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [47, 47, 49], [ 23, 166,   3], [41, 76, 38], [47, 47, 49], [47, 47, 49], [47, 48, 49], [40, 79, 37], [ 25, 155,   7], [ 27, 145,  11], [38, 93, 31], [47, 47, 49], [ 23, 166,   3], [41, 76, 38], [47, 47, 49], [47, 47, 49], [47, 48, 49], [40, 79, 37], [ 25, 155,   7], [ 27, 145,  11], [38, 93, 31], [47, 47, 49], [ 23, 166,   3], [41, 76, 38], [47, 47, 49], [47, 47, 49], [47, 48, 49], [40, 79, 37], [ 25, 155,   7], [ 27, 145,  11], [38, 93, 31]]

            res = True

            x = 449
            x1 = 492
            y = 163

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            print(res)
            return res
        except:
            return False

    def check_IN_LOADING(self):
        try:
            print("DEBUG === check_IN_LOADING")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[  0,   9, 145], [  0,   9, 145], [  0,   9, 145], [  0,   9, 145], [  1,   9, 143], [  1,   9, 141], [  2,  10, 142], [  2,  10, 142], [  1,   9, 141], [  1,   9, 141], [  1,   9, 141], [  1,   9, 141], [  1,   9, 141], [  1,   9, 141], [  0,   8, 140], [  0,   7, 139], [  0,   7, 139], [  0,   7, 139], [  0,   7, 139], [  0,   7, 139], [  0,   6, 138], [  0,   6, 138], [  0,   6, 138], [  0,   6, 138], [  0,   6, 138], [  0,   6, 138], [  0,   6, 138], [  0,   6, 138], [  0,   6, 138], [  0,   5, 137], [  0,   4, 136], [  0,   5, 137], [  0,   6, 138], [  0,   6, 138], [  0,   7, 136], [  0,   8, 132], [  0,   8, 132], [  0,   8, 132], [  0,   9, 133], [  0,   9, 133], [  1,   9, 133], [  0,   8, 132], [  0,   8, 132], [  0,   7, 131], [  0,   7, 131], [  0,   8, 132], [  0,   7, 131], [  0,   7, 131], [  0,   8, 132], [  0,   8, 132]]

            res = True

            x = 520
            x1 = 570
            y = 84

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False

    def check_ULTIMATE_SKILL(self):
        try:
            print("DEBUG === check_ULTIMATE_SKILL")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[  0,   0, 150], [  0,   0, 147], [  0,   0, 148], [  0,   0, 150], [  0,   0, 147], [  0,   0, 150], [  0,   0, 147], [  0,   0, 148], [  0,   0, 150], [  0,   0, 150], [  0,   0, 149], [  0,   0, 148], [  0,   0, 148], [  0,   0, 149], [  0,   0, 150], [  0,   0, 150], [  0,   0, 150], [  0,   0, 150], [  0,   0, 147], [  0,   0, 148], [  0,   0, 150], [  0,   0, 147], [  0,   0, 149], [  0,   0, 150]]

            res = True

            x = 181
            x1 = 205
            y = 448

            for i in range(x, x1):
                # print(image[y][i], arr[i - x])
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            
            return res
        except:
            return False

    def check_AR_LOGGED_OUT(self):
        try:
            print("DEBUG === check_AR_LOGGED_OUT")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [229, 237, 252], [255, 255, 255], [176, 201, 247], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [152, 185, 245], [255, 255, 255], [243, 247, 254], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [ 38, 107, 234], [255, 255, 255], [255, 255, 255], [119, 162, 242], [  0,  81, 230], [  0,  81, 230], [143, 179, 244], [255, 255, 255], [255, 255, 255], [  8,  86, 231], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [  0,  81, 230], [238, 243, 253], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [217, 229, 251], [  0,  81, 230]]

            res = True

            x = 385
            x1 = 435
            y = 355

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            print(res)
            return res
        except:
            return False
    
    def check_UNIT_STORE(self):
        try:
            print("DEBUG === check_UNIT_STORE")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[176, 122,  45], [209, 178, 133], [221, 198, 164], [189, 143,  79], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [206, 172, 124], [231, 214, 191], [187, 140,  74], [176, 122,  45], [176, 122,  45], [210, 179, 135], [219, 195, 160], [185, 138,  70], [176, 122,  45], [187, 141,  75], [217, 190, 153], [219, 195, 160], [189, 144,  80], [177, 123,  47], [176, 122,  45], [176, 122,  45], [206, 173, 126], [230, 213, 189], [185, 138,  70], [176, 122,  45], [176, 122,  45], [181, 130,  57], [206, 173, 126], [221, 197, 164], [191, 147,  85], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [215, 187, 148], [230, 213, 188], [182, 132,  61], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [176, 122,  45], [204, 169, 119], [229, 211, 185], [215, 187, 148], [204, 169, 119]]

            res = True

            x = 582
            x1 = 642
            y = 111

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            print(res)
            return res
        except:
            return False

    def check_WARNING_NETWORK(self):
        try:
            print("DEBUG === check_WARNING_NETWORK")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[47, 47, 49], [62, 62, 64], [237, 237, 237], [255, 255, 255], [191, 191, 191], [47, 47, 49], [116, 116, 118], [255, 255, 255], [236, 236, 236], [62, 62, 64], [101, 101, 102], [255, 255, 255], [255, 255, 255], [144, 144, 145], [47, 47, 49], [168, 168, 169], [255, 255, 255], [253, 253, 253], [58, 58, 60], [47, 47, 49], [47, 47, 49], [54, 54, 55], [212, 212, 212], [255, 255, 255], [235, 235, 236], [48, 48, 50], [47, 47, 49], [75, 75, 76], [255, 255, 255], [255, 255, 255], [181, 181, 181], [47, 47, 49], [47, 47, 49], [47, 47, 49], [202, 202, 202], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [227, 227, 228], [54, 54, 55], [47, 47, 49], [47, 47, 49], [233, 233, 233], [255, 255, 255], [205, 205, 206]]

            res = True

            x = 399
            x1 = 450
            y = 182

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            print(res)
            return res
        except:
            return False

    def check_X_HERO_EXIST(self):
        try:
            print("DEBUG === check_X_HERO_EXIST")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[47, 47, 49], [60, 60, 62], [112, 112, 114], [112, 112, 114], [112, 112, 114], [112, 112, 114], [112, 112, 114], [112, 112, 114], [92, 92, 93]]

            res = True

            x = 549
            x1 = 558
            y = 156

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            print(res)
            return res
        except:
            return False

    def check_X_SUMMONER_PROFILE(self):
        try:
            print("DEBUG === check_X_SUMMONER_PROFILE")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[47, 47, 49], [77, 77, 79], [112, 112, 114], [112, 112, 114], [112, 112, 114], [112, 112, 114], [112, 112, 114], [112, 112, 114], [73, 73, 75]]

            res = True

            x = 703
            x1 = 712
            y = 40

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            print(res)
            return res
        except:
            return False

    def check_CrashApp(self):
        try:
            print("DEBUG === check_CrashApp")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[238, 238, 238], [238, 238, 238], [164, 174,  66], [136, 150,   0], [136, 150,   0], [172, 181,  85], [238, 238, 238], [238, 238, 238], [238, 238, 238], [238, 238, 238], [238, 238, 238], [238, 238, 238], [238, 238, 238], [238, 238, 238], [165, 175,  69], [136, 150,   0], [136, 150,   0], [171, 180,  81], [238, 238, 238], [238, 238, 238], [215, 218, 184], [136, 150,   0], [136, 150,   0], [136, 150,   0], [181, 189, 105], [136, 150,   0], [136, 150,   0], [136, 150,   0], [173, 182,  86], [238, 238, 238], [238, 238, 238], [238, 238, 238], [238, 238, 238], [238, 238, 238], [238, 238, 238], [238, 238, 238]]

            res = True

            x = 596
            x1 = 632
            y = 317

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            print(res)
            return res
        except:
            return False

    def check_WARNING_10K_BC(self):
        try:
            print("DEBUG === check_WARNING_10K_BC")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[51, 51, 53], [204, 204, 204], [255, 255, 255], [250, 250, 250], [63, 63, 65], [192, 192, 193], [255, 255, 255], [211, 211, 211], [54, 54, 55], [58, 58, 60], [248, 248, 248], [255, 255, 255], [198, 198, 198], [50, 50, 52], [214, 214, 215], [255, 255, 255], [193, 193, 194], [47, 47, 49], [47, 47, 49], [47, 47, 49], [82, 82, 84], [248, 248, 248], [255, 255, 255], [204, 204, 204], [146, 146, 147], [146, 146, 147], [146, 146, 147], [235, 235, 236], [255, 255, 255], [243, 243, 243], [62, 62, 64], [47, 47, 49], [47, 47, 49], [202, 202, 202], [255, 255, 255], [253, 253, 253], [226, 226, 227], [221, 221, 221], [221, 221, 221], [241, 241, 241], [255, 255, 255], [255, 255, 255], [149, 149, 150], [58, 58, 60], [47, 47, 49], [47, 47, 49], [47, 47, 49], [233, 233, 233], [255, 255, 255], [207, 207, 207], [47, 47, 49], [49, 49, 51], [191, 191, 191], [255, 255, 255], [213, 213, 213], [64, 64, 66], [241, 241, 241], [255, 255, 255], [171, 171, 172], [47, 47, 49], [47, 47, 49], [165, 165, 166], [255, 255, 255], [255, 255, 255], [129, 129, 130], [47, 47, 49], [47, 47, 49], [233, 233, 233], [255, 255, 255], [207, 207, 207], [47, 47, 49], [49, 49, 51], [191, 191, 191], [255, 255, 255], [213, 213, 213], [64, 64, 66], [241, 241, 241], [255, 255, 255], [171, 171, 172], [47, 47, 49], [82, 82, 84], [255, 255, 255], [255, 255, 255], [222, 222, 223], [47, 47, 49], [49, 49, 51], [132, 132, 133], [156, 156, 157], [156, 156, 157], [175, 175, 176], [255, 255, 255], [255, 255, 255]]

            res = True

            x = 400
            x1 = 492
            y = 168

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            print(res)
            return res
        except:
            return False

    def check_IN_DIALY_QUEST(self):
        try:
            print("DEBUG === check_IN_DIALY_QUEST")
            # self.capture_image()
            image = cv2.imread(self.pic_folder + "/screen{}.png".format(self.threadID))
            
            arr = [[  1,   1, 146], [  0,   0, 146], [ 14,  14, 152], [156, 156, 213], [178, 178, 222], [178, 178, 222], [  9,   9, 150], [  0,   0, 146], [  0,   0, 146], [  0,   0, 146], [  0,   0, 146], [  0,   0, 146], [  0,   0, 146], [  0,   0, 146], [  0,   0, 146], [  0,   0, 146], [ 90,  90, 184], [ 99,  99, 188], [ 37,  37, 162], [  0,   0, 146]]

            res = True

            x = 804
            x1 = 824
            y = 337

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res = False
                    break
            print(res)

            arr = [[  1,   1, 146], [  0,   0, 146], [ 14,  14, 152], [156, 156, 213], [178, 178, 222], [178, 178, 222], [  9,   9, 150], [  0,   0, 146], [  0,   0, 146], [  0,   0, 146], [  0,   0, 146], [  0,   0, 146], [  0,   0, 146], [  0,   0, 146], [  0,   0, 146], [  0,   0, 146], [162, 162, 215], [178, 178, 222], [ 67,  67, 175], [  0,   0, 146]]

            res2 = True

            x = 804
            x1 = 824
            y = 413

            for i in range(x, x1):
                if image[y][i][0] not in range(arr[i - x][0] - 2, arr[i - x][0] + 2) or image[y][i][1] not in range(arr[i - x][1] - 2, arr[i - x][1] + 2) or image[y][i][2] not in range(arr[i - x][2] - 2, arr[i - x][2] + 2):
                    res2 = False
                    break
            print(res2)

            return res or res2
        except:
            return False

    def check_file_is_not_modified_in_10mins(self):
        current_time = time.time()
        last_time = os.path.getmtime(self.pic_folder + "/screen{}.png".format(self.threadID))
        if current_time - last_time > 180: # 3 min
            return True
        else:
            return False

    def click_FIGHT_RECOVER(self):
        print("DEBUG === click_FIGHT_RECOVER")
        self.execute_cmd_tap(425, 345)

        time.sleep(1)

    def click_X_TODAY_REWARD(self):
        print("DEBUG === click_X_TODAY_REWARD")
        self.execute_cmd_tap(636, 28)

        time.sleep(1)
    
    def click_X_INCURSION(self):
        print("DEBUG === click_X_INCURSION")
        cmd = 'nox_adb.exe -s {} shell input tap 883 42'.format(self.device_name)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

        time.sleep(1)

    def click_continue_arena_on_right(self):
        print("DEBUG === click_continue_arena_on_right")
        self.execute_cmd_tap(577, 291)
        time.sleep(1)

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
        cmd = 'adb.exe -s {} shell input tap {} {}'.format(self.device_name, x, y)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def execute_cmd_swipe(self, x, y, z, t):
        cmd = 'adb.exe -s {} shell input swipe {} {} {} {}'.format(self.device_name, x, y, z, t)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def execute_cmd_tap_no_wait(self, x, y):
        cmd = 'nox_adb.exe -s {} shell input tap {} {}'.format(self.device_name, x, y)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def execute_cmd_swipe_no_wait(self, x, y, z, t):
        cmd = 'nox_adb.exe -s {} shell input swipe {} {} {} {}'.format(self.device_name, x, y, z, t)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def execute_cmd_input_text(self, text):
        cmd = 'nox_adb.exe -s {} shell input text {}'.format(self.device_name, text)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()

    def random_swipe_right(self):
        x = randrange()
        y = randrange()
        z = randrange()
        t = randrange()

        return x, y, z, t