FROM httpd:latest

RUN apt-get update && apt-get install libapache2-mod-auth-openidc -y
RUN mkdir -p /var/www/html

EXPOSE 8080

