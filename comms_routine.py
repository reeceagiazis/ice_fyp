import smtplib, ssl

class Alert(object):
    def __init__(self, receiver_email, message):
        self.receiver_email = receiver_email
        self.message = message
        
    def send_email(self):
        port = 465  # For SSL
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
                
Alert("r.agiazis@gmail.com", "hey").send_email()