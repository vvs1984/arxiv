#!/bin/bash
echo "build the docker image"
docker image build -t imdb_app . >> ./output
echo "built docker images and proceeding to delete existing container"
result=$( docker ps -q -f name=imdb_app)
if [[ $? -eq 0 ]]; then
echo "Container exists"
else
echo "No such container"
fi
echo "Deploying the updated container"
sleep 2 
echo "docker run ..."
docker run --name imdb_appv1 -p 5430:5430 -p 5000:5000 -d imdb_app 
sleep 2
echo "Now you can try to connect to app.. ip_or_lacalhost:5000/queve/var"

