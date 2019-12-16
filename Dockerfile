FROM python:3.7-alpine3.9
MAINTAINER Lucas M. Sing

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
# Copy the app folder from system to docker
COPY ./app /app

# -D is only to run the apps without root premision
RUN adduser -D user
USER user
