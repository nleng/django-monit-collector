#!/bin/bash
orgdir=${PWD##*/}
dir=${orgdir//[-]/}
service=monitcollector
name=${dir}_${service}_1

docker-compose up -d
sleep 5
echo "Setting up ${name}"
docker exec ${name} python manage.py makemigrations
docker exec ${name} python manage.py migrate
docker-compose restart ${service}
docker exec -it ${name} python manage.py createsuperuser --username "admin" --email "admin@example.com"
