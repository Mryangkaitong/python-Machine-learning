
## Condor

Put this folder when you use http://chtc.cs.wisc.edu/chtcjobwrapper.shtml

Follow the instruction of http://chtc.cs.wisc.edu/chtcjobwrapper.shtml to start the job

### Notes

It is VERY VERY important to add the line

      -Xmx4g -XX:CICompilerCount=1 -XX:ConcGCThreads=1 -XX:ParallelGCThreads=1 

whenever you start JVM on Condor. Otherwise, Stanford CoreNLP would use more
than 1 core.

In the file URLS, there are two things:
   - jre-8u31-linux-x64.gz: Just pack the Oracle Java's binary into this. When you
   need JVM, start it like ./jre1.8.0_31/bin/java
   - nlp_2015_2.jar: Put your jar here to use it. Make sure it is compiled with JRE-8u31. 