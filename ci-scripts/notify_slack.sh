#!/bin/bash

set -ex
set -o pipefail

#@--- Fuction to replace variables for branch staging ---@#
replace_env_variables() {

    if [[ $GITHUB_EVENT_NAME == "release" ]]; then
        export APPLICATION_ENV=${APPLICATION_ENV_PROD}
    fi
}


#@--- Function to setup the message to be send ---@#
setup_message() {

    if [[ $DEPLOY == "success" ]]; then
        echo "++++++++++++ generate deployment message +++++++++++++"
        COMMIT_URL="https://github.com/hikaya-io/activity/commit/${GITHUB_SHA}"
        DEPLOYMENT_MESSAGE="*Success* :white_check_mark: The following commit was deployed to *_activity ${APPLICATION_ENV}_* by ${EMOJI} \n [Message]: $TRAVIS_COMMIT_MESSAGE \n [Link]: ${COMMIT_URL}"
    else
        COMMIT_URL="https://github.com/hikaya-io/activity/commit/${GITHUB_SHA}"
        DEPLOYMENT_MESSAGE="*Failed* :no_entry: The following commit was unable to deploy to *_activity ${APPLICATION_ENV}_* by ${EMOJI} \n [Message]: $TRAVIS_COMMIT_MESSAGE \n [Link]: ${COMMIT_URL}"
    fi

}

#@--- Function to send slack notification ---@#
send_slack_notification() {

    echo "++++++++++++ sending slack message +++++++++++++"
    echo $DEPLOYMENT_MESSAGE
    curl -X POST --data-urlencode \
    "payload={\"channel\": \"${DEPLOYMENT_CHANNEL}\", \"username\": \"DeployNotification\", \"text\": \"${DEPLOYMENT_MESSAGE}\", \"icon_emoji\": \":rocket:\"}" \
    "${SLACK_CHANNEL_HOOK}"

}

main() {
    if  [[ $GITHUB_REF == "refs/heads/develop" ]] || \
        [[ $GITHUB_EVENT_NAME == "release" ]]; then
        #@--- run the replace function ---@#
        replace_env_varibles

        #@-- Run the message function ---@#
        setup_message

        #@--- Run slack notify function ---@#
        send_slack_notification
    fi
}

main
