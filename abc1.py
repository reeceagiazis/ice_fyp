import cv2
import numpy as np 
from picamera.array import PiRGBArray
from picamera import PiCamera 
#test
#comment
#newtest

#hello!!!
def nothing(x):    
    pass
 
cv2.namedWindow("Trackbars")
 
cv2.createTrackbar("B", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("G", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("R", "Trackbars", 0, 255, nothing)

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 16

rawCapture = PiRGBArray(camera, size=(640, 480))

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    B = 240
    G = 110
    R = 150

    green = np.uint8([[[B, G, R]]])
    hsvGreen = cv2.cvtColor(green,cv2.COLOR_BGR2HSV)
    lowerLimit = np.uint8([hsvGreen[0][0][0]-10,100,100])
    upperLimit = np.uint8([hsvGreen[0][0][0]+10,255,255])

    mask = cv2.inRange(hsv, lowerLimit, upperLimit)

    result = cv2.bitwise_and(image  , image , mask=mask)

    cv2.imshow("frame", image)
    
    key = cv2.waitKey(0)
    if key == ord(' '): #press space to start
        
        cv2.imshow("mask", mask) #shows the mask
        whitePixels = cv2.countNonZero(mask) #counts the white pixels
        print('Number of white pixels is: %d' %whitePixels) #prints them
        blackPixels = (640 * 480) - whitePixels
        print('Number of black pixels is: %d' %blackPixels)
        blackPixels = 0
        whitePixels = 0
    
    elif key == 27:  #escape key 
        break

    key = cv2.waitKey(1)
    rawCapture.truncate(0)
    if key == 27:
        break

cv2.destroyAllWindows()
