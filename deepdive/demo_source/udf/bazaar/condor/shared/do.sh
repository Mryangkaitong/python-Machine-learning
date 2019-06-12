#!/bin/sh

####
# We always log which machine does this job run first
####
uname -a

tar xf jre-8u31-linux-x64.gz

for l in `ls *.nxml`
do
  sed -i 's/title>/p>/g' $l
  python html2text.py $l > $l.txt
  
  time ./jre1.8.0_31/bin/java -Xmx4g -XX:CICompilerCount=1 -XX:ConcGCThreads=1 -XX:ParallelGCThreads=1 -jar nlp_2015_2.jar $l.txt 
  if [ -f $l.txt.nlp ]
  then
     echo "SUCCEED!" > SUCCEED.txt
  fi
done

rm nlp_2015_2.jar


