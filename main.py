import cv2
import numpy as np 
import comms_routine as cr
import time
import ice_detector as df
from picamera.array import PiRGBArray
from picamera import PiCamera

run_once =0
off = 0

#main for loop,triggers when ice has been detected.
while(off == 0):
    
    #this ensures the basethreshold values aren't re calculated each iternation.
    #the base values are grabbed and printed once.
    if(run_once == 0):
        base = df.getBaseThreshold()
        print('Base value of pixels is: %d\n' %base)
        run_once =1
        continue
    
    #function goes to sleep for x seconds
    time.sleep(3)
    
    #grabs the new threshold value each time.
    iceTest = df.iceThreshold()
    print('Ice value pixels: %d\n' %iceTest)
    
    #checks for ice, sends emails if present, else reiterates thrugh the loop
    #off will exit the main while loop is ice is detected.
    df.iceTestEmail(iceTest,base)
    off= df.iceTest(iceTest,base)
 
#code to be executed once loop has been broken
print("Loop has been broken")