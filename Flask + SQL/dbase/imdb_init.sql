
CREATE SCHEMA imdb

CREATE TABLE imdb.basics(
tconst varchar(20) primary key,
titleType varchar(15),
primaryTitle varchar(500),
originalTitle varchar(500),
isAdult boolean,
startYear int,
endYear int,
runtimeMinutes int,
genres varchar(50)
)


CREATE TABLE imdb.ratings(
tconst varchar(20) primary key,
averageRating real, 
numVotes int
);



