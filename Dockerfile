FROM aprimediet/alpine-python-nginx:latest
LABEL maintainer="<Muhamad Aditya Prima> aditya.prima@qti.co.id"

ENV MONGO_HOST=sentiment-mongo

# Install required dependencies
RUN apk add --no-cache openssl-dev libffi-dev

# SET WORKDIR
WORKDIR /usr/local/app

ADD deploy /
ADD crawler ./crawler
ADD scrapy.cfg .
ADD requirements.txt .

# INSTALL REQUIRED DEPENDENCIES
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80 443 6080
