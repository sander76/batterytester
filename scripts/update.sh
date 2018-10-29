#!/usr/bin/env bash

echo "updating test frame configs"
cd ~/test_configs/test_frame_configs
git pull

echo "stopping tester server"
sudo systemctl stop tester-server

echo "updating repo"
cd ~/batterytester
git pull
cd ~
echo "updating batterytester"
sudo pip3 install batterytester/ --upgrade

cd ~/test-frame-configs
git pull
cd ~
sudo pip3 install test-frame-configs/ --upgrade

echo "starting tester-server"
sudo systemctl start tester-server
echo "ready"