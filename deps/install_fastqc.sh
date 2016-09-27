#!/bin/bash
mkdir -p bin
mkdir -p temp

########### FastQC #############
echo "Downloading fastqc..."
cd ./temp
curl -o fastqc.zip 'http://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.5_source.zip'
unzip fastqc.zip
cd FastQC
ant

#retrieve missing jar
curl -o bin/commons-math.zip http://mirror.cc.columbia.edu/pub/software/apache/commons/math/binaries/commons-math3-3.6.1-bin.zip
unzip -j bin/commons-math.zip commons-math3-3.6.1/commons-math3-3.6.1.jar -d ./bin/

#move required files
mv bin/Configuration ../../bin/
mv bin/Templates ../../bin/

#move included jars
mv bin/*.jar ../../bin/
mv bin/uk ../../bin/
mv bin/net ../../bin/

#move and fix fastqc to include missing jar
chmod u+x bin/fastqc
mv bin/fastqc ../../bin/fastqc.pl
echo '#!/bin/bash' > ../../bin/fastqc
echo 'script_dir="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"' >> ../../bin/fastqc
echo 'export CLASSPATH=${script_dir}/commons-math3-3.6.1.jar' >> ../../bin/fastqc
echo '${script_dir}/fastqc.pl "$@"' >> ../../bin/fastqc
chmod u+x ../../bin/fastqc

#retrieve test file
curl -o ../../bin/test.fastq.gz http://bioseed.mcs.anl.gov/~seaver/Files/Sample_Reads/WT1_S1_L001_R2_001.fastq.gz

cd ../../
#rm -rf temp
