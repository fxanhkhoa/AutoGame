import subprocess
import os
import cv2
import numpy as np

# adb connect localhost:21503

wd = os.getcwd()
os.chdir("C:\\adb")

p = subprocess.Popen('adb connect localhost:21503', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

for line in p.stdout.readlines():
    print (line)

retval = p.wait()

p = subprocess.Popen("adb exec-out screencap -p", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# print(p.stdout.read())
image_bytes = p.stdout.read().replace(b'\r\n', b'\n')

# print(image_bytes)
# f = open('screenCap.png', 'wb')
# f.write(image_bytes)
# f.close()
nparr = np.frombuffer(image_bytes, np.uint8)
image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
print(nparr.shape, image.shape)
cv2.imwrite("screenCap.png", image)
cv2.imshow("screen", image)
cv2.waitKey(0)
cv2.destroyWindow("")
retval = p.wait()