import subprocess
import os
import cv2
import numpy as np
from signal import signal, SIGINT
from sys import exit
import time
import json

from ultility.memu_process import memu_process_class

list_thread = []

NUM_OF_THREAD = 1

### Input Signal
def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    for thread in list_thread:
        thread.stop_thread()
    exit(0)



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
    #### Process
    for i in range(0, NUM_OF_THREAD):
        print("creating {}".format(i))
        memu_thr = memu_process_class(i, pic_folder = config_obj["picture_share_folder"])
        list_thread.append(memu_thr)
        list_thread[i].start()

    # thr = memu_process_class(0)
    # while (thr.check_GET_HELP_and_CLICK()):
    #     time.sleep(1)

    while True:
        pass
