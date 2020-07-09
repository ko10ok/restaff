FROM python:3.8

ADD requirements.txt /tmp/requirements.txt
RUN python3.8 -m pip install -r /tmp/requirements.txt

ADD src /root/app
WORKDIR /root/app

CMD python3.8 server.py
