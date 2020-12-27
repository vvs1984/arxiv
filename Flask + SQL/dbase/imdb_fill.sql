COPY imdb.basics FROM '/imdb/title.basics2.tsv' WITH DELIMITER E'\t' NULL '\N' CSV HEADER;
COPY imdb.ratings FROM '/imdb/title.ratings.tsv' WITH DELIMITER E'\t' NULL '\N' CSV HEADER;
