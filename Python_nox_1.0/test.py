import subprocess
import os
import cv2
import numpy as np
from signal import signal, SIGINT
from sys import exit
import time

# wd = os.getcwd()
# os.chdir("D:\\Program Files (x86)\\Micro virt\\MEmu")

# print(os.getcwd())

# cmd = 'memuc execcmd -i {} "screencap -p"'.format(0)
# p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# image_bytes = bytearray(p.stdout.read().replace(b'\r\n', b'\n'))
# while image_bytes[0] != 0x89:
#     del image_bytes[0]
# nparr = np.frombuffer(image_bytes, np.uint8)
# image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

# # print(image_bytes)

# f = open("D:\\My_Work\\AutoGame\\Python_memuc\\PIC_TEST.txt", "wb")
# f.write(image_bytes)
# f.close()

# p.wait()


# cv2.namedWindow("image", cv2.WINDOW_NORMAL)

# # cv2.imshow('image', image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# print(os.path.getmtime('C:/Users/Admin/Nox_share/Download/screen0.png'))


from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
device = MonkeyRunner.waitForConnection()
device.touch(183, 23, MonkeyRunner.DOWN_AND_UP)
