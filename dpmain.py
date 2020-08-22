import cv2
import numpy as np 
import comms_routine as cr
import time
import darcy_functions as df
from picamera.array import PiRGBArray
from picamera import PiCamera

run_once =0
off = 0
while(1):
    
    if(run_once == 0):
        base = df.getBaseThreshold()
        print('Base value of pixels is: %d\n' %base)
        run_once =1
        continue
        
    time.sleep(3)
    iceTest = df.iceThreshold()
    print('Ice value pixels: %d\n' %iceTest)
    
    if(off ==0):
        df.iceTest(off,iceTest,base)
        continue
    