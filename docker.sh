#!/bin/bash

### It dockerizes automatically ###
cd /home/Activity-CE
git stash
git pull origin master

docker-compose build 
docker-compose up

