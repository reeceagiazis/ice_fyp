import email, smtplib, ssl, imaplib, os, re
from email import encoders
from email.header import decode_header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import weather_get as wg
import config_detector as cf


class Alert(object):
    def __init__(self, receiver_email):
        self.receiver_email = receiver_email
        port = 465  # For SSL
    
    def send_email_file(self, filename, text, html):
        self.message = MIMEMultipart("alternative")
        self.message["Subject"] = "multipart test"
        self.message["From"] = cf.sender_email
        self.message["To"] = self.receiver_email
        self.text = text
        self.html = html
        

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(self.text, "plain")
        part2 = MIMEText(self.html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        self.message.attach(part1)
        self.message.attach(part2)


                
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
            self.message.attach(part)
            self.text = message.as_string()

            # Log in to server using secure context and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.sender_email, self.password)
                try:
                    server.sendmail(self.sender_email, self.receiver_email, self.text)
                except smtplib.SMTPRecipientsRefused:
                    print("Recipient refused: Are you sure " + self.receiver_email + " is the correct address?")
                
        except NameError:
            pass
            
        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(cf.sender_email, cf.password)
            try:
                server.sendmail(cf.sender_email, self.receiver_email, self.message)
            except smtplib.SMTPRecipientsRefused:
                print("Recipient refused: Are you sure " + self.receiver_email + " is the correct address?")
                
    def send_email(self, message):
        port = 465  # For SSL
        self.message = message
        password = "FYP2020COVID19"
        email_address = "icedetector.alert@gmail.com"
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
        imap.login(self.username, self.password)
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
            
    def read_email_choice():
        subject, option = Alert("icedetector.alert@gmail.com").read()
        search = "choice"
        
        #splits the html div into an array
        a = option.replace(">", " ",)
        b = a.replace("<", " ")
        option = b.split()
        print(option)
        print(subject)

        #only returns the choice if the subject is choice, else will return 0
        if subject == search:
            return option[2]
        else:
            print("No choice found in email")
            return 0

    def send_report(self, text, html):
        #lert("icedetector.alert@gmail.com").send_email_file("image.jpg")
        curr_weather = wg.get_weather_forecast()
        save_file = curr_weather.save_data()
        
        # Create the plain-text and HTML version of your message
        self.text = text
        self.html = html
        
        self.send_email_file(save_file, self.text, self.html)
        
        

        
#Alert("r.agiazis@gmail.com", "Ice has been detected").send_email()
#Alert("icedetector.alert@gmail.com").send_email_file("image.jpg")
#Alert("icedetector.alert@gmail.com").read()
Alert("icedetector.alert@gmail.com").send_report()