import email, smtplib, ssl, imaplib, time, cv2, glob, os
import numpy as np
from email import encoders
from email.header import decode_header
from picamera import PiCamera
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import weather_get as wg
import ice_detector as ice
import config_detector as cf
import datetime as dt


class Alert(object):
    def __init__(self, receiver_email):
        self.receiver_email = receiver_email
        port = 465  # For SSL
    
    def send_email_file(self, filename, subject, text_in, html):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = cf.sender_email
        message["To"] = self.receiver_email
        self.text_in = text_in
        self.html = html
        

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(self.text_in, "plain")
        part2 = MIMEText(self.html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)


                
        try:
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
                
        except NameError:
            message = 'error: no file found'
            print('error: no file found')

    def send_email_nf(self, subject, text_in, html):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = cf.sender_email
        message["To"] = self.receiver_email
        self.text_in = text_in
        self.html = html
        

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(self.text_in, "plain")
        part2 = MIMEText(self.html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)
        text = message.as_string()
        
        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(cf.sender_email, cf.password)
            try:
                server.sendmail(cf.sender_email, self.receiver_email, text)
            except smtplib.SMTPRecipientsRefused:
                print("Recipient refused: Are you sure " + self.receiver_email + " is the correct address?")
               

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
            
    def read_email_choice(self):
        
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        (retcode, capabilities) = mail.login(cf.sender_email,cf.password)
        mail.list()
        mail.select('inbox')
        print('Unread messages: ' + str(len(mail.search(None,'UnSeen')[1][0].split())))
        
        search = "choice"
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
        else:
            print('no new messages; no error or no choice')
            return 0, 0
        

    def ice_trigger(self):
        #gather datetime and format it
        now = dt.datetime.now()
        format_subject = "%H-%M-%S_%d-%m-%Y"
        format1 = "%H:%M:%S %d/%m/%Y"
        #format datetime using strftime()
        self.time = now.strftime(format_subject)
        time1 = now.strftime(format1)
        
        #get weather object to show in email
        weather = wg.get_weather_forecast()
        #'temp','precip','snow_depth','wind_dir','wind_spd'
        self.w_data = weather.queryWeather()
        #load in the html slab
        html = cf.html_trigger
        
        print('HTML READ INIT.')
        #print(html)
        
        ########################
        #attachment section
        #take photo of current scene
        still = '/home/pi/Desktop/fyp/base_cond/base_'
        still = ice.takeImageSave(still, 1)
        
        
        #concatenate the image taken with the one initially taken
        output_destination = '/home/pi/Desktop/fyp/event/event_' + self.time + '.jpg'
        im1 = cv2.imread(still)
        
        #quick and dirty code to find last created base scene in folder
        list_recent_loc = glob.glob('/home/pi/Desktop/fyp/base_cond/*')
        latest_file = max(list_recent_loc, key = os.path.getctime)
        
        #read latest file from base conditions
        im2 = cv2.imread(latest_file)
        vis = np.concatenate((im1, im2), axis = 0)
        cv2.imwrite(output_destination, vis)
        
        
        ########################
        
        
        #encode the image and embed into html
        part = MIMEBase("application", "octet-stream")
        part.set_payload(vis)
        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        
        #add the variables into the slab
        a=cf.location
        b="#"+cf.dev
        c=time1
        d=cf.configParser.get("device_status", "events")
        e = part
        
        replacements = [a,b,c,d, e]
        
        for i in range(3):
            search_no = "!"*(1+i)
            search = "&lt;" + search_no + "&gt;"         
            html = html.split(search)
            html.insert(1, replacements[i])
            html = ''.join(html)
            
        subject = a + '  (' + b + ') ' + " has detected ice at " + c
        text = "beautify html then send through"
        


        self.send_email_file(output_destination, subject, text, html)
        

    def send_report(self, subject, text, html):
        #lert("icedetector.alert@gmail.com").send_email_file("image.jpg")
        curr_weather = wg.get_weather_forecast()
        save_file = curr_weather.save_data()
        
        # Create the plain-text and HTML version of your message
        self.text = text
        self.html = html
        self.subject = subject
        self.send_email_file(save_file, self.subject, self.text, self.html)

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
            text = cf.text_reset
            html = cf.html_reset
            
            #append datetime to end of subject line
            text = str(text) + ' ' + str(time1)
            html = str(html) + ' ' + str(time1) 
            
            cf.configParser.set('device_status', 'state', 0)

            
            
        elif self.option_no == "toggle":
            #toggles the state of the detector off/on
            text = cf.text_toggle
            html = cf.html_toggle
            
            #append datetime to end of subject line
            text = str(text) + ' ' + str(time1)
            html = str(html) + ' ' + str(time1) 
            
            #conditional to toggle the states of the detector
            if cf.configParser.get('device_status', 'state') == 0:
                cf.configParser.set('device_status', 'state', 1)
                toggle_text = " ON "
            elif cf.configParser.get('device_status', 'state') == 1:
                cf.configParser.set('device_status', 'state', 0)
                toggle_text = " OFF "

            #split and insert state + time into subject
            subject = cf.subject_toggle + ' ' +  time1
            subject = subject.split("<->")
            subject.insert(1, toggle_text)
            subject = "".join(subject)
            
        elif self.option_no == "report":
            #compile a photo of current scene, weather report and send them to own email
            subject = cf.subject_report + ' ' + time1
            text = cf.text_report
            html = cf.html_report

            #append datetime to end of subject line
            text = str(text) + ' ' + str(time1)
            html = str(html) + ' ' + str(time1) 
            
            #get current time for saving file names, different format due to OS issues
            format = "%d-%m-%Y_%H-%M-%S" 
            time1 = now.strftime(format) #format datetime using strftime()
            
            #save the current weather information
            curr_weather = wg.get_weather_forecast()
            weather_plot = curr_weather.save_data()
            
            #take picture and return array
            camera = PiCamera()
            camera.resolution = (1920, 1080)
            still = '/home/pi/Desktop/fyp/stills/' + time1 + '.jpg'
            camera.capture(still)
            camera.close() #essential
            
            #concatenate the newly saved images to be sent
            output_destination = '/home/pi/Desktop/fyp/reports/report_' + time1 + '.jpg'
            im1 = cv2.imread(still)
            im2 = cv2.imread(weather_plot)
            vis = np.concatenate((im1, im2), axis = 0)
            cv2.imwrite(output_destination, vis)
            
            
            
