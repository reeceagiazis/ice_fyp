import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Alert(object):
    def __init__(self, receiver_email):
        self.receiver_email = receiver_email
        
        port = 465  # For SSL
        self.password = "FYP2020COVID19"
        email_address = "icedetector.alert@gmail.com"
        self.sender_email = email_address
    
    def send_email_file(self, filename):
        message = MIMEMultipart("alternative")
        message["Subject"] = "multipart test"
        message["From"] = self.sender_email
        message["To"] = self.receiver_email

        # Create the plain-text and HTML version of your message
        text = """\
        Hi,
        How are you?
        Real Python has many great tutorials:
        www.realpython.com"""
        html = """\
        <html>
          <body>
            <p>Ice has been detected<br>
            </p>
          </body>
        </html>
        """

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

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
                server.login(self.sender_email, self.password)
                try:
                    server.sendmail(self.sender_email, self.receiver_email, text)
                except smtplib.SMTPRecipientsRefused:
                    print("Recipient refused: Are you sure " + self.receiver_email + " is the correct address?")
                
        except NameError:
            print("no file name")
            
        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(self.sender_email, self.password)
            try:
                server.sendmail(sender_email, self.receiver_email, self.message)
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
           

# class Read(object):
#     def __init__(self, receiver_email, message):
#         self.receiver_email = receiver_email
#         self.message = message
        
        
        
#Alert("r.agiazis@gmail.com", "Ice has been detected").send_email()
Alert("icedetector.alert@gmail.com").send_email_file("image.jpg")