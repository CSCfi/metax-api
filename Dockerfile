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

COPY crontab /etc/cron.d/fetch_all_reference.sh
RUN touch /var/log/cron.log
RUN chmod 0744 /etc/cron.d/fetch_all_reference.sh
RUN service cron start
# # Copy fetch_all_reference.sh file to the cron.d directory
# COPY src/metax_api/tasks/refdata/refdata_fetcher/fetch_all_reference.sh /etc/cron.d/fetch_all_reference.sh

# # Give execution rights on the cron job
# RUN chmod 0744 /etc/cron.d/fetch_all_reference.sh

# # Apply cron job
# RUN crontab /etc/cron.d/fetch_all_reference.sh

# # Create the log file to be able to run tail
# RUN touch /var/log/cron.log

# # Run the command on container startup
# CMD cron && tail -f /var/log/cron.log

# CMD ["python", "/code/manage.py", "runserver", "0.0.0.0:8008"]
CMD ["python", "manage.py", "runsslserver", "--certificate", ".certs/cert.pem","--key", ".certs/key.pem", "0.0.0.0:8008"]