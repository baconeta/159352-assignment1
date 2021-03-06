# syntax=docker/dockerfile:1
FROM python:3.10.0a2-slim-buster
RUN pip3 install requests
COPY . /src
WORKDIR /src
# EXPOSE 8080
CMD python server.py $PORT