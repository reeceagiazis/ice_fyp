import cv2
import numpy as np 
import comms_routine as cr
import time
from picamera.array import PiRGBArray
from picamera import PiCamera 

def nothing(x):    
    pass

class create_windows():
    def start_id(resolution_x, resolution_y, framerate):
        print("Initialising windows..")
    
        #create trackbars for adjusting recognition param (usually left commented out)
        cv2.namedWindow("Trackbars")
        cv2.createTrackbar("B", "Trackbars", 0, 255, nothing)
        cv2.createTrackbar("G", "Trackbars", 0, 255, nothing)
        cv2.createTrackbar("R", "Trackbars", 0, 255, nothing)

        #initiate rpi camera 
        camera = PiCamera()
        camera.resolution = (resolution_x, resolution_y)
        camera.framerate = camera.framerate
        rawCapture = PiRGBArray(camera, size=camera.resolution)

        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            image = frame.array
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            B = 95
            G = 0
            R = 50
            
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
                #cv2.imshow("mask", mask)
                #print('Base value of pixels is %d\n' %baseBlack) #prints them
                
            elif key1 == 27:  
                break
            
            
            key = cv2.waitKey(0)
            if key == ord(' '): #press space to start

                blackPixels=0   
                whitePixels = cv2.countNonZero(cropped) #counts the white pixels
                #print('Number of white pixels is: %d' %whitePixels) #prints them
                #blackPixels = (400 * 475) - whitePixels   
                print(' # pixels is: %d' %blackPixels) #prints them
                cv2.imshow("frame", image)
                if blackPixels > 1.25*baseBlack:
                    
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(image,"Ice Detected",(10,250), font, 2,(255,255,255),2,cv2.LINE_AA,0)
                    print(' ICE DETECTED') #prints them
                    cr.Alert("darcy.plant@hotmail.com", "Ice has been detected real").send_email()
                    time.sleep(0.5)
                    
            
                
            
            elif key == 27:  #escape key 
                break

            key = cv2.waitKey(1)
            rawCapture.truncate(0)
            if key == 27: 
                break
            
    def close_program():
        cv2.destroyAllWindows()


#main loop for script (like c)
cr.Alert.send_email("r.agiazis@gmail.com", "hey")

create_windows.start_id(640, 480, 15)
create_windows.close_program()
