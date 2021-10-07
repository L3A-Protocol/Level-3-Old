FROM    ubuntu:20.04

RUN apt-get update && apt-get install -y software-properties-common && apt-get install -y git
RUN apt-get update && apt-get install -y software-properties-common gcc && \
    add-apt-repository -y ppa:deadsnakes/ppa

RUN apt-get update && apt-get install -y python3.8 python3-distutils python3-pip python3-apt

COPY requirements.txt .

RUN pip3 install -r requirements.txt

