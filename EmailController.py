from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

class EmailController:
    def __init__(self):
        self.msg = MIMEMultipart()
        self.server = smtplib.SMTP('smtp.gmail.com: 587')

    def write(self, email, password, subject, messageText):
        self.msg['From'] = self.msg['To'] = email
        self.password = password
        self.msg['Subject'] = subject
        self.msg.attach(MIMEText(messageText, "plain"))

    def send(self):
        self.server.starttls()
        self.server.login(self.msg["From"], self.password)
        self.server.sendmail(self.msg["From"], self.msg["To"], self.msg.as_string())
        self.server.quit()
        print("email enviado")
