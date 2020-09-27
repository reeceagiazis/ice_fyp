import cv2, time
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np 
import config_detector as cf
import ice_detector as ice
import datetime as dt
import comms_routine as cr

#variable declaration for continuous function and toggling of device functionality
run_once =0
off = 0

#instantiate object, argument is the receiver email. has been sent to sender email in this case
mail = cr.Alert(cf.sender_email)
state_c = cr.TwoWay()

#set the start date of the program for monitor # of events
cf.configParser.set('device_status', 'start_date', str(dt.datetime.now().strftime("%H:%M:%S %d/%m/%Y")))

#set the events back to 0 when initialising the program 
cf.configParser.set('device_status', 'events', 0)


while(1):
    #main for loop,triggers when ice has been detected.
    while(off == 0):
        #this ensures the basethreshold values aren't re calculated each iternation.
        #the base values are grabbed and printed once.
        #also take photo to compare with base conditions
        if(run_once == 0):
            #base = ice.getBaseThreshold()
            base = 0 #for test purposes only
            print('Base value of pixels is: %d\n' %base)
            #capture image of what the base conditions look like
            ice.takeImageSave('/home/pi/Desktop/fyp/base_cond/base_', 1)
            run_once = 1
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
        ice.iceTestEmail(iceTest,base, mail)
        off = ice.iceTest(iceTest,base)
        off = cf.configParser.set('device_status', 'state', off)
        
        #checks for new message INSIDE the loop
        state_c.sendresponse()
        
        #reads config file at the start of each iteration to see if an email has asked to turn off
        off = cf.configParser.get('device_status', 'state')
        
        print("OFF: " + str(off) + " INSIDE LOOP")

    #checks for emails while detector is OFF here, will always check AFTER starting
    state_c.sendresponse()
    #checks if off has been toggled by email
    off = cf.configParser.get('device_status', 'state')
    print("OFF: " + str(off) + " OUTSIDE LOOP")
    
        
#code to be executed once loop has been broken
print("Loop has been broken; program terminated")