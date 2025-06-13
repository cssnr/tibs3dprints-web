FROM python:3.12-alpine AS python

ENV TZ=UTC
ENV PYTHONDONTWRITEBYTECODE=1

#RUN apk add --update --no-cache alpine-sdk mysql-dev gcc libffi-dev musl-dev
RUN apk add --update --no-cache alpine-sdk mysql-dev

COPY requirements.txt /
RUN python3 -m pip install --no-cache-dir -U pip  &&\
    python3 -m pip install --no-cache-dir -r /requirements.txt


FROM python:3.12-alpine

LABEL org.opencontainers.image.source="https://github.com/cssnr/tibs3dprints-web"
LABEL org.opencontainers.image.description="Django 5 Boiler Plate"
LABEL org.opencontainers.image.authors="smashedr"

ENV TZ=UTC
ENV PYTHONDONTWRITEBYTECODE=1

COPY --from=python /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=python /usr/local/bin/ /usr/local/bin/

RUN addgroup -g 1000 app  &&\
    adduser -S -H -h /app -s /sbin/nologin -u 1000 -G app app  &&\
    mkdir -p /app /data /data/static  &&  chown -R app:app /app /data /data/static  &&\
    apk add --no-cache curl mysql-dev

WORKDIR /app
COPY --chown=app:app . .
USER app
ENTRYPOINT ["sh", "docker-entrypoint.sh"]
