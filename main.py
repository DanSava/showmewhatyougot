import requests
import re
import json
import sched
import time
from email.mime.text import MIMEText
import smtplib
import logging


def send_email(url):
    if url:
        sender = 'dan.sava@qfix.ro'
        password = 'fonduriue102938'
        target = 'dan.sava42@gmail.com'
        # target = 'gabriela.georgescu@gmail.com'
        msg = MIMEText(' \n'.join(url))
        msg['Subject'] = 'Postari interesante'
        msg['From'] = sender
        msg['To'] = target

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)

        # Next, log in to the server
        server.login(sender, password)

        # Send the mail
        logger.info("Sending email to %s" % target)
        server.sendmail(sender, target, msg.as_string())

        server.quit()


class Scraper(object):
    def __init__(self, logger):
        self.logger = logger
        self.processed_urls = []
        self.words_to_find_regex = None
        self.main_url = 'https://www.fonduri-ue.ro'
        self.anunturi_url = '%s/anunturi' % self.main_url
        self.desc_regex = r'(\/desc-lot\?d=.*?)"'
        self.matchObj = None
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
        if url not in self.processed_urls:
            self.processed_urls.append(url)

    def email_new_url(self, url):
        self.logger.info("Found something interesting: ", url)
        # Send the new url as email notification
        send_email(url)

    def load_key_words(self):
        with open('key_words.json', 'r') as f:
            loaded_words = json.load(f)
        self.words_to_find_regex = r'({})'.format(loaded_words['words'])

    def run(self):
        self.logger.info("Starting new run")
        try:
            self.load_key_words()
            response = requests.get(self.anunturi_url)
            if response.status_code == 200:
                for url_part in re.findall(r'a href="\/anunturi(\/details.*?)"', response.text,  re.M | re.I):
                    anunt_url ='%s%s' % (self.anunturi_url, url_part)
                    if anunt_url not in self.processed_urls:
                        anunt_resp = requests.get(anunt_url)
                        if anunt_resp.status_code == 200:
                            logging.info("Processing url %s" % anunt_url)
                            anunt_text = anunt_resp.text

                            # Find interesting words in anunt page
                            if self.find_in_text(anunt_text):
                                self.email_new_url(anunt_url)
                            else:
                                for match in re.findall(self.desc_regex, anunt_text, re.M | re.I):
                                    desc_text = requests.get('%s%s' % (self.main_url, match)).text
                                    if self.find_in_text(desc_text):
                                        self.email_new_url(anunt_url)
                    self.process_url(anunt_url)
        except Exception as e:
            self.logger.error(e)

        self.scheduler.enter(600, 1, self.run)

    def start(self):
        self.scheduler.run()


if __name__ == '__main__':
    logger = logging.getLogger('croller')
    logger.setLevel(logging.INFO)
    # create console handler and set level to info
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter
    formatter = logging.Formatter('[%(levelname)s]-%(asctime)s: %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    x = Scraper(logger)
    x.start()
