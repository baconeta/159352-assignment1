# syntax=docker/dockerfile:1
FROM python:3.10.0a2-slim-buster
RUN pip3 install requests
COPY . /src
WORKDIR /src
CMD python server.py $PORT
# EXPOSE 8080