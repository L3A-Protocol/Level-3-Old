#!/bin/bash
sudo aws ecr get-login-password --region eu-west-1 | sudo docker login --username AWS --password-stdin 381452754685.dkr.ecr.eu-west-1.amazonaws.com