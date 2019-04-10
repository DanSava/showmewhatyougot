FROM python:3.5

ADD main.py /
ADD key_words.json /
ADD requirements.txt /

RUN pip install -r requirements.txt
CMD [ "python", "-u", "./main.py" ]