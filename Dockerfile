FROM python:3.5
ENV PYTHONUNBUFFERED 1

MAINTAINER Andreas Backx

ARG version
ARG certificate_type

# Environment
ENV DB_NAME LB_${version}
ENV DB_USER LB_${version}
ENV certificates_path "/etc/lunchbreak/certificates/apns"
ENV BUSINESS_APNS_CERTIFICATE "${certificates_path}/business_${certificate_type}.pem"
ENV CUSTOMERS_APNS_CERTIFICATE "${certificates_path}/customers_${certificate_type}.pem"
ENV DJANGO_SETTINGS_VERSION ${version}
ENV MEDIA_ROOT /var/lunchbreak/media
ENV MEDIA_PRIVATE_ROOT /var/lunchbreak/media-private

# uWSGI
RUN apt-get update
RUN apt-get install -y \
    libpcre3 \
    libpcre3-dev
RUN pip install uwsgi

# Setting up entrypoint
ADD ./docker/web/docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

# Code
RUN mkdir /code
WORKDIR /code
ADD ./lunchbreak /code/
RUN pip install -r requirements.txt --exists-action w
RUN python manage.py collectstatic --noinput -c

ENTRYPOINT ["/docker-entrypoint.sh"]
