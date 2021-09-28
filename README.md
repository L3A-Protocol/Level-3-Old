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
```
Build the library
```
cmake .
make && sudo make install
```

