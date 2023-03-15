#!/bin/bash
mkdir -p bin
mkdir -p temp

########### FastQC #############
echo "Downloading fastqc..."
cd ./temp
#curl -o fastqc.zip 'http://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.9_source.zip'
#curl -o fastqc.zip 'https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.9.zip'
wget --no-check-certificate 'https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.12.1.zip'
unzip fastqc_v0.12.1.zip
cd FastQC

#ant  # no longer compiling from source

#retrieve missing jar
#curl -o bin/commons-math.zip http://mirror.cc.columbia.edu/pub/software/apache/commons/math/binaries/commons-math3-3.6.1-bin.zip
#unzip -j bin/commons-math.zip commons-math3-3.6.1/commons-math3-3.6.1.jar -d ./bin/

#move required files
mv Configuration ../../bin/
mv Templates ../../bin/

#move included jars
mv *.jar ../../bin/
mv uk ../../bin/
mv net ../../bin/

#move and fix fastqc to include missing jar
chmod u+x fastqc
mv fastqc ../../bin/fastqc.pl
echo '#!/bin/bash' > ../../bin/fastqc
echo 'script_dir="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"' >> ../../bin/fastqc
echo 'export CLASSPATH=${script_dir}/commons-math3-3.6.1.jar' >> ../../bin/fastqc
echo '${script_dir}/fastqc.pl "$@"' >> ../../bin/fastqc
chmod u+x ../../bin/fastqc

#retrieve test files
cd ../../
rm -rf temp
