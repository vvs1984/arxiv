FROM postgres:latest

RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*
RUN mkdir /imdb
RUN chmod 777 /imdb

WORKDIR /imdb
RUN wget – quiet https://datasets.imdbws.com/title.basics.tsv.gz 2>err.log || cat err.log; rm err.log
RUN gunzip title.basics.tsv.gz
RUN wget – quiet https://datasets.imdbws.com/title.ratings.tsv.gz 2>err.log || cat err.log; rm err.log
RUN gunzip title.ratings.tsv.gz
RUN ls -a
RUN tr '"' ' ' < title.basics.tsv > title.basics2.tsv

WORKDIR ~/
COPY ./init-user-db2.sh /docker-entrypoint-initdb.d/init-user-db.sh
COPY ./imdb_init.sql /imdb/imdb_init.sql
COPY ./imdb_fill.sql /imdb/imdb_fill.sql
COPY ./fill_table.sh /imdb/fill_table.sh
EXPOSE 5432
