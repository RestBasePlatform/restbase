FROM ubuntu:18.04

ENV LANG de_DE.UTF-8
ENV PG_VERSION 9.6
ENV PG_PASSWORD password
ENV PG_BASE /var/lib/postgresql
ENV PG_PASSWORD_FILE ${PG_BASE}/pwfile
ENV PG_DATA ${PG_BASE}/${PG_VERSION}/main
ENV PG_CONFIG_DIR /etc/postgresql/${PG_VERSION}/main
ENV PG_CONFIG_FILE ${PG_CONFIG_DIR}/postgresql.conf
ENV PG_BINDIR /usr/lib/postgresql/${PG_VERSION}/bin

RUN apt-get update && apt-get upgrade -y \
      && apt-get install -y --no-install-recommends \
           locales \
      && locale-gen $LANG && update-locale LANG=$LANG \
      && apt-get install -y --no-install-recommends \
           postgresql-$PG_VERSION \
           postgresql-client-$PG_VERSION \
           postgresql-contrib-$PG_VERSION \
           postgresql-doc-$PG_VERSION \
           postgresql-$PG_VERSION-plv8 \
           postgresql-plpython-$PG_VERSION \
           python \
           python3 \
           pwgen \
      && apt-get clean \
      && rm -rf /var/lib/apt/lists/* \
      && rm -rf /tmp/*


RUN rm -rf "$PG_BASE" && mkdir -p "$PG_BASE" && chown -R postgres:postgres "$PG_BASE" \
      && mkdir -p /var/run/postgresql/$PG_VERSION-main.pg_stat_tmp \
      && chown -R postgres:postgres /var/run/postgresql && chmod g+s /var/run/postgresql \
      && chmod +x /usr/local/bin/docker-entrypoint.sh


USER postgres
ENV LANG de_DE.UTF-8

VOLUME ["${PG_BASE}"]

COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN service postgresql start

COPY . /app
WORKDIR /app

ENTRYPOINT bash
