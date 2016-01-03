#!/bin/bash

tmpoutput=`Rscript test.r`
echo $tmpoutput | grep -q "1 2 3 4 5 6 7 8 9 10" # answer to the question goes here
echo -n $?'@' >> output
tmpoutput=""
tmpoutput=`Rscript test2.r`
echo $tmpoutput | grep -q "10 9 8 7 6 5 4 3 2 1"
echo -n $?'@' >> output
tmpoutput=""
echo "" >> output
