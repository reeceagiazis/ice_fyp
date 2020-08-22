# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import comms_routine as cr
import time
import cv2
import numpy as np 



def takeImage():
    
    
    camera = PiCamera()
    rawCapture = PiRGBArray(camera)
    # allow the camera to warmup
    time.sleep(0.5)
    # grab an image from the camera
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    camera.close()
    return image




def thresholds():
    image = takeImage()
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    B = 95
    G = 0
    R = 50
    green = np.uint8([[[B, G, R]]])
    hsvGreen = cv2.cvtColor(green,cv2.COLOR_BGR2HSV)
    lowerLimit = np.uint8([hsvGreen[0][0][0]-10,100,100])
    upperLimit = np.uint8([hsvGreen[0][0][0]+10,255,255])
    mask = cv2.inRange(hsv, lowerLimit, upperLimit)
    y=350
    x=1
    w=1000
    h=700
    cropped = mask[x:w,y:h]
    return cropped

# cropped1 = thresholds()
# cv2.imshow("frame1", cropped1)
# cv2.waitKey(0)

def getBaseThreshold():
    cropped = thresholds()
    baseWhite = cv2.countNonZero(cropped)
    base = (345 * 718) - baseWhite
    return base



def iceThreshold():
    cropped = thresholds()
    baseWhite = cv2.countNonZero(cropped)
    icePixelVal = (345 * 718) - baseWhite
    return icePixelVal

def iceTestEmail(iceThreshold,baseThreshold):
    if (iceThreshold > 1.25*baseThreshold):
        print(' ICE DETECTED')
        cr.Alert("darcy.plant@hotmail.com", "Ice has been detected real").send_email()
    
    
def iceTest(iceThreshold,baseThreshold):
    if (iceThreshold > 1.25*baseThreshold):
        off =1
        return off
    else:
        off =0
        return off



# cropped2 = thresholds()
# cv2.imshow("frame2", cropped2)
# cv2.waitKey(0)




        
            

