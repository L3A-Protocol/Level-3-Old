#!/bin/bash
cp ../s3writer/*.py .
sudo docker image build -t gdafund/bybit:0.05 .
rm *.py
