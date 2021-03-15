#!/bin/bash

set -ex

#@--- Function to authenticate to docker hub ---@#
docker_hub_auth() {
    if [[ $TRAVIS_BRANCH == "develop" ]] || \
        [[ $GITHUB_REF == "refs/heads/develop" ]] || \
        [[ $TRAVIS_BRANCH == "staging" ]] || \
        [[ $GITHUB_REF == "refs/heads/staging" ]] || \
        [[ $GITHUB_EVENT_NAME == "release" ]] || \
        [[ $GITHUB_REF == "refs/pull/731/merge" ]] || \
        [[ ! -z $TRAVIS_TAG ]]; then

        docker login -p=$DOCKER_HUB_PASSWD -u=$DOCKER_HUB_USERNM
    fi

}

#@--- Function to export env variables ---@#
export_variables() {
    touch .env.deploy
    echo export SECRET_KEY=${SECRET_KEY} >> .env.deploy
    echo export DEBUG=${DEBUG} >> .env.deploy
    echo export DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS} >> .env.deploy
    echo export DB_ENGINE=${DB_ENGINE} >> .env.deploy
    echo export EMAIL_PORT=${EMAIL_PORT} >> .env.deploy
    echo export EMAIL_HOST_USER=${EMAIL_HOST_USER} >> .env.deploy
    echo export EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD} >> .env.deploy
    echo export EMAIL_HOST=${EMAIL_HOST} >> .env.deploy
    echo export GOOGLE_MAP_API_KEY=${GOOGLE_MAP_API_KEY} >> .env.deploy
}

#@--- Build docker image  and push---@#
build_and_push_image() {

    #@--- Build image for deployment ---@#
    echo "++++++++ Start building image +++++++++"
    if [[ $TRAVIS_BRANCH == "develop" ]] || [[ $GITHUB_REF == "refs/heads/develop" ]] || [[ $GITHUB_REF == "refs/pull/731/merge" ]]
    then
        #@--- Run export function ---@#
        export_variables

        echo export ACTIVITY_CE_DB_NAME=${ACTIVITY_CE_DB_NAME_DEV} >> .env.deploy
        echo export ACTIVITY_CE_DB_USER=${ACTIVITY_CE_DB_USER_DEV} >> .env.deploy
        echo export ACTIVITY_CE_DB_PASSWORD=${ACTIVITY_CE_DB_PASSWORD_DEV} >> .env.deploy
        echo export ACTIVITY_CE_DB_HOST=${ACTIVITY_CE_DB_HOST_DEV} >> .env.deploy
        echo export ACTIVITY_CE_DB_PORT=${ACTIVITY_CE_DB_PORT_DEV} >> .env.deploy

        export APPLICATION_ENV="dev"
        export APPLICATION_NAME="activity"
        docker build -t $REGISTRY_OWNER/activity:$APPLICATION_NAME-$APPLICATION_ENV-$TRAVIS_COMMIT -f docker-deploy/Dockerfile .
        echo "-------- Building Image Done! ----------"

        echo "++++++++++++ Push Image built -------"
        docker push $REGISTRY_OWNER/activity:$APPLICATION_NAME-$APPLICATION_ENV-$TRAVIS_COMMIT

    fi

    #@--- Build staging image ---@#

    if [[ $TRAVIS_BRANCH == "staging" ]] || \
        [[ $GITHUB_REF == "refs/heads/staging" ]]; then
        echo "++++++ Build Staging Image +++++++++++"
        old_line="source .env.deploy"
        new_line='source /vault/secrets/config'
        sed -i "s%$old_line%$new_line%g" docker-deploy/start_app.sh

        docker build -t $REGISTRY_OWNER/activity:$APPLICATION_NAME_STAGING-$TRAVIS_COMMIT -f docker-deploy/Dockerfile .
        echo "-------- Building Image Done! ----------"

        echo "++++++++++++ Push Image built -------"
        docker push $REGISTRY_OWNER/activity:$APPLICATION_NAME_STAGING-$TRAVIS_COMMIT

    fi

    #@--- Build production image ---@#

    if [[ $GITHUB_EVENT_NAME == "release" ]] || [[ ! -z $TRAVIS_TAG ]]; then

        # Create prod settings file and modify dockerfile for production image
        old_line='mv /app/activity/settings/local-sample.py /app/activity/settings/local.py'
        new_line='echo yes | python manage.py collectstatic'
        sed -i "s%$old_line%$new_line%g" docker-deploy/Dockerfile
        sed -i "s/DEBUG = True/DEBUG = False/" activity/settings/local-sample.py
        cp activity/settings/local-sample.py activity/settings/local.py
        cp activity/settings/local-sample.py activity/settings/production.py
        old_email_config="EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'"
        new_email_config="EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'"
        sed -i "s%$old_email_config%$new_email_config%g" activity/settings/local.py
        sed -i "s%$old_email_config%$new_email_config%g" activity/settings/production.py

        echo "+++++++++++ Build Production Image +++++++++++++"

        #@--- Run export function ---@#
        export_variables

        echo export ACTIVITY_CE_DB_NAME=${ACTIVITY_CE_DB_NAME_PROD} >> .env.deploy
        echo export ACTIVITY_CE_DB_USER=${ACTIVITY_CE_DB_USER_PROD} >> .env.deploy
        echo export ACTIVITY_CE_DB_PASSWORD=${ACTIVITY_CE_DB_PASSWORD_PROD} >> .env.deploy
        echo export ACTIVITY_CE_DB_HOST=${ACTIVITY_CE_DB_HOST_PROD} >> .env.deploy
        echo export ACTIVITY_CE_DB_PORT=${ACTIVITY_CE_DB_PORT_PROD} >> .env.deploy
        export APPLICATION_ENV=${APPLICATION_ENV_PROD}

        docker build -t $REGISTRY_OWNER/activity:$APPLICATION_NAME-$APPLICATION_ENV-$TRAVIS_COMMIT -f docker-deploy/Dockerfile .
        echo "-------- Building Image Done! ----------"

        echo "++++++++++++ Push Image built -------"
        docker push $REGISTRY_OWNER/activity:$APPLICATION_NAME-$APPLICATION_ENV-$TRAVIS_COMMIT

    fi

    #@--- Logout from docker ---@#
    echo "--------- Logout dockerhub --------"
    docker logout
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
