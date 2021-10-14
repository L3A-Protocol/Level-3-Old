# lws secure streams bybit

## build

Lws must have been built with `LWS_ROLE_WS=1`, `LWS_WITH_SECURE_STREAMS=1`, and
`LWS_WITHOUT_EXTENSIONS=0`

```
 $ cmake . && make
```

Debug configurarion 

```
 $ cmake . -DCMAKE_BUILD_TYPE=DEBUG && make
```
## Commandline Options

Option|Meaning
---|---
-d|Set logging verbosity

## Build and Run the docker image

```
    sudo docker image build -t gdafund/bybit:0.01 .
```

Make sure all necessay env variables are defined in s3writer/.env  
  
Then execute the following:  
```
    sudo docker run --env-file s3writer/.env gdafund/bybit:0.01
```

