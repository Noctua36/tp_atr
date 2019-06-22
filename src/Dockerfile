FROM python:3.7-alpine

RUN apk add --update \
    nodejs \
    nodejs-npm \
  && npm i -g nodemon \
  && rm -rf /var/cache/apk/*

# COPY src/requirements.txt /
# RUN pip install -r /requirements.txt

COPY *.py /app/
WORKDIR /app

CMD [ "python", "app.py" ]