#             #read if the detector is enabled
#             state = cf.configParser.get('device_status', 'state')
#             if state == "1":
#                 status_io = "on"
#             else:
#                 staus_io = "off"
          #  text = "The detector is currently " + status_io
            #html = text
            
        elif self.option_no == "help":
            #help email that displays what the display does etc
            subject = cf.subject_help
            subject = subject + ' ' +  time1
            text = cf.text_help
            html = cf.html_help
        else:
            #if none of these options are chosen, then the an error message is produced
            subject = "<!> ERROR, no choice has been detected"
            text = "<!> ERROR, no choice has been detected"
            html = "<!> ERROR, no choice has been detected"
        
        return subject, text, html


        
class TwoWay(object):
    def __init__(self):
        self.mail = Alert(cf.sender_email)        
        
    def readloop(self):
        self.flag, self.option_no = self.mail.read_email_choice()
        print("Flag state: " + str(self.flag))
        print("Requested option: " +  str(self.option_no))
        
        if self.flag == -1:
            print("You shouldn't be here.")
            return -1, 0, 0, 0
        elif self.flag == 1:
            subject, text, html = self.mail.option_text(self.option_no)
            print("Choice of text: " + text)
            return 1, subject, text, html
        else:
            print("No flag detected.")
            return 0, 0, 0, 0
        
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
    
    def sendresponse(self):
        #receive information from inbox
        send_confirm, subject, text, html = TwoWay.readloop(self)
        
        #append device name to subject
        subject = self.append_device_location_name(subject)
        
        #make class for converting html and then convert
        if html != 0:
            html_parse = HtmlRead(self.option_no, html)
            html = html_parse.replace()
        
        if send_confirm == 1:
            self.mail.send_email_nf(subject, text, html) #change this to a html email with no attach
        elif send_confirm == -1:
            pass
        elif send_confirm == 0:
            pass
        else:
            text = "Check that your intial request for help was in the right format"
            html = text #make a nice looking html for this and store it in the config, can be the help file
            subject = "Error: Check the help request is correct"
            #this coulg also be the same as the ask for help option
            print("Request not possible, try again.")
            self.mail.send_email_nf(subject, text, html)
            self.mail.read()
          
#reads custom html file for each page and splits by the unique identifier codes, then replaces

class HtmlRead(object):
    def __init__(self, option_no, html):
        #gather datetime and format it
        now = dt.datetime.now()
        format_subject = "%H:%M:%S %d/%m/%Y"
        #format datetime using strftime()
        self.time = now.strftime(format_subject)
        
        print('HTML READ INIT.')
        print(html)
        print(option_no)
        
        self.option_no = option_no
        self.html = html
        #Splits the list by the <!> operator, unique enough to not cause problems
        self.html.split('&lt;!&gt;')
        
        #get weather object to show in email
        weather = wg.get_weather_forecast()
        #'temp','precip','snow_depth','wind_dir','wind_spd'
        self.w_data = weather.queryWeather()
        
    def replace_reset(self):
        a=cf.location
        b="#"+cf.dev
        c=self.time
        d=str(self.w_data[0]['temp'])
        e=self.w_data[0]['wind_spd']
        e=str('% 12.1f'%e)
        f=str(self.w_data[0]['wind_cdir_full'])
        g=str(self.w_data[0]['snow_depth'])
        h=str(self.w_data[0]['precip'])
        
        replacements = [a,b,c,d,e,f,g,h]
        
        for i in range(8):
            search_no = "!"*(1+i)
            search = "&lt;" + search_no + "&gt;"         
            self.html = self.html.split(search)
            self.html.insert(1, replacements[i])
            self.html = ''.join(self.html)
       
    def replace_toggle(self):
        a=cf.location
        b="#"+cf.dev
        c=cf.configParser.get('device_status', 'state')
        if c == 0:
            c = "ON"
        elif c == 1:
            c = "OFF"
            
        d=self.time
        e=str(self.w_data[0]['temp'])
        f=self.w_data[0]['wind_spd']
        f=str('% 12.1f'%f)
        
        g=str(self.w_data[0]['wind_cdir_full'])
        h=str(self.w_data[0]['snow_depth'])
        i=str(self.w_data[0]['precip'])
        
        replacements = [a,b,c,d,e,f,g,h,i]
        
        for i in range(9):
            search_no = "!"*(1+i)
            search = "&lt;" + search_no + "&gt;"         
            self.html = self.html.split(search)
            self.html.insert(1, replacements[i])
            self.html = ''.join(self.html)
    
    def replace_report(self):
        pass
    
    def replace_help(self):
        pass
    
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
    
    
#Alert("r.agiazis@gmail.com", "Ice has been detected").send_email()
#Alert("icedetector.alert@gmail.com").send_email_file("image.jpg")
#Alert("icedetector.alert@gmail.com").read()
#Alert("icedetector.alert@gmail.com").send_report("Test" ,"hello", "hello")


