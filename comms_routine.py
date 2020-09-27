import email, smtplib, ssl, imaplib, time, cv2, glob, os, base64, io
import numpy as np
from gpiozero import CPUTemperature
from email import encoders
from email.header import decode_header
from picamera import PiCamera
from bs4 import BeautifulSoup
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import weather_get as wg
import ice_detector as ice
import config_detector as cf
import datetime as dt

#Alert Class
#The main email functionality resides here, with a function to send and read emails as they come into the inbox

class Alert(object):
    def __init__(self, receiver_email):
        self.receiver_email = receiver_email
        port = 465  # For SSL
        
        #instantiate a class wide copy of the current weather data
        self.curr_weather = wg.get_weather_forecast()
        self.weather_plot = self.curr_weather.save_data()
    
    def send_email_file(self, filename, subject, text_in, html):
        #setting up email format to be send to own device
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = cf.sender_email
        message["To"] = self.receiver_email
        self.text_in = text_in
        self.html = html
    
        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text_in, 'plain')
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        #catch for if there is no file attached, doubly redundant coding
        #with the if statement, the catch should never be caught
        try:
            if filename != 0:
                # Open PDF file in binary mode
                with open(filename, "rb") as attachment:
                    # Add file as application/octet-stream
                    # Email client can usually download this automatically as attachment
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                # Encode file in ASCII characters to send by email    
                encoders.encode_base64(part)

                # Add header as key/value pair to attachment part
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
                )
                part.add_header('Content-Id', '<disp_image>')

                # Add attachment to message and convert message to string
                message.attach(part)
                text = message.as_string()

                # Log in to server using secure context and send email
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(cf.sender_email, cf.password)
                    try:
                        server.sendmail(cf.sender_email, self.receiver_email, text)
                    except smtplib.SMTPRecipientsRefused:
                        print("Recipient refused: Are you sure " + self.receiver_email + " is the correct address?")
            elif filename == 0:
               text = message.as_string()
               # Create secure connection with server and send email
               context = ssl.create_default_context()
               with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                   server.login(cf.sender_email, cf.password)
                   try:
                       server.sendmail(cf.sender_email, self.receiver_email, text)
                   except smtplib.SMTPRecipientsRefused:
                       print("Recipient refused: Are you sure " + self.receiver_email + " is the correct address?")
               
        except NameError:
            message = 'error: no file found'
            print('error: no file found')

#Send a simple text email to the device
#Good for debugging purposes and left in only as the base for the attachment code
#Source: www.realpython.com/python-send-email/
            
    def send_email(self, message):
        port = 465  # For SSL
        self.message = message
        password = cf.password
        email_address = cf.sender_email
        sender_email = email_address

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(email_address, password)
            try:
                server.sendmail(sender_email, self.receiver_email, self.message)
                
            except smtplib.SMTPRecipientsRefused:
                print("Recipient refused: Are you sure " + self.receiver_email + " is the correct address?")

#Reading inbox the device's Gmail Account
#Fetch the most recent message using IMAP. Used to check if user has request information
#Source: www.thepythoncode.com/article/reading-emails-in-python
                
    def read(self):
        imap = imaplib.IMAP4_SSL("imap.gmail.com")   
        imap.login(cf.sender_email, cf.password)
        status, messages = imap.select("INBOX")
        # number of top emails to fetch
        N = 1
        # total number of emails
        messages = int(messages[0])
        
        for i in range(messages, messages-N, -1):
            # fetch the email message by ID
            res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode()
                # email sender
                from_ = msg.get("From")
                #print("Subject:", subject)
                #print("From:", from_)
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()

                        
                #print("="*100)
                imap.close()
                imap.logout()
                
                return subject, body

#Read Email Choice
#Using the previous function, read(), this function parses the text and checks if the user has sent the keyword (eg. request)
#Splits HTML into something simply readable by a loop to see if the request is in the right format
            
    def read_email_choice(self):
        
        #Quick way to check how many messages are unread in the inbox (can be change to a custom folder)
        #This can be commented out, used for debugging
