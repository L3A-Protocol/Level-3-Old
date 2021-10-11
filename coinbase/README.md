# lws secure streams coinbase

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

## Containerize

```
    sudo docker image build -t gdafund/coinbase:0.01 .
```

## Run the container

Create .env file  

```
    cp s3writer/.env.sample .env
```
  
Replace the values in `.env` with the correct ones  
  
Run the container  
  
```
    sudo docker run --env-file s3writer/.env gdafund/coinbase:0.01
```

## Running ECS Fargate task with the container image
  
You basically nee to follow [Deploying a Docker container with ECS and Fargate.](https://towardsdatascience.com/deploying-a-docker-container-with-ecs-and-fargate-7b0cbc9cd608)  
  
The only difference is that you should make change to the ESC task JSON definition to provide the environment variables to the task  

```
...
            "environment": [
                {
                    "name": "C_BINARY_PATH",
                    "value": "/app/lws-coinbase"
                },
                {
                    "name": "TOPIC",
                    "value": "BTC-USD"
                },
                {
                    "name": "AWS_ACCESS_KEY_ID",
                    "value": "<your key here>"
                },
                {
                    "name": "AWS_SECRET_ACCESS_KEY",
                    "value": "<your secret key here>"
                },
                {
                    "name": "BUCKET_NAME",
                    "value": "<your bucket name here>"
                }
            ],
...
```
