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
    $ ./build-docker-image.sh -v <version>
```

where <version> usually contains major and minor version nubmers.  
For instance it may be `0.01`. Here major version is `0` and minor is `01`

Make sure all necessay env variables are defined in the `.env` file.
See `s3writer\.env.sample`
  
Then execute the following:  
```
    sudo docker run --env-file .env gdafund/bybit:<version>
```