#         mail = imaplib.IMAP4_SSL('imap.gmail.com')
#         (retcode, capabilities) = mail.login(cf.sender_email,cf.password)
#         mail.list()
#         mail.select('inbox')
#         print('Unread messages: ' + str(len(mail.search(None,'UnSeen')[1][0].split())))
        
        #search is the keyword to be looked for in the subject line
        search = "request"
        subject, option = Alert(cf.sender_email).read()

        #checks emails first for unread message
        if subject == search:
            #splits the html div into an array
            a = option.replace(">", " ",)
            b = a.replace("<", " ")
            option = b.split()
            #only returns the choice if the subject is choice, else will return 0
            flag = 1
            return flag, option[2]
        elif subject == "Error: Check the help request is correct":
            flag = -1
            print("error found; incorrect type")
            return flag, 0
        elif subject == cf.configParser.get('responses', 'last_response'):
            print('no new messages; no error or no choice;last response was correct')
            return 0, 0
        else:
            return 0, 0 
        
#Ice Trigger
#If ice is detected, this function is called and the email is sent to the account with some information about the detected ice.
    def ice_trigger(self, base_threshold, ice_threshold):        
        #gather datetime and format it
        now = dt.datetime.now()
        format_subject = "%H-%M-%S_%d-%m-%Y"
        format1 = "%H:%M:%S %d/%m/%Y"
        #format datetime using strftime()
        self.time = now.strftime(format_subject)
        time1 = now.strftime(format1)
        
        self.bt = str(base_threshold)
        self.it = str(ice_threshold)

        #write to a file the current date and time of when the event was triggered
        f = open('event/event_history.txt', "a")
        f.write("Event recorded at " + time1 + " with base threshold of " + self.bt + " and ice threshold of " + self.it + "\n")
        f.close()
        
        #get weather object to show in email
        weather = wg.get_weather_forecast()
        #'temp','precip','snow_depth','wind_dir','wind_spd'
        self.w_data = weather.queryWeather()
        #load in the html slab
        html = cf.html_trigger
        
        #DEBUGGING ONLY
        #print('HTML READ INIT.')
        #print(html)
        
        #attachment section: creates a concatenated image to be attached to the email 
        #create output filename for event image to be attached
        output_destination = '/home/pi/Desktop/fyp/event/event_' + self.time + '.jpg'

        #take photo of current scene
        still = '/home/pi/Desktop/fyp/stills/triggered_'
        still = ice.takeImageSave(still, 1)
        
        
        #concatenate the image taken with the one initially taken
        im1 = cv2.imread(still)
        
        #quick and dirty code to find last created base scene in folder
        list_recent_loc = glob.glob('/home/pi/Desktop/fyp/base_cond/*')
        latest_file = max(list_recent_loc, key = os.path.getctime)
        
        #read latest file from base conditions
        im2 = cv2.imread(latest_file)
        vis = np.concatenate((im1, im2), axis = 0)
        cv2.imwrite(output_destination, vis)
        
        #embed image into html
        html_img = '<img style="display: block; margin-left: auto; margin-right: auto;" src="cid:disp_image" alt="&quot;Base" width="576" height="648" align="middle" />'
        
        #add the variables into the slab of html 
        a=cf.location #device location
        b="#"+cf.dev #device number
        c=time1 #current time
        d=str(cf.configParser.get("device_status", "events")) #number of triggered ice events
        
        #a simple grammar check to change event from to events depending on the no. events
        if d == '1':
            e = 'event'
        else:
            e =  'events'

        f = str(cf.configParser.get('device_status', 'start_date')) #time when main.py was first run
        g = str(html_img) #image of html code
        replacements = [a,b,c,d,e,f,g] #list to make the next cond. statements easy
        
        #checks for <!n> where n is number of ! and then replaces them.
        for i in range(7):
            search_no = "!"*(1+i)
            search = "&lt;" + search_no + "&gt;"         
            html = html.split(search)
            html.insert(1, replacements[i])
            html = ''.join(html)
        
        #add current data into subject line
        subject = a + '  (' + b + ') ' + " has detected ice at " + c
        
        #convert html into text
        soup = BeautifulSoup(html, features="html.parser")
        text = soup.get_text()

        #gatehr all the information and send it out
        self.send_email_file(output_destination, subject, text, html)

