FROM python:3.9-alpine

MAINTAINER "falcoeye team"

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 80

COPY . .

CMD [ "python3", "falcoeye.py" ]
