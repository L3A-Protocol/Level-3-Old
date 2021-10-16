#!/bin/bash
sudo aws ecr get-login-password --region us-west-1 | sudo docker login --username AWS --password-stdin 381452754685.dkr.ecr.us-west-1.amazonaws.com