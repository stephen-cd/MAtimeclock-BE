FROM ubuntu:22.04
RUN apt-get update
RUN apt-get install -y apt-utils vim curl apache2 apache2-utils
RUN apt-get -y install python3 libapache2-mod-wsgi-py3

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN apt-get -y install python3-pip

RUN pip3 install --upgrade pip

WORKDIR /var/www/html
COPY . /var/www/html/

RUN DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get install tzdata

RUN pip3 install -r requirements.txt

#RUN chmod 664 /var/www/html/db.sqlite3
#RUN chown :www-data /var/www/html/db.sqlite3

#RUN mkdir -p /var/www/html/logs

RUN touch /var/www/html/access.log
RUN chmod 775 /var/www/html/access.log

RUN touch /var/www/html/error.log
RUN chmod 775 /var/www/html/error.log

RUN touch /var/www/html/last-updated.txt
RUN chmod 775 /var/www/html/last-updated.txt

RUN chown :www-data /var/www/html

RUN mkdir -p /var/www/html/static
RUN chmod 775 /var/www/html/static

#RUN chown -R www-data:www-data /var/www/html
#3RUN chmod -R 775 /var/www/html

RUN echo 'ServerName localhost' >> /etc/apache2/apache2.conf

RUN python manage.py collectstatic

ADD ./site-config.conf /etc/apache2/sites-available/000-default.conf

# set permissions of database directory to be owned by www-user
# RUN chown -R 33:33 /var/www/html/data

EXPOSE 80
#CMD ["apache2ctl", "-D", "FOREGROUND"]
CMD ["sh", "-c", "apache2ctl -D FOREGROUND & tail -f /var/www/html/*log"]
#CMD ["sh", "-c", "tail -f /var/www/html/*log"]
