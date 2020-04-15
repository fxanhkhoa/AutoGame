import subprocess
import os
import cv2
import numpy as np
from signal import signal, SIGINT
from sys import exit

from ultility.screen_process import screen_process_class

### Input Signal
def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    screen_process_class.stop_thread()
    exit(0)



if __name__ == '__main__':
    # Tell Python to run the handler() function when SIGINT is recieved
    signal(SIGINT, handler)

    ### Connect
    wd = os.getcwd()
    os.chdir("C:\\adb")

    p = subprocess.Popen('adb connect localhost:21503', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for line in p.stdout.readlines():
        print (line)

    retval = p.wait()

    print('Running. Press CTRL-C to exit.')
    #### Process

    scr_process = screen_process_class(1)

    scr_process.start()

    scr_process.go_to_arena()
    scr_process.go_to_arena_3_vs_3_and_fight()