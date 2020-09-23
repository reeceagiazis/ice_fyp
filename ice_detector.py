# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import comms_routine as cr
import time
import cv2
import numpy as np 
import config_detector as cf


#This funtion turns the pi camera on and takes an image, once the camera has finished
#taking an image the camera saves the image into an array and returns this array. Once
#this is done, the camera closes so the function can be recalled without an error.

def takeImage():
    
    
    camera = PiCamera()
    rawCapture = PiRGBArray(camera)
    # allow the camera to warmup
    time.sleep(0.5)
    # grab an image from the camera
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    #turns off the camera
    camera.close()
    return image




#This fucntions grabs the image taken by the camera and thresholds them based on an
#(R,G,B) value that is preset. This is then compared, if the values are in the range the
#pixels are shown. This is then converted to a black and white image based on if a
#certain RGB value is present (called mask). Once this black and white image has been
#created, the image is then cropped around the wire, this reduces the error with
#differnt lighting levels. The cropped image is returned out of the function.


def thresholds():
    
    #grabs the image from the takeImage() fn
    image = takeImage()
    #converts image from R,G,B to Hue saturation value.
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    #sets the tresholding values for the comparioson
    B = 95
    G = 0
    R = 50
    #converts to the required colour threshold to uint8
    blue = np.uint8([[[B, G, R]]])
    hsvBlue = cv2.cvtColor(blue,cv2.COLOR_BGR2HSV)
    
    #sets the range for the thresholding
    lowerLimit = np.uint8([hsvBlue[0][0][0]-10,100,100])
    upperLimit = np.uint8([hsvBlue[0][0][0]+10,255,255])
    #applies the thresholding to image and outputs that image.
    mask = cv2.inRange(hsv, lowerLimit, upperLimit)
    
    #sets the values to crop
    y=350
    x=1
    w=1000
    h=700
    
    #crops the image
    cropped = mask[x:w,y:h]
    return cropped

# cropped1 = thresholds()
# cv2.imshow("frame1", cropped1)
# cv2.waitKey(0)



#this function runs once and counts the number of pixels that aren't blue. This is used
#as the base value to compare to.

def getBaseThreshold():
    
    cropped = thresholds()
    #counts white pixels, then uses 1 - white to find black pixels.
    baseWhite = cv2.countNonZero(cropped)
    base = (345 * 718) - baseWhite
    return base

#this function is periodically triggered in main, basically the same as
#getBaseThreshold() except this is used as the comparison value. Returns the comparison
#pixel values


def iceThreshold():
    cropped = thresholds()
    baseWhite = cv2.countNonZero(cropped)
    icePixelVal = (345 * 718) - baseWhite
    return icePixelVal

#This function take the base and the latest ice threshold and does a comparison. If the
#value is greater then 1.25 x the base. The wire has "grown" or ice has been formed.
#An email is then sent through the comms_routine.py

def iceTestEmail(iceThreshold,baseThreshold):
    if (iceThreshold > 1.25*baseThreshold):
        print(' ICE DETECTED')
        #cr.Alert("darcy.plant@hotmail.com").send_email("Ice has been detected real")
 
#very similar to iceTestEmail(), except this ensures the email function is only sent once
#and the program stops.
    
def iceTest(iceThreshold,baseThreshold):
    if (iceThreshold > 1.25*baseThreshold):
        off = 1
        cf.configParser.set('device_status', 'state', off)

        return off
    else:
        off =0
        return off



# cropped2 = thresholds()
# cv2.imshow("frame2", cropped2)
# cv2.waitKey(0)




        
            

