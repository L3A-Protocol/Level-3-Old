FROM    gdafund/ubuntu-python

RUN mkdir /app

COPY lws-binance /app
COPY binance-policy.json /app
COPY s3writer/s3writer.py .

#CMD "/bin/bash"
CMD python3 s3writer.py
