FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------

# Insert apt-get instructions here to install
# any required dependencies for your module.

RUN apt-get update && apt-get install -y ant  && apt-get -y install wget

RUN mkdir -p /kb/data
COPY ./data/index_start.txt /kb/data/
COPY ./data/index_end.txt /kb/data/

RUN mkdir -p /kb/deps
COPY ./deps/install_fastqc.sh /kb/deps/
WORKDIR /kb/deps
RUN ./install_fastqc.sh

# WIERD: https://community.jaspersoft.com/questions/1064816/solved-getting-atkswing-errors-running-report
RUN rm -f /usr/lib/jvm/java-8-openjdk-amd64/jre/lib/accessibility.properties && \
    rm -f /etc/java-8-openjdk/accessibility.properties
# -----------------------------------------
COPY ./ /kb/module
RUN mkdir -p /kb/module/work

WORKDIR /kb/module
RUN mkdir -p ./bin
RUN cp -r /kb/deps/bin/* ./bin/
ENV PATH=/kb/module/bin:$PATH

RUN make

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
