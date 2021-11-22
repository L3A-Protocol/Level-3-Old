FROM    gdafund/ubuntu-python

RUN mkdir /app

COPY lws-bytick /app
COPY bytick-policy.json /app
COPY *.py ./

#CMD "/bin/bash"
CMD python3 -u s3writer.py
