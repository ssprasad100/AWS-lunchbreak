#!/bin/bash

if [ -d "/var/secrets" ]; then
    tmpfile="$(mktemp)"
    for file in /var/secrets/*
    do
        if [ -f $file ]; then
            file_contents=$(head -1 $file)
            filename=$(basename "$file")
            underscored_filename="${filename//-/_}"
            capitalized_filename=${underscored_filename^^}
            echo "export $capitalized_filename=\"$file_contents\"" >> $tmpfile
        fi
    done

    source $tmpfile
    rm -f $tmpfile
fi

# Need to find a way so secrets are no longer available after initialisation,
# then the directory can be deleted.
#rm -rf /var/secrets
python manage.py migrate --no-input 1> /dev/null
python manage.py collectstatic --noinput -c 1> /dev/null

export C_FORCE_ROOT=true

celery -A Lunchbreak worker \
    -l debug \
    --detach \
    --logfile="/var/lunchbreak/log/%n%I.log"

uwsgi \
    --chdir=/code/ \
    --module=Lunchbreak.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=Lunchbreak.settings \
    --env DJANGO_SETTINGS_VERSION="${DJANGO_SETTINGS_VERSION}" \
    --env MEDIA_ROOT="${MEDIA_ROOT}" \
    --env PRIVATE_MEDIA_ROOT="${PRIVATE_MEDIA_ROOT}" \
    --env DB_NAME="${DB_NAME}" \
    --env DB_USER="${DB_USER}" \
    --env DB_PASS="${DB_PASS}" \
    --env DB_HOST="${DB_HOST}" \
    --env BUSINESS_APNS_CERTIFICATE="${BUSINESS_APNS_CERTIFICATE}" \
    --env CUSTOMERS_APNS_CERTIFICATE="${CUSTOMERS_APNS_CERTIFICATE}" \
    --env GOOGLE_CLOUD_SECRET="${GOOGLE_CLOUD_SECRET}" \
    --env GOCARDLESS_ACCESS_TOKEN="${GOCARDLESS_ACCESS_TOKEN}" \
    --env GOCARDLESS_WEBHOOK_SECRET="${GOCARDLESS_WEBHOOK_SECRET}" \
    --env GOCARDLESS_APP_CLIENT_ID="${GOCARDLESS_APP_CLIENT_ID}" \
    --env GOCARDLESS_APP_CLIENT_SECRET="${GOCARDLESS_APP_CLIENT_SECRET}" \
    --env GOCARDLESS_APP_WEBHOOK_SECRET="${GOCARDLESS_APP_WEBHOOK_SECRET}" \
    --env EMAIL_HOST_USER="${EMAIL_HOST_USER}" \
    --env EMAIL_HOST_PASSWORD="${EMAIL_HOST_PASSWORD}" \
    --env PLIVO_AUTH_ID="${PLIVO_AUTH_ID}" \
    --env PLIVO_AUTH_TOKEN="${PLIVO_AUTH_TOKEN}" \
    --env OPBEAT_APP_ID="${OPBEAT_APP_ID}" \
    --env OPBEAT_SECRET_TOKEN="${OPBEAT_SECRET_TOKEN}" \
    --master \
    --pidfile=/tmp/lunchbreak.pid \
    --socket=0.0.0.0:49152 \
    --processes=5 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum

exec "$@"
