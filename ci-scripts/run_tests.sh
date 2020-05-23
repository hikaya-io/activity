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

#@--- Install and activate virtualenv ---@#
install_activate_virtualenv() {
    cp activity/settings/local-sample.py activity/settings/local.py
    pip3 install pipenv
    pipenv install
    source $(python3 -m pipenv --venv)/bin/activate
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
