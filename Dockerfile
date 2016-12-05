FROM kbase/kbase:sdkbase.latest
MAINTAINER KBase Developer
# -----------------------------------------

# Insert apt-get instructions here to install
# any required dependencies for your module.

RUN apt-get update && apt-get install -y ant
RUN mkdir -p /kb/deps
COPY ./deps/install_fastqc.sh /kb/deps/
WORKDIR /kb/deps
RUN ./install_fastqc.sh

# update installed WS client (will now include get_objects2)
RUN mkdir -p /kb/module && \
    cd /kb/module && \
    git clone https://github.com/kbase/workspace_deluxe && \
    cd workspace_deluxe && \
    git checkout 696add5 && \
    rm -rf /kb/deployment/lib/biokbase/workspace && \
    cp -vr lib/biokbase/workspace /kb/deployment/lib/biokbase/workspace && \
    cd /kb/module && \
    rm -rf workspace_deluxe

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
