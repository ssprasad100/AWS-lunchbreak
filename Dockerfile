FROM python:3.5
ENV PYTHONUNBUFFERED 1

MAINTAINER Andreas Backx

RUN mkdir /code
WORKDIR /code

# uWSGI
RUN apt-get update
RUN apt-get install -y \
    libpcre3 \
    libpcre3-dev
RUN pip install uwsgi

# Arguments
ARG version
ARG certificate_type
ARG requirements_file=requirements.txt
ARG db_name=LB_${version}
ARG db_user=LB_${version}
ARG db_pass=''
ARG db_host='db'
ARG STATIC_ROOT='/var/lunchbreak/static'
ARG MEDIA_ROOT='/var/lunchbreak/media'
ARG MEDIA_PRIVATE_ROOT='/var/lunchbreak/media-private'

# Environment
ENV DB_NAME ${db_name}
ENV DB_USER ${db_user}
ENV DB_PASS ${db_pass}
ENV DB_HOST ${db_host}
ENV certificates_path "/etc/lunchbreak/certificates/apns"
ENV BUSINESS_APNS_CERTIFICATE "${certificates_path}/business_${certificate_type}.pem"
ENV CUSTOMERS_APNS_CERTIFICATE "${certificates_path}/customers_${certificate_type}.pem"
ENV DJANGO_SETTINGS_VERSION ${version}
ENV MEDIA_ROOT ${MEDIA_ROOT}
ENV PRIVATE_MEDIA_ROOT ${PRIVATE_MEDIA_ROOT}

# Setting up entrypoint
ADD ./docker/web/docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

# Code
RUN pip install -r ${requirements_file} --exists-action w
ADD ./lunchbreak /code/
