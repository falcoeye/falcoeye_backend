FROM python:3.9-slim

MAINTAINER "falcoeye team"

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update && \
    apt-get install -y git && \
    apt-get -y install gcc musl-dev libffi-dev libpq-dev netcat && \
    apt-get clean && \
    pip3 install -U pip && \
    pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install gunicorn

EXPOSE 8000

COPY . .
RUN chmod +x /usr/src/app/entrypoint.sh

CMD ["/usr/src/app/entrypoint.sh"]
