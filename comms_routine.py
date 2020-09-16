import email, smtplib, ssl, imaplib, time
from email import encoders
from email.header import decode_header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import weather_get as wg
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
            
        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(cf.sender_email, cf.password)
            try:
                server.sendmail(cf.sender_email, self.receiver_email, message)
            except smtplib.SMTPRecipientsRefused:
                print("Recipient refused: Are you sure " + self.receiver_email + " is the correct address?")

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
        print('mailbox length' + str(len(mail.search(None,'UnSeen')[1][0].split())))
        
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
        
        #maybe this can be all put in a config file
        if self.option_no == "1":
            subject = cf.configParser.get('option_1_text', 'subject')
            text = cf.configParser.get('option_1_text', 'text')
            html = cf.configParser.get('option_1_text', 'html')
            
            now = dt.datetime.now()
            format = "%d/%m/%Y %H:%M:%S"
            #format datetime using strftime()
            time1 = now.strftime(format)
            text = str(text) + ' ' + str(time1)
            html = str(html) + ' ' + str(time1) 
            
        elif self.option_no == "2":
            subject = "Detector Toggled"

            text =  "Ice detector has been turned off/on;"
            html = text
            
            cf.configParser.set('device_status', 'state', 1)

            
            
            
        elif self.option_no == "3":
            subject = "Detector Status"
#             #read if the detector is enabled
#             state = configParser.get('device_status', 'state')
#             if state == "1":
#                 status_io = "on"
#             else:
#                 staus_io = "off"
            text = "The detector is currently " + status_io
            html = text
            
        elif self.option_no == "4":
            subject = "Help List"
            text =  "Ice detector help functions;"
            html = text
        else:
            subject = "ERROR:"
            text = "ERROR"
            html = text
        
        return subject, text, html


        
class TwoWay(object):
    def __init__(self):
        self.mail = Alert(cf.sender_email)
    
    def readloop(self):
        flag, option_no = self.mail.read_email_choice()
        print(flag)
        print(option_no)
        
        if flag == -1:
            print("i am in the flag department")
            return -1, 0, 0, 0
        elif flag == 1:
            subject, text, html = self.mail.option_text(option_no)
            print(text)
            return 1, subject, text, html
        else:
            print("no flag")
            return 0, 0, 0, 0
        
        
    def sendresponse(self):
        
        send_confirm, subject, text, html = TwoWay.readloop(self)
                 
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
            print("you are in no mans land")
            self.mail.send_email_nf(subject, text, html)
            self.mail.read()
            
#Alert("r.agiazis@gmail.com", "Ice has been detected").send_email()
#Alert("icedetector.alert@gmail.com").send_email_file("image.jpg")
#Alert("icedetector.alert@gmail.com").read()
#Alert("icedetector.alert@gmail.com").send_report("Test" ,"hello", "hello")


