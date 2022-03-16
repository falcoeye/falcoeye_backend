FROM python:3.9-alpine

MAINTAINER "falcoeye team"

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev \
    && pip3 install -U pip \
    && pip3 install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

RUN pip3 install gunicorn

EXPOSE 8000

COPY . .

CMD ["gunicorn", "-w 3", "-b :8000", "falcoeye:app"]