#Option_Text
#Checks which option has been input and will return the appropriate html, text and subject line for the mail
    def option_text(self, option_no_in):
        self.option_no = option_no_in
        
        #gather datetime and format it
        now = dt.datetime.now()
        format_subject = "%H:%M:%S %d/%m/%Y"
        #format datetime using strftime()
        time1 = now.strftime(format_subject)
        
        if self.option_no == "reset":
            #resets the state of the detector (OFF = 0), like a perma-on button
            subject = cf.subject_reset + ' ' +  time1
            html = cf.html_reset        
            cf.configParser.set('device_status', 'state', 0)
            attachment = 0
            
            #capture image of what the base conditions look like
            ice.takeImageSave('/home/pi/Desktop/fyp/base_cond/base_', 1)

        elif self.option_no == "toggle":
            #toggles the state of the detector off/on
            html = cf.html_toggle
        
            
            #conditional to toggle the states of the detector
            if cf.configParser.get('device_status', 'state') == 0:
                cf.configParser.set('device_status', 'state', 1)
                toggle_text = " OFF "
            elif cf.configParser.get('device_status', 'state') == 1:
                cf.configParser.set('device_status', 'state', 0)
                toggle_text = " ON "

            #split and insert state + time into subject
            subject = cf.subject_toggle + ' ' +  time1
            subject = subject.split("<->")
            subject.insert(1, toggle_text)
            subject = "".join(subject)
            
            attachment = 0

            
        elif self.option_no == "report":
            #compile a photo of current scene, weather report and send them to own email
            #get current time for saving file names, different format due to OS issues
            format = "%d-%m-%Y_%H-%M-%S" 
            time2 = now.strftime(format) #format datetime using strftime()
            
            #take picture and return array
            camera = PiCamera()
            camera.resolution = (1920, 1080)
            still = '/home/pi/Desktop/fyp/stills/' + time2 + '.jpg'
            camera.capture(still)
            camera.close() #essential
            
            #concatenate the newly saved images to be sent
            output_destination = '/home/pi/Desktop/fyp/reports/report_' + time2 + '.jpg'
            im1 = cv2.imread(still)
            im2 = cv2.imread(self.weather_plot)
            vis = np.concatenate((im1, im2), axis = 0)
            cv2.imwrite(output_destination, vis)
            
            html = cf.html_report
            attachment = output_destination
            subject = cf.subject_report
            subject = subject + ' ' +  time1

 
        elif self.option_no == "help":
            #help email that displays what the display does etc
            subject = cf.subject_help
            subject = subject + ' ' +  time1
            html = cf.html_help
            attachment = 0

        else:
            #if none of these options are chosen, then the an error message is produced
            subject = "<!> ERROR, no choice has been detected"
            text = "<!> ERROR, no choice has been detected"
            html = "<!> ERROR, no choice has been detected"
            attachment = 0
            
        #convert html into text
        soup = BeautifulSoup(html, features="html.parser")
        text = soup.get_text()
        
        return attachment, subject, text, html

#Class TwoWay
#Using the functions set up in the Alert class, this class is responsible for the two way communiucation between the user and the device
    #and allows them to fetch data by sending in requests.
    
