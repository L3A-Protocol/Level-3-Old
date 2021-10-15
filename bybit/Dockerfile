FROM    gdafund/ubuntu-python

RUN mkdir /app
RUN pip3 install numpy
RUN pip3 install pandas

COPY lws-bybit /app
COPY policy.json /app
COPY s3writer/*.py ./

#CMD "/bin/bash"
CMD python3 -u s3writer.py
