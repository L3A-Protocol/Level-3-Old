FROM    gdafund/ubuntu-python

RUN mkdir /app
RUN pip3 install opensearch-py

COPY lws-coinbase /app
COPY coinbase-policy.json /app
COPY *.py ./

#CMD "/bin/bash"
CMD python3 -u s3writer.py
