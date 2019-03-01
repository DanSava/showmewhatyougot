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
        sender = 'dan.sava@qfix.ro'
        password = 'fonduriue102938'
        target = 'dan.sava42@gmail.com'
        # target = 'gabriela.georgescu@gmail.com'
        msg = MIMEText(' \n'.join(urls))
        msg['Subject'] = 'Postari interesante'
        msg['From'] = sender
        msg['To'] = target

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)

        # Next, log in to the server
        server.login(sender, password)

        # Send the mail
        print("[x] Sending email to %s" % target)
        server.sendmail(sender, target, msg.as_string())

        server.quit()


class Scraper(object):
    def __init__(self):
        self.data_file = 'data.json'
        if os.path.exists(self.data_file):
            with open('data.json', 'r') as infile:
                self.processed_urls = json.load(infile)
        else:
            self.processed_urls = []

        self.words_to_find_regex = r'(3d|masurat|MMC|coordonate|masina de masurat|brat robotic|strung|freza|brat portabil|CNC)'
        self.main_url = 'https://www.fonduri-ue.ro'
        self.anunturi_url = '%s/anunturi' % self.main_url
        self.desc_regex = r'(\/desc-lot\?d=.*?)"'
        self.matchObj = None
        self.new_urls = []
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.scheduler.enter(1, 1, self.run)

    def find_in_text(self, text):
        return len(re.findall(self.words_to_find_regex, text, re.M | re.I)) > 0

    def process_url(self, url):
        if url not in self.processed_urls:
            self.processed_urls.insert(0, url)
        if len(self.processed_urls) > 30:
            self.processed_urls.pop()

    def add_url(self, url):
        if url not in self.new_urls:
            self.new_urls.append(url)

    def email_new_url(self):
        if len(self.new_urls) > 0:
            print("[x] Found something interesting", self.new_urls)
            # Send the new urls as email notification
            send_email(self.new_urls)
            self.new_urls = []

    def save_processed_urls(self):
        with open('data.json', 'w') as outfile:
            json.dump(self.processed_urls, outfile)

    def run(self):
        print("[x] Starting new run")
        response = requests.get(self.anunturi_url)
        if response.status_code == 200:
            for url_part in re.findall(r'a href="\/anunturi(\/details.*?)"', response.text,  re.M | re.I):
                anunt_url ='%s%s' % (self.anunturi_url, url_part)
                if anunt_url not in self.processed_urls:
                    anunt_resp = requests.get(anunt_url)
                    if anunt_resp.status_code == 200:
                        print("[x] Processing url %s" % anunt_url)
                        anunt_text = anunt_resp.text

                        # Find interesting words in anunt page
                        if self.find_in_text(anunt_text):
                            self.add_url(anunt_url)
                        else:
                            for match in re.findall(self.desc_regex, anunt_text, re.M | re.I):
                                desc_text = requests.get('%s%s' % (self.main_url, match)).text
                                if self.find_in_text(desc_text):
                                    self.add_url(anunt_url)
                self.process_url(anunt_url)

        self.email_new_url()
        self.save_processed_urls()
        self.scheduler.enter(600, 1, self.run)

    def start(self):
        self.scheduler.run()


if __name__ == '__main__':
    x = Scraper()
    x.start()
