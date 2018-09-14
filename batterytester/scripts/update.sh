#!/usr/bin/env bash

sudo systemctl stop tester-server

cd ~/batterytester
git pull
cd ~
sudo pip3 install batterytester/ --upgrade
sudo systemctl start tester-server
