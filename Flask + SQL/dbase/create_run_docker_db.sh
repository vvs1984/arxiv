#!/bin/bash
echo "build the docker image"
docker image build -t im_db . >> ./output
echo "built docker images and proceeding to delete existing container"
result=$( docker ps -q -f name=im_db)
if [[ $? -eq 0 ]]; then
echo "Container exists"
else
echo "No such container"
fi
echo "Deploying the updated container"
sleep 2 
echo "docker run ..."
docker run --name imdb_postgres -e POSTGRES_PASSWORD=docker -e POSTGRE_USER=docker -p5430:5432 -d im_db 
sleep 2
echo "Docker exec"
docker exec -it imdb_postgres /bin/bash -f /imdb/fill_table.sh
