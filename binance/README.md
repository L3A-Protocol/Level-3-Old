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

## Build and Run the docker image

```
    $ ./build-docker-image.sh -v <version>
```

where <version> usually contains major and minor version nubmers.  
For instance it may be `0.01`. Here major version is `0` and minor is `01`

Make sure all necessay env variables are defined in the `.env` file of the `binance` directory
See `s3writer\.env.sample`
  
Then execute the following:  
```
    sudo docker run --env-file .env gdafund/binance:<version>
```




## Running ECS Fargate task with the container image
  
You basically nee to follow [Deploying a Docker container with ECS and Fargate.](https://towardsdatascience.com/deploying-a-docker-container-with-ecs-and-fargate-7b0cbc9cd608)  
  
The only difference is that you should make change to the ESC task JSON definition to provide the environment variables to the task  

```
...
            "environment": [
                {
                    "name": "C_BINARY_PATH",
                    "value": "/app/lws-binance"
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