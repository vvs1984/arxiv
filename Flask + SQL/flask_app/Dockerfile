FROM python:alpine
WORKDIR /usr/src/app
COPY . .
ADD requirements.txt /
RUN apk update --no-cache \
&& apk add build-base postgresql-dev libpq --no-cache --virtual .build-deps \
&& pip install --no-cache-dir --upgrade pip \
&& pip install --no-cache-dir -r /requirements.txt \
&& apk del .build-deps
RUN apk add postgresql-libs libpq --no-cache
EXPOSE 5000 5432
ENTRYPOINT ["python3", "./imdb.py"]

