import cv2
import numpy as np 
import comms_routine as cr
import time
import ice_detector as ice
from picamera.array import PiRGBArray
from picamera import PiCamera
import config_detector as cf

run_once =0
off = 0

#instantiate object, argument is the receiver email. has been sent to sender email in this case
mail = cr.Alert(cf.sender_email)
state_c = cr.TwoWay()


while(1):
    
 
        
        #main for loop,triggers when ice has been detected.
    while(off == 0):
        
        #this ensures the basethreshold values aren't re calculated each iternation.
        #the base values are grabbed and printed once.
        if(run_once == 0):
            base = ice.getBaseThreshold()
            print('Base value of pixels is: %d\n' %base)
            run_once =1
            continue
        
        #function goes to sleep for x seconds, set by hours and minutes
        hours = 0
        minutes = 0 
        seconds = 1
        x = 3600*hours + 60*minutes + seconds
        time.sleep(x)
        
        #grabs the new threshold value each time.
        iceTest = ice.iceThreshold()
        print('Ice value pixels: %d\n' %iceTest)
        
        #checks for ice, sends emails if present, else reiterates thrugh the loop
        #off will exit the main while loop is ice is detected.
        ice.iceTestEmail(iceTest,base)
        off = ice.iceTest(iceTest,base)
        off = cf.configParser.set('device_status', 'state', 0)
        
        #checks for new message INSIDE the loop
        state_c.sendresponse()
        
        #reads config file at the start of each iteration to see if an email has asked to turn off
        off = cf.configParser.get('device_status', 'state')
        
        print("OFF: " + str(off) + " INSIDE LOOP")

    #checks for emails while detector is OFF here, will alwasy check AFTER starting
    state_c.sendresponse()
    #checks if off has been toggled by email
    off = cf.configParser.get('device_status', 'state')
    print("OFF: " + str(off) + " OUTSIDE LOOP")
    

        
#code to be executed once loop has been broken
print("Loop has been broken; program terminated")