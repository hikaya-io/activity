#!/bin/bash

set +ex

#@--- Function to authenticate to docker hub ---@#
docker_hub_auth() {

    docker login -p=$DOCKER_HUB_PASSWD -u=$DOCKER_HUB_USERNM

}

#@--- Build docker image  and push---@#
build_and_push_image() {

    #@--- Build image for deployment ---@#
    echo "++++++++ Start building image +++++++++"
    if [[ $TRAVIS_BRANCH == "dev" ]] || [[ $GITHUB_REF == "refs/heads/dev" ]]; then
        #@--- Set all the required variables ---@#
        touch .env.deploy

        echo export ACTIVITY_CE_DB_NAME=${ACTIVITY_CE_DB_NAME_DEV} >> .env.deploy
        echo export ACTIVITY_CE_DB_USER=${ACTIVITY_CE_DB_USER_DEV} >> .env.deploy
        echo export ACTIVITY_CE_DB_PASSWORD=${ACTIVITY_CE_DB_PASSWORD_DEV} >> .env.deploy
        echo export ACTIVITY_CE_DB_HOST=${ACTIVITY_CE_DB_HOST_DEV} >> .env.deploy
        echo export SECRET_KEY=${SECRET_KEY_DEV_ENV} >> .env.deploy
        echo export DEBUG=${DEBUG} >> .env.deploy
        echo export DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS} >> .env.deploy
        echo export DB_ENGINE=${DB_ENGINE} >> .env.deploy
        echo export ACTIVITY_CE_DB_PORT=${ACTIVITY_CE_DB_PORT_DEV} >> .env.deploy
        echo export EMAIL_PORT=${EMAIL_PORT} >> .env.deploy
        echo export EMAIL_HOST_USER=${EMAIL_HOST_USER_DEV} >> .env.deploy
        echo export EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD_DEV} >> .env.deploy
        echo export EMAIL_HOST=${EMAIL_HOST} >> .env.deploy
        echo export GOOGLE_MAP_API_KEY=${GOOGLE_MAP_API_KEY_DEV} >> .env.deploy

        docker build -t $REGISTRY_OWNER/activity:$APPLICATION_NAME-$APPLICATION_ENV-$TRAVIS_COMMIT -f docker-deploy/Dockerfile .  
        echo "-------- Building Image Done! ----------"

        echo "++++++++++++ Push Image built -------"
        docker push $REGISTRY_OWNER/activity:$APPLICATION_NAME-$APPLICATION_ENV-$TRAVIS_COMMIT

    fi

    #@--- Logout from docker ---@#
    echo "--------- Logout dockerhub --------"
    docker logout                                                                                                                                          ─╯
}


#@--- main function ---@#
main() {
    if [[ $TRAVIS_EVENT_TYPE != "pull_request" ]]; then
        #@--- Run the auth fucntion ---@#
        docker_hub_auth

        #@--- Run the build function ---@#
        build_and_push_image
    fi
}

#@--- Run the main function ---@#
main
