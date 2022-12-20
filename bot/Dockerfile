FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]


#FROM ubuntu:latest
#
#RUN apt-get update && apt-get install -y python3.11 python3.11-distutils
#
#RUN apt-get install -y vim
#
#RUN apt-get install -y python3.pip
#
#CMD [ "python", "main.py" ]