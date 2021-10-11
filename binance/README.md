# Binance support

## Build C module

Lws must have been built with `LWS_ROLE_WS=1`, `LWS_WITH_SECURE_STREAMS=1`, and
`LWS_WITHOUT_EXTENSIONS=0`

```
 $ cmake . && make
```

## Containerize

```
    sudo docker image build -t gdafund/binance:0.01 .
```

## Run the container

Create .env file  

```
    cp s3writer/.env.sample .env
```
  
Replace the values in `.env` with the correct ones  
  
Run the container  
  
```
    sudo docker run --env-file s3writer/.env gdafund/binance:0.01
```