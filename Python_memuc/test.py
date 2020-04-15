import cv2

image = cv2.imread("tennis-court.png")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (3, 3), 0)
# apply Canny edge detection using a wide threshold, tight
# threshold, and automatically determined threshold
wide = cv2.Canny(blurred, 10, 200)
tight = cv2.Canny(blurred, 225, 250)
# auto = auto_canny(blurred)
# show the images
cv2.imshow("Original", image)
cv2.imshow("Edges", wide)
cv2.imshow("tight", tight)
cv2.waitKey(0)