FROM fairdata-docker.artifactory.ci.csc.fi/fairdata-centos7-systemd:latest

RUN yum install mod_auth_openidc httpd mod_ssl mod_php mod_security mod_security_crs -y; yum clean all; systemctl enable httpd.service
RUN mkdir -p /var/www/html

EXPOSE 8080

CMD ["/usr/sbin/init"]

