import cv2
import numpy as np 
import comms_routine as cr
import time
import ice_detector as df
from picamera.array import PiRGBArray
from picamera import PiCamera

run_once =0
off = 0
while(off == 0):
    
    if(run_once == 0):
        base = df.getBaseThreshold()
        print('Base value of pixels is: %d\n' %base)
        run_once =1
        continue
        
    time.sleep(3)
    iceTest = df.iceThreshold()
    print('Ice value pixels: %d\n' %iceTest)
    df.iceTestEmail(iceTest,base)
    off= df.iceTest(iceTest,base)
 

print("Loop has been broken")