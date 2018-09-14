#!/usr/bin/env bash

echo "stopping tester server"
sudo systemctl stop tester-server

echo "updating repo"
cd ~/batterytester
git pull
cd ~
echo "updating batterytester"
sudo pip3 install batterytester/ --upgrade
echo "starting tester-server"
sudo systemctl start tester-server
echo "ready"