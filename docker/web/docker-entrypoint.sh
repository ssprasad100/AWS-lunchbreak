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

uwsgi \
    --chdir=/code/ \
    --module=Lunchbreak.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=Lunchbreak.settings \
    --env DJANGO_SETTINGS_VERSION="${DJANGO_SETTINGS_VERSION}" \
    --env MEDIA_ROOT="${MEDIA_ROOT}" \
    --env PRIVATE_MEDIA_ROOT="${PRIVATE_MEDIA_ROOT}" \
\
    --env DB_NAME="${DB_NAME}" \
    --env DB_USER="${DB_USER}" \
    --env DB_PASS="${DB_PASS}" \
    --env DB_HOST="${DB_HOST}" \
\
    --env BUSINESS_APNS_CERTIFICATE="${BUSINESS_APNS_CERTIFICATE}" \
    --env CUSTOMERS_APNS_CERTIFICATE="${CUSTOMERS_APNS_CERTIFICATE}" \
    --env GOOGLE_CLOUD_SECRET="${GOOGLE_CLOUD_SECRET}" \
\
    --env GOCARDLESS_ACCESS_TOKEN="${GOCARDLESS_ACCESS_TOKEN}" \
    --env GOCARDLESS_WEBHOOK_SECRET="${GOCARDLESS_WEBHOOK_SECRET}" \
    --env GOCARDLESS_APP_CLIENT_ID="${GOCARDLESS_APP_CLIENT_ID}" \
    --env GOCARDLESS_APP_CLIENT_SECRET="${GOCARDLESS_APP_CLIENT_SECRET}" \
    --env GOCARDLESS_APP_WEBHOOK_SECRET="${GOCARDLESS_APP_WEBHOOK_SECRET}" \
\
    --env EMAIL_HOST_USER="${EMAIL_HOST_USER}" \
    --env EMAIL_HOST_PASSWORD="${EMAIL_HOST_PASSWORD}" \
\
    --master \
    --pidfile=/tmp/lunchbreak-master.pid \
    --socket=0.0.0.0:49152 \
    --processes=5 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum

exec "$@"
