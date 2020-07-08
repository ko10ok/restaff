FROM python:3.8

ADD src /root/app
WORKDIR /root/app

ENTRYPOINT python3.8
CMD server.py
