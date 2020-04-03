FROM python:3

RUN mkdir /pwd
WORKDIR /pwd
COPY ./ /pwd
RUN pip3 install .
WORKDIR /root
RUN rm -rf /pwd

ENTRYPOINT ["tinytinypy"]
