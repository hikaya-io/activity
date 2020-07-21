#!/bin/bash

set -ex

#@--- install and setup python ---@#
setup_python() {
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt-get update -y
    sudo apt-get install gdal-bin -y
    sudo apt-get install software-properties-common python-software-properties -y
    sudo apt-get install python3.6 -y
    sudo apt-get install python3-pip python3-setuptools -y
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.5 2
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 10
    pip3 install --upgrade pip
}

#@--- Setup postgresdb ---@#
setup_postgresql() {
    #@--- setup postgres db with docker, just for the test ---@#
    docker run -dp 5432:5432 -e POSTGRES_PASSWORD='test_user' -e POSTGRES_USER="postgres" -e POSTGRES_DB='test_db' postgres:11
    sleep 5
    #@--- Check if db is up ---@#
    docker ps
}

#@--- Install and activate virtualenv ---@#
install_activate_virtualenv() {
    cp activity/settings/local-sample.py activity/settings/local.py
    pip3 install pipenv
    pipenv install
    source $(python3 -m pipenv --venv)/bin/activate

    #@ --- export variables for the postgres db ---@#
    export DB_NAME="test_db"
    export DB_USER=postgres
    export DB_HOST=0.0.0.0
    export DB_PORT=5432
    export DB_PASSWORD='test_user'
}

#@--- run linter ---@#
run_linter() {
    flake8 . --statistics
    # exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
    flake8 . --count --exit-zero --max-complexity=10  --statistics
}

#@--- run tests --- @#
run_tests() {
    echo "++++++++++++++++ Run tests ++++++++++++++++"
    coverage run  manage.py test
    coverage report
}

#@--- function to report coverage ---@#
report_coverage() {
    bash <(curl -s https://codecov.io/bash)
}


#@--- Main function ---@#
main() {

    #@--- run Setup finction ---@#
    setup_python

    #@--- start virtualenv ---@#
    install_activate_virtualenv

    #@--- Run linter ---@#
    run_linter

    #@--- Run tests ---@#
    run_tests

    #@--- Report Coverage ---@#
    report_coverage
}

#@--- Run main function ---@#
main
