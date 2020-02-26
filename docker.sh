#!/bin/bash

### It dockerizes automatically ###
cd /home/activity
git stash
git pull origin master

docker-compose build 
docker-compose up

