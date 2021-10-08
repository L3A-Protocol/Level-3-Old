FROM    gdafund/ubuntu-python

RUN mkdir /app
RUN pip3 install numpy
RUN pip3 install pandas

COPY bybit/lws-bybit /app
COPY bybit/example-policy.json /app/policy.json
COPY s3writer/s3writer.py .
COPY s3writer/s3_storage.py .
COPY s3writer/.env .

#CMD "/bin/bash"
CMD python3 s3writer.py
