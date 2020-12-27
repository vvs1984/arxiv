FROM python:3.7
RUN mkdir /brat
COPY /brat_v /brat
RUN chmod 777 /brat
WORKDIR /brat
EXPOSE 8080
ENTRYPOINT ["python", "/brat/standalone.py", "8080"]