class TwoWay(object):
    def __init__(self):
        #Instan
        self.mail = Alert(cf.sender_email)        
    
    #Read Loop:  reads and returns a different variables to the response email and ensures that the same email isn't continuiously sent
    def readloop(self):
        self.flag, self.option_no = self.mail.read_email_choice()
        print("Flag state: " + str(self.flag))
        print("Requested option: " +  str(self.option_no))
        
        #an imporbable state, used for debugging but happens every once in a while
        if self.flag == -1:
            print("Received an email outside the scope of the read functions.")
            return -1, 0, 0, 0, 0
        #normal state; what regularly is entered
        elif self.flag == 1:
            attachment, subject, text, html = self.mail.option_text(self.option_no)
            #print("Choice of text: " + text)
            return 1, attachment, subject, text, html
        #what happens when a repsonse from the device has been read, this makes sure that there is no feedback loop of 1000 emails
        else:
            print("No flag detected.")
            return 0, 0, 0, 0, 0

#Appends the device name and location to all the subject lines.
    def append_device_location_name(self, subject):
        #split the subject and add in the device name and number if there is text
        
        if subject == 0:
            pass
        else:
            subject = subject.split('<!>')
            subject.insert(0, ' (#' + cf.dev + ')')
            subject.insert(0, cf.location)
            subject = " ".join(subject)
        
        return subject

#Colects the data and flags sent by the other functions and puts together an email response for the user
    def sendresponse(self):
        #receive information from inbox
        send_confirm, attachment, subject, text, html = TwoWay.readloop(self)
        
        print('Send Confirm state: ' + str(send_confirm))
        #append device name to subject
        subject = self.append_device_location_name(subject)
        
        #make class for converting html and then convert
        if html != 0 :
            html_parse = HtmlRead(self.option_no, html)
            html = html_parse.replace()
        
        #the normal state is below; 
        if send_confirm == 1:
            self.mail.send_email_file(attachment, subject, text, html)
        #if send_conifrm is not 1, then usually the user entered the wrong request for help.
        elif send_confirm == 0:
            print('Waiting for new message...')
        elif send_confirm == -1:
            text = "Check that your intial request for help was in the right format"
            html = text #make a nice looking html for this and store it in the config, can be the help file
            subject = "Error: Check the help request is correct"
            #this coulg also be the same as the ask for help option
            print("Request not possible, try again.")
            self.mail.send_email_file(attachment, subject, text, html)

        cf.configParser.set('responses', 'last_response', subject)

          
#HtmlRead class that reads custom html file for each page and splits by the unique identifier codes, then replaces the identifiers
#with device information
class HtmlRead(object):
    def __init__(self, option_no, html):
        #gather datetime and format it
        self.now = dt.datetime.now()
        format_subject = "%H:%M:%S %d/%m/%Y"
        #format datetime using strftime()
        self.time = self.now.strftime(format_subject)
        
#         print('HTML READ INIT.')
#         print(html)
#         print(option_no)
        
        self.option_no = option_no
        self.html = html
        #Splits the list by the <!> operator, unique enough to not cause problems
        self.html.split('&lt;!&gt;')
        
        #get weather object to show in email
        weather = wg.get_weather_forecast()
        #'temp','precip','snow_depth','wind_dir','wind_spd'
        self.w_data = weather.queryWeather()

#replaces the html when the reset option have been requested. 
    def replace_reset(self):
        a=cf.location #device location
        b="#"+cf.dev #device number
        c=self.time #current time
        d=str(self.w_data[0]['temp']) #current temperature
        e=self.w_data[0]['wind_spd'] #current wind speed
        e=str('% 12.1f'%e) #format current wind speed
        f=str(self.w_data[0]['wind_cdir_full']) #current wind direction
        g=str(self.w_data[0]['snow_depth']) #current snow depth
        h=str(self.w_data[0]['precip']) #current precipitaion level
        
        replacements = [a,b,c,d,e,f,g,h]
        
        #searches for the identifier then replaces
        for i in range(8):
            search_no = "!"*(1+i)
            search = "&lt;" + search_no + "&gt;"         
            self.html = self.html.split(search)
            self.html.insert(1, replacements[i])
            self.html = ''.join(self.html)

