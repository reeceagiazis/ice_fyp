import cv2
import numpy as np 
from picamera.array import PiRGBArray
from picamera import PiCamera 

def nothing(x):    
    pass

cv2.namedWindow("Trackbars")
 
cv2.createTrackbar("B", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("G", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("R", "Trackbars", 0, 255, nothing)

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 15

rawCapture = PiRGBArray(camera, size=camera.resolution)



for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    B = 180
    G = 0
    R = 60
    
    #B = cv2.getTrackbarPos("B", "Trackbars")
    #G = cv2.getTrackbarPos("G", "Trackbars")
    #R = cv2.getTrackbarPos("R", "Trackbars")

    green = np.uint8([[[B, G, R]]])
    hsvGreen = cv2.cvtColor(green,cv2.COLOR_BGR2HSV)
    lowerLimit = np.uint8([hsvGreen[0][0][0]-10,100,100])
    upperLimit = np.uint8([hsvGreen[0][0][0]+10,255,255])

    mask = cv2.inRange(hsv, lowerLimit, upperLimit)
    x=0
    y=100
    h=500
    w=640
    cropped = mask[x:w,y:h]
    

    result = cv2.bitwise_and(image  , image , mask=mask)
    
    
    cv2.imshow("frame", image)
    
   
    key1 = cv2.waitKey(0)
    if key1 == ord('t'):
        baseWhite = cv2.countNonZero(cropped)
        baseBlack = (400 * 475) - baseWhite
        #print('Base value of pixels is %d\n' %baseBlack) #prints them
        
    elif key1 == 27:  
        break
    
    
    key = cv2.waitKey(0)
    if key == ord(' '): #press space to start


        whitePixels = cv2.countNonZero(cropped) #counts the white pixels
        #print('Number of white pixels is: %d' %whitePixels) #prints them
        blackPixels = (400 * 475) - whitePixels   
        #print(' # pixels is: %d' %blackPixels) #prints them
        if blackPixels > 1.1*baseBlack:
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(image,"Ice Detected",(10,250), font, 2,(255,255,255),2,cv2.LINE_AA,0)
            cv2.imshow("frame", image)
    
    
    elif key == 27:  #escape key 
        break

    key = cv2.waitKey(1)
    rawCapture.truncate(0)
    if key == 27: 
        break

cv2.destroyAllWindows()
