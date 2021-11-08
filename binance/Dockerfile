FROM    gdafund/ubuntu-python

RUN mkdir /app

COPY lws-binance /app
COPY binance-policy.json /app
COPY *.py ./

#CMD "/bin/bash"
CMD python3 -u s3writer.py
