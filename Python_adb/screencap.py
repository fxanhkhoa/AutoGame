import subprocess
import os
import cv2
import numpy as np

lower = np.uint8([0,0,0])

def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cropping
    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True
        print(x, y)
        # BGR color
        print(image[y][x])
        arr = []
        arr2 = []
        print(image.shape)
        for i in range(341, 351):
            #print(image[584][i])
            arr.append(image[312][i])
            # cv2.circle(image,(i, 300), 10, (255,0,255))
        # print(arr)
        # print("==============")
        # for i in range(455, 505):
        #     #print(image[473][i])
        #     arr2.append(image[473][i])
        #     # cv2.circle(image,(i,473), 10, (255,0,255))
        # print(arr2)
    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        refPt.append((x, y))
        cropping = False
        # draw a rectangle around the region of interest
        cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)
        cv2.imshow("image", image)

def process(frame):
   #frame = cv2.resize(frame, (320, 160))
   
   #frame = frame[90:160, 0:320]

   ##### Tracking bar #######
   l_h = cv2.getTrackbarPos("L - H", "image")
   l_s = cv2.getTrackbarPos("L - S", "image")
   l_v = cv2.getTrackbarPos("L - V", "image")
   u_h = cv2.getTrackbarPos("U - H", "image")
   u_s = cv2.getTrackbarPos("U - S", "image")
   u_v = cv2.getTrackbarPos("U - V", "image")

   hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

   # define range of white color in HSV
   lower = np.array([l_h, l_s, l_v])
   upper = np.array([u_h, u_s, u_v])
   mask = cv2.inRange(hsv, lower, upper)

   white_mask = cv2.inRange(hsv, lower, upper)
   
   result = cv2.bitwise_and(frame, frame, mask = white_mask)

   cv2.imshow('image', result)

def nothing(x):
    pass

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

retval = p.wait()

print(nparr.shape, image.shape)
cv2.imwrite("screenCap.png", image)
# cv2.resize(image, (640, 360), interpolation = cv2.INTER_AREA)

# For Get Mouse Coordinate
cv2.namedWindow("image", cv2.WINDOW_NORMAL)
cv2.resizeWindow('Resized Window', 640, 360)

# Set Mouse Callback
cv2.setMouseCallback("image", click_and_crop)

work_with_track_bar = False


while (True):
    # image = cv2.imread('252.png')
    # image = frame.array
    if work_with_track_bar:
        process(image)
    else:
        cv2.imshow('image', image)
    #   print('1 frame: ', time.time() - timeStart)

    if cv2.waitKey(1) & 0xFF == ord('t'):
        cv2.createTrackbar("L - H", "image", 0, 179, nothing)
        cv2.createTrackbar("L - S", "image", 0, 255, nothing)
        cv2.createTrackbar("L - V", "image", 0, 255, nothing)
        cv2.createTrackbar("U - H", "image", 179, 179, nothing)
        cv2.createTrackbar("U - S", "image", 255, 255, nothing)
        cv2.createTrackbar("U - V", "image", 255, 255, nothing)
        work_with_track_bar = True
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
   
   # cap.release()
cv2.destroyAllWindows()
