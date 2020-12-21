FROM python:3.6

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /code

RUN apt-get update && apt install xqilla libxerces-c-dev build-essential libssl-dev libffi-dev python-dev libxqilla-dev nano less cron -y

COPY requirements.txt /code/

# RUN pip install --upgrade pip wheel
# RUN pip install -r requirements.txt

EXPOSE 8008
EXPOSE 8006

ARG METAX_DATABASE_HOST
ARG REDIS_HOST
ARG RABBITMQ_HOST
ARG RABBIT_MQ_PASSWORD=guest
ARG RABBIT_MQ_USER=guest
ARG ELASTIC_SEARCH_HOST

ENV METAX_DATABASE_HOST $METAX_DATABASE_HOST
ENV REDIS_HOST $REDIS_HOST
ENV RABBIT_MQ_HOSTS $RABBITMQ_HOST
ENV RABBIT_MQ_PASSWORD $RABBIT_MQ_PASSWORD
ENV RABBIT_MQ_USER $RABBIT_MQ_USER
ENV ELASTIC_SEARCH_HOSTS $ELASTIC_SEARCH_HOST

ADD cron_git_setup.sh /cron_git_setup.sh
RUN ["chmod", "+x", "/cron_git_setup.sh"]
ENTRYPOINT ["/cron_git_setup.sh"]

# CMD ["python", "manage.py", "runsslserver", "--certificate", ".certs/cert.pem","--key", ".certs/key.pem", "0.0.0.0:8008"]