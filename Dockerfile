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

# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work

WORKDIR /kb/module
RUN mkdir -p ./bin
RUN cp -r /kb/deps/bin/* ./bin/
ENV PATH=/kb/module/bin:$PATH

#retrieve test file
RUN curl -o test/test_1.fastq.gz http://bioseed.mcs.anl.gov/~seaver/Files/Sample_Reads/WT1_S1_L001_R2_001.fastq.gz

RUN make

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
