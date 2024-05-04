FROM python:3.9-aplpine3.13
LABEL maintainer="wistler4u@gmail.com"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt