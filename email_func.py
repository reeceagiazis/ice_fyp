import smtplib, ssl

class Alert(object):
    def send_email(receiver_email, message):
        port = 465  # For SSL
        password = "FYP2020COVID19"
        email_address = "icedetector.alert@gmail.com"
        sender_email = email_address

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(email_address, password)
            try:
                server.sendmail(sender_email, receiver_email, message)
            except smtplib.SMTPRecipientsRefused:
                print("Recipient refused: Are you sure " + receiver_email + " is the correct address?")