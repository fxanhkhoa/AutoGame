import subprocess
import os
import cv2
import numpy as np
from signal import signal, SIGINT
from sys import exit
import time
import json
from ultility.vm_management import vm_manage

from ultility.memu_process import memu_process_class

from tkinter import *
import tkinter as tk

# Make UI

window = Tk()
window.title("Auto MCOC")

gridFrame = tk.Frame(window)

list_thread = []
b0_text = tk.StringVar()
b0_text.set("pause 0")

b1_text = tk.StringVar()
b1_text.set("pause 1")

b2_text = tk.StringVar()
b2_text.set("pause 2")

b3_text = tk.StringVar()
b3_text.set("pause 3")

b4_text = tk.StringVar()
b4_text.set("pause 4")

b5_text = tk.StringVar()
b5_text.set("pause 5")

b6_text = tk.StringVar()
b6_text.set("pause 6")

b7_text = tk.StringVar()
b7_text.set("pause 7")

def b0_thread():
    global b0_text
    print("click b0")
    if b0_text.get() == 'run 0':
        b0_text.set('pause 0')
    else:
        b0_text.set('run 0')
    list_thread[0].toggle_thread()

def b1_thread():
    global b1_text
    print("click b1")
    if b1_text.get() == 'run 1':
        b1_text.set('pause 1')
    else:
        b1_text.set('run 1')
    list_thread[1].toggle_thread()

def b2_thread():
    global b2_text
    print("click b2")
    if b2_text.get() == 'run 2':
        b2_text.set('pause 2')
    else:
        b2_text.set('run 2')
    list_thread[2].toggle_thread()

def b3_thread():
    global b3_text
    print("click b3")
    if b3_text.get() == 'run 3':
        b3_text.set('pause 3')
    else:
        b3_text.set('run 3')
    list_thread[3].toggle_thread()

def b4_thread():
    global b4_text
    print("click b4")
    if b4_text.get() == 'run 4':
        b4_text.set('pause 4')
    else:
        b4_text.set('run 4')
    list_thread[4].toggle_thread()

def b5_thread():
    global b5_text
    print("click b5")
    if b5_text.get() == 'run 5':
        b5_text.set('pause 5')
    else:
        b5_text.set('run 5')
    list_thread[5].toggle_thread()

def b6_thread():
    global b6_text
    print("click b6")
    if b6_text.get() == 'run 6':
        b6_text.set('pause 6')
    else:
        b6_text.set('run 6')
    list_thread[6].toggle_thread()

def b7_thread():
    global b7_text
    print("click b7")
    if b7_text.get() == 'run 7':
        b7_text.set('pause 7')
    else:
        b7_text.set('run 7')
    list_thread[7].toggle_thread()

### Input Signal
def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    for thread in list_thread:
        thread.stop_thread()
    exit(0)

def test():
    print(vm_manage.check_vm_running(0))

def on_closing():
    print("CLOSE TOOL")
    vm_manage.stop_all_vm()
    window.destroy()

if __name__ == '__main__':
    # Tell Python to run the handler() function when SIGINT is recieved
    signal(SIGINT, handler)

    f = open("config.json", "r")
    jsonStr = f.read()

    config_obj = json.loads(jsonStr)
    f.close()

    

    ### Connect
    wd = os.getcwd()
    os.chdir(config_obj["memu_folder"])

    print(os.getcwd())

    print('Running. Press CTRL-C to exit.')

    ### Test Part
    # test()

    #### Process
    for i in range(0, config_obj['NUM_OF_THREAD']):
        print("creating {}".format(i))
        memu_thr = memu_process_class(i, pic_folder = config_obj["picture_share_folder"], log_file = config_obj["log_file"], num_of_mode = config_obj["NUM_OF_MODE"][i], device_name = config_obj["nox_name"][i], account_name = config_obj["account_username"][i], account_password = config_obj["account_password"][i], time_to_reset_nox = config_obj["time_to_reset_nox"], claim_reward=config_obj["claim_reward"], claim_help=config_obj["claim_help"], time_get_reward_and_help_from=config_obj["time_get_reward_and_help_from"], time_get_reward_and_help_to=config_obj["time_get_reward_and_help_to"], time_check_freeze=config_obj["time_check_freeze"], time_to_wait_then_reconnect=config_obj["time_to_wait_then_reconnect"], time_reset_claim_reward=config_obj["time_reset_claim_reward"], time_wait_after_nox_reset=config_obj["time_wait_after_nox_reset"], check_loading_pattern=config_obj["loading_pattern"])
        list_thread.append(memu_thr)
        list_thread[i].start()
        time.sleep(3)
        if i == 0:
            b1 = Button(gridFrame, textvariable=b0_text, width=10, command=b0_thread).pack(side=tk.LEFT)
        if i == 1:
            b2 = Button(gridFrame, textvariable=b1_text, width=10, command=b1_thread).pack(side=tk.LEFT)
        if i == 2:
            b3 = Button(gridFrame, textvariable=b2_text, width=10, command=b2_thread).pack(side=tk.LEFT)
        if i == 3:
            b4 = Button(gridFrame, textvariable=b3_text, width=10, command=b3_thread).pack(side=tk.LEFT)
        if i == 4:
            b5 = Button(gridFrame, textvariable=b4_text, width=10, command=b4_thread).pack(side=tk.LEFT)
        if i == 5:
            b6 = Button(gridFrame, textvariable=b5_text, width=10, command=b5_thread).pack(side=tk.LEFT)
        if i == 6:
            b7 = Button(gridFrame, textvariable=b6_text, width=10, command=b6_thread).pack(side=tk.LEFT)
        if i == 7:
            b8 = Button(gridFrame, textvariable=b7_text, width=10, command=b7_thread).pack(side=tk.LEFT)

    # thr = memu_process_class(0)
    # while (thr.check_GET_HELP_and_CLICK()):
    #     time.sleep(1)

    gridFrame.grid(row = 1, column = 0, padx=20)

    window.protocol("WM_DELETE_WINDOW", on_closing)

    window.mainloop()

