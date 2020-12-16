FROM python:3.6

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /code

COPY requirements.txt /code/

RUN apt-get update && apt install xqilla libxerces-c-dev build-essential libssl-dev libffi-dev python-dev libxqilla-dev cron -y

RUN pip install --upgrade pip wheel
RUN pip install -r requirements.txt

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

COPY crontab /etc/cron.d/reference_data
RUN touch /var/log/cron.log
RUN chmod 0744 /etc/cron.d/reference_data

# COPY src/.ssh /code/.ssh
# RUN eval $(ssh-agent) && \
#     echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config && \
#     chmod 0700 /code/.ssh && \
#     chmod 0600 /code/.ssh/id_rsa.github && \
#     ssh-add -k /code/.ssh/id_rsa.github && \
#     git clone git@github.com:CSCfi/metax-refdata.git

# COPY src/metax_api/tasks/refdata/refdata_fetcher/resources/gitconfig /code/metax-refdata/.git/config

CMD ["python", "manage.py", "runsslserver", "--certificate", ".certs/cert.pem","--key", ".certs/key.pem", "0.0.0.0:8008"]