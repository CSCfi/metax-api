#!/bin/bash

# should be in Dockerfile but for some reason not working from there ATM
pip install --upgrade pip wheel
pip install -r /code/docker_data/requirements.txt

chmod -R 0777 /code/docker_data

# add permissions for scripts cron is using
# fetcher scripts should be running ONLY on one environment, can be handled by giving only to one env read/write ssh key
chmod 0777 /code/metax_api/tasks/refdata/refdata_fetcher/fetch_all_reference.sh
chmod 0777 /code/metax_api/tasks/refdata/refdata_fetcher/weekly_merge_refdata.sh
chmod 0777 /code/metax_api/tasks/refdata/refdata_indexer/reindex_all.sh

cp -r /code/.ssh /root/.ssh
git clone git@github.com:CSCfi/metax-refdata.git

chmod -R 0777 /code/metax-refdata

# add git configurations for git user and email
cp /code/docker_data/gitconfig /code/metax-refdata/.git/config

# create cron logging file, add cron job for root user and check it's there
touch /var/log/cron.log
cp /code/docker_data/crontab /var/spool/cron/crontabs/root
crontab -l

# restart cron and check it's running
service cron restart
service cron status

# start metax-api
python manage.py runsslserver --certificate .certs/cert.pem --key .certs/key.pem 0.0.0.0:8008
