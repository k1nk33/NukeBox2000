#!/bin/bash

# 14.04

sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

sudo apt-get -y install git python-pip python-dev vlc mercurial libffi-dev libssl-dev libpython2.7-dev

# # Install Pygame using pip
# sudo apt-get -y build-dep python-pygame
# sudo apt-get -y install libfreetype6-dev
# sudo pip install hg+http://bitbucket.org/pygame/pygame

sudo pip install setuptools --upgrade
sudo pip install Cython
sudo pip install requests==2.10.0

# sudo pip install -U -r requirements.txt

# cd nukebox2000
sudo python setup.py install
# cd ..

sudo chmod o+r -R /usr/local/lib/python2.7/dist-packages/*
