FROM python:3.8
ENV TZ=Europe/Kiev

RUN python3 -m pip install --upgrade pip
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
WORKDIR /app
