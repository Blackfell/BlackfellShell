#!/bin/sh

python -m pip install -r requirements.txt
echo "install wine now"
echo "download python installer for python 3.8"
wine py -3 -m pip install -r requirements.txt
