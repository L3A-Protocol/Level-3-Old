# GDA fund project

## Prerequisites for building on Ubuntu 20.04

Clone the repo
```
git clone https://github.com/ggrig/gda-fund-project.git
git submodule update --init --recursive
```

Install build tools
```
sudo apt  install cmake
sudo apt-get install build-essential
sudo apt-get install libssl-dev
```

Build & install libwebsockets
```
cd libwebsockets/
cmake .
make && sudo make install
```

