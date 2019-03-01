import requests
import re
import json
import sched
import time
import os
from email.mime.text import MIMEText
import smtplib


def send_email(urls):
    if urls is not None and len(urls) > 0:
        sender = 'hexagon.mi.ro@gmail.com'
        password = 'fonduriue102938'
        target = 'dan.sava42@gmail.com'
        # target = 'gabriela.georgescu@gmail.com'
        msg = MIMEText(' \n'.join(urls))
        msg['Subject'] = 'Postari interesante'
        msg['From'] = sender
        msg['To'] = target

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        # Next, log in to the server
        server.login(sender, password)

        # Send the mail
        print("[x] Sending email to %s" % target)
        server.sendmail(sender, target, msg.as_string())

        server.quit()

send_email(["test"])