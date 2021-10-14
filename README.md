# GDA fund project

## Prerequisites for building on Ubuntu 20.04

Clone the repo
```
git clone https://github.com/ggrig/gda-fund-project.git
git submodule update --init --recursive
```

Install build tools
```
sudo apt-get update
sudo apt  install cmake
sudo apt-get install build-essential
sudo apt-get install libssl-dev
sudo apt install zlib1g-dev
```

Build & install libwebsockets

```
cd libwebsockets/
```
Fix a confuguration bug in the librarary source

Open `libwebsockets/CMakeLists.txt` and change
```
...
option(LWS_WITH_SECURE_STREAMS "Secure Streams protocol-agnostic API" OM)
...
```
to
```
...
option(LWS_WITH_SECURE_STREAMS "Secure Streams protocol-agnostic API" ON)
...

To make the sample at `libwebsockets/minimal-examples/client/binance$` work enable Extensions
```
option(LWS_WITHOUT_EXTENSIONS "Don't compile with extensions" OFF)
```

```
Build the library
```
cmake .
make && sudo make install
```
## Install Docker
```
    ./install-docker.sh
```
Verify docker has been installed
```
    docker -v
    Docker version 20.10.8, build 3967b7d
```
## Build the base docker image with Ubuntu and Python  
Build the docker image from the `docker-ubuntu` directory  
See the directory README for instructions  

## References

[Deploying a Docker container with ECS and Fargate](https://towardsdatascience.com/deploying-a-docker-container-with-ecs-and-fargate-7b0cbc9cd608)  
[Monitoring your container instances](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_cloudwatch_logs.html)


