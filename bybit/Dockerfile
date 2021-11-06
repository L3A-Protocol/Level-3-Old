FROM    gdafund/ubuntu-python

RUN mkdir /app
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install opensearch-py

COPY lws-bybit /app
COPY policy.json /app
COPY *.py ./

#CMD "/bin/bash"
CMD python3 -u s3writer.py