#replaces the html when the TOGGLE option have been requested. 
    def replace_toggle(self):
        a=cf.location
        b="#"+cf.dev
        c=str(cf.configParser.get('device_status', 'state'))
        if c == '0':
            c = "ON"
        elif c == '1':
            c = "OFF"
            
        d=self.time
        e=str(self.w_data[0]['temp'])
        f=self.w_data[0]['wind_spd']
        f=str('% 12.1f'%f)
        
        g=str(self.w_data[0]['wind_cdir_full'])
        h=str(self.w_data[0]['snow_depth'])
        i=str(self.w_data[0]['precip'])
        
        replacements = [a,b,c,d,e,f,g,h,i]
        
        #searches for the identifier then replaces
        for i in range(9):
            search_no = "!"*(1+i)
            search = "&lt;" + search_no + "&gt;"         
            self.html = self.html.split(search)
            self.html.insert(1, replacements[i])
            self.html = ''.join(self.html)

#replaces the html when the report option have been requested. 
    def replace_report(self):
            cpu = CPUTemperature()

            #embed image into html
            html_img = '<img style="display: block; margin-left: auto; margin-right: auto;" src="cid:disp_image" alt="&quot;Base" width="576" height="648" align="middle" />'
        
            #add the variables into the slab
            a=cf.location #!
            b="#"+cf.dev #!!
            c=self.time #!!!
            state_check=cf.configParser.get('device_status', 'state') #!!!!
            
            #check for state int then convert to text
            if int(state_check) == 1:
                d = 'OFF'
            elif int(state_check) == 0:
                d = 'ON'
            
            #check for number of events that have occurred
            e=str(cf.configParser.get("device_status", "events")) #!!!!!
            
            #grammar replacement check
            if e == '1': 
                f = 'event' #!!!!!!
            else:
                f =  'events' #!!!!!!

            g = str(cf.configParser.get('device_status', 'start_date')) #!!!!!!!
            h = str(html_img) #!!!!!!!!
            i = cpu.temperature
            
            replacements = [a,b,c,d,e,f,g,h,i]
            
            for i in range(9):
                search_no = "!"*(1+i)
                search = "&lt;" + search_no + "&gt;"         
                self.html = self.html.replace(search, str(replacements[i]))
            
            
            w_meta=self.w_data[0]['weather']

            #weather data; self explanatory mostly
            d0 = w_meta["description"]
            d1=str(self.w_data[0]['temp'])
            d2=str(max([x['temp'] for x in self.w_data]))
            d3=str(min([x['temp'] for x in self.w_data]))
            d4=str(self.w_data[0]['snow_depth'])
            d5=str(self.w_data[0]['precip'])
            d6=str(self.w_data[0]['wind_spd'])+' m/s '+str(self.w_data[0]['wind_cdir_full'])
            d7=str(self.w_data[0]['clouds'])
            d8=str(max([x['uv'] for x in self.w_data])) #uv index
            d9=str(max([x['rh'] for x in self.w_data])) #relative humidity
            data_weather = [d0,d1,d2,d3,d4,d5,d6,d7,d8,d9]
            
            for i in range(10):
                search_no = "d" +str(i)
                search = "&lt;" + search_no + "&gt;"         
                self.html = self.html.replace(search, str(data_weather[i]))
                
            #append list of events since creation
            f = open('event/event_history.txt','r')
            event_html = ''
            while True:
                #get new line of text from file
                line = f.readline()
                #if line empty; eof reached
                if not line:
                    break
                event_html += '<p style="text-align: center;">' + line + '</p>'
                
            self.html = self.html.replace('<table></table>', event_html)
            f.close()
            
            #attach weather icon to email as attachment
            self.html = self.html.replace('&lt;w_icon&gt;', w_meta["icon"])

            
#replaces the html when the help option have been requested; currently a place holder for future improvemtns
    def replace_help(self):
        pass

#where the decision making happens on which item to replace
    def replace(self):
        
        if self.option_no == 'reset':
            self.replace_reset()
        elif self.option_no == 'toggle':
            self.replace_toggle()
        elif self.option_no == 'report':
            self.replace_report()
        elif self.option_no == 'help':
            self.replace_help()
        
        return self.html



