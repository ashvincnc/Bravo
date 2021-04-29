#!/bin/bash


sudo apt-get install python3-pyqt5
pip3 install numpy==1.16.2
pip3 install pyqtgraph==0.11.0
sudo apt-get install libatlas-base-dev
sudo pip3 install adafruit-ads1x15
mkdir /home/pi/.config/autostart
mv ventilator.desktop /home/pi/.config/autostart

reboot


