#!/bin/bash

while getopts v: flag
do
    case "${flag}" in
        v) version=${OPTARG};;
    esac
done

cp ../s3writer/*.py .
sudo docker image build -t gdafund/bybit-usdt:$version -f Dockerfile-USDT .
rm *.py
