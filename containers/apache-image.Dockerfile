FROM httpd:latest

RUN apt-get update && apt-get install libapache2-mod-auth-openidc -y

EXPOSE 80

