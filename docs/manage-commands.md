# Metax management commands

## Create and migrate database

`python manage.py migrate`

## Index the reference data 

`python manage.py index_refdata`

## Reload reference data to redis cache

`python manage.py reload_refdata_cache`

## Add necessary initial data to database

`python manage.py loadinitialdata`

## Add some test datasets to database

`python manage.py loaddata metax_api/tests/testdata/test_data.json` 

## Run all tests

`DJANGO_ENV=test python manage.py test --parallel --failfast --keepdb -v 0`

## Inspect current application settings

`python manage.py diffsettings --output unified --force-color`

## Execute management commands against docker swarm metax-api container

`docker exec $(docker ps -q -f name=metax-dev_metax) python manage.py check`

 docker service update --config-add source=metax-httpd-test-extra-ssl-config,target=/usr/local/apache2/conf/extra/httpd-ssl.conf --config-add source=metax-httpd-test-extra-userdir-config,target=/usr/local/apache2/conf/extra/httpd-userdir.conf --config-add source=metax-httpd-test-extra-vhosts-config,target=/usr/local/apache2/conf/extra/httpd-vhosts.conf --config-add source=metax-httpd-test-config,target=/usr/local/apache2/conf/httpd.conf --config-add source=metax-httpd-test-extra-autoindex-config,target=/usr/local/apache2/conf/extra/httpd-autoindex.conf metax-dev_apache2
 
docker service update --config-add source=fairdata-ssl-certificate,target=/usr/local/apache2/conf/server.crt --config-add source=fairdata-ssl-certificate-key,target=/usr/local/apache2/conf/server.key metax-dev_apache2