#!/usr/bin/env sh

set -ex

if echo "${*}" | grep -q "gun\|runserver";then
    if [ -n "${DJANGO_SUPERUSER_PASSWORD}" ] &&
    [ -n "${DJANGO_SUPERUSER_USERNAME}" ] &&
    [ -n "${DJANGO_SUPERUSER_EMAIL}" ];then
        python manage.py createsuperuser --noinput || :
    fi
    # TODO: Use flock so this only runs once
    python manage.py migrate
    python manage.py collectstatic --noinput -v 0
fi

exec "$@"
