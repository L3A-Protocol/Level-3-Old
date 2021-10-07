FROM    gdafund/ubuntu-python

RUN mkdir /app
COPY bybit/lws-bybit /app
COPY bybit/example-policy.json /app/policy.json
COPY s3writer/s3writer.py .
COPY s3writer/s3_storage.py .

# CMD "/bin/bash"
CMD python3 s3writer.py
