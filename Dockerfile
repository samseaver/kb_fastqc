FROM kbase/kbase:sdkbase.latest
MAINTAINER KBase Developer
# -----------------------------------------

# Insert apt-get instructions here to install
# any required dependencies for your module.

RUN apt-get update && apt-get install -y ant
RUN mkdir -p /kb/deps
COPY ./deps/install_fastqc.sh /kb/deps/
WORKDIR /kb/deps
RUN pwd
RUN ls
RUN ./install_fastqc.sh

# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work

WORKDIR /kb/module
RUN mkdir -p ./bin
RUN cp -r /kb/deps/bin/* ./bin/
RUN make

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
