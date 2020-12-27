#!/bin/bash

 
psql -d imdb -U docker -f /imdb/imdb_init.sql
psql -d imdb -U postgres -f /imdb/imdb_fill.sql

rm -dr /imdb
