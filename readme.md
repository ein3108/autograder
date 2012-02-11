% Autograder Script
%
%

## Synopsis

`autograder.py [options] file1 [file2 [file3...]]`

## Overview

This short script is designed to help automate grading of programming
assignments.

## Details

~~~~~~~~~~~~~~~~~~~~~~~~~~ {.latex}
usage: ag.py [-h] [-d MAINDIR] [-t TOOLONG] [-l LOGFILE] [-m MAKESTR]
             [-s TESTSCRIPT] [-k DELIMITER] [-o SCORESFILE]
             implfiles [implfiles ...]

positional arguments:
  implfiles             Name of students' implementation file(s), e.g.
                        'hello.cpp'.

optional arguments:
  -h, --help 			show this help message and exit
  -d DIR, --maindir=DIR	The main directory containing student directories.
  						Default: the current directory.
  -t TIMEOUT, --toolong=TIMEOUT
						No. of seconds before program is determined non-
                        responsive.  Default: 5.
  -l LOGFILE, --logfile=LOGFILE
						Temporary file to store compiler output.
  						Default: "clog"
  -m MAKECMD, --makestr=MAKECMD
  						Command to run in order to build students' code.
  						Default: "/usr/bin/make"
  -s TESTSCRIPT, --testscript=TESTSCRIPT
  						Test script to produce delimited output of tests.
						Default: "./test.sh"
  -k DELIM, --delimiter=DELIM
  						Delimiter used to separate tests in the output files.
						Default: "@"
  -o SCORES, --scoresfile=SCORES
  						Filename to store the tab-delimited scores.
						Default: "scores"
~~~~~~~~~~~~~~~~~~~~~~~~~~

## Setup

Make a directory for each student's work, and store all of these directories
under one main directory, which should have nothing else in it to begin with.
If you have more than one class, keep a separate directory for each one.  Here
is an example of the directory structure, assuming that the class was called
"103" and that the source code for the assignment was named `hello.cpp`:

~~~~~~~~~~~~~~~~~~~~~~~~~~
~Grading/
 |~103/
 | |~student1/
 | | `-hello.cpp
 | |~student2/
 | | `-hello.cpp
 | |~student3/
 | | `-hello.cpp
 | |~student4/
 | | `-hello.cpp
~~~~~~~~~~~~~~~~~~~~~~~~~~

Other files can be present in the student directory; only the ones mentioned
by the `implfiles` option will be used.  There can also be other files in the
main directory.

The script will perform the following steps for every student:

1. Move student's work to the main directory (the one containing all of the
   student directories; `Grading/103/`, in the example above).
1. Try to compile the code (if necessary), recording the results for the
   student's reference.
1. Run a test script which interfaces with the student's program (either via a
   language-level interface, or through the shell, etc.) and produces an
   output file, named `output`.
1. Compare the output file with the *s*olution's *output* (named `soutput`)
   and record the results, both in a file to return to the student, and as a
   line in a tab-delimited file which can be copied / pasted into a
   spreadsheet.

Naturally, steps 2 and 3 require some configuration (e.g., providing makefiles
and test scripts).  See below for examples.


## Example Usage

### Standalone C++ Code; Testing with Bash

This was the first assignment of an intro course on programming.  The
assignment was to modify the "hello world" program to receive two input
strings from the user and then format and print a message based on those
strings back to standard output.  To test, we create a script that echoes
random strings into the program, and then searches the output for the random
strings to make sure they were recorded.  (Recall that `grep` will give a
return code of 1 for a failed search, and 0 otherwise.)

~~~~~~~~~~~~~~~~~~~~~~ {.bash}
#!/bin/bash

strings=( 'sasew' 'hehea' '2s9df' 'kk22' '9rIaf2' 'DFDaj' '43adf' '9khieq' )

for ((i=0; i < ${#strings[@]}; i=i+2)); do
	tmpoutput=`echo -e ${strings[$i]}'\n'${strings[$i+1]} | ./hello`
	echo $tmpoutput | grep "${strings[$i]}" > /dev/null
	echo -n $?'@' >> output
	echo $tmpoutput | grep "${strings[$i+1]}" > /dev/null
	echo -n $?'@' >> output
	tmpoutput=""
done
echo "" >> output
~~~~~~~~~~~~~~~~~~~~~~

Note that the different tests are delimited by the `@` symbol.  This can be
modified via the `--delimiter` option.  Anyhow, a correct program will have
output of `0@0@0@0@0@0@0@0@`; thus the solution's output (`soutput`) should
contain exactly this string.

To invoke the autograder in such a situation, we could populate the main
directory with the following:

* a straightforward makefile named `makefile` to build `hello.cpp` into the
  executable file `hello`;
* the above script with the name `test.sh`;
* the solution's output, `soutput` (which just contains the above string of
  `0@0@0@...`).

To reiterate, the directory should look something like the following before
running the autograder:

~~~~~~~~~~~~~~~~~~~~~~~~~~
~Grading/
 |~103/
 | |~student1/
 | | `-hello.cpp
 | |~student2/
 | | `-hello.cpp
 | |~student3/
 | | `-hello.cpp
 | |~student4/
 | | `-hello.cpp
 | |-makefile
 | |-test.sh
 | |-soutput
~~~~~~~~~~~~~~~~~~~~~~~~~~


Since we have used mainly the default values, we can simply invoke the
autograder via:

~~~~~~~~~~~~~~~~~~~~~~~~~ {.bash}
$ autograder.py --maindir "~/Grading/103/" hello.cpp
~~~~~~~~~~~~~~~~~~~~~~~~~

This will produce a file named `hello.cpp_result` in every student's directory
containing:

* a summary
* the compiler output
* detail on any failed tests
* the student's source code

For example:

~~~~~~~~~~~~~~~~~~~~~~~~~ {.latex}
Executive summary: All tests passed.

Compiler output:

make: Warning: File `hello' has modification time 0.3 s in the future
g++ -Wall hello.cpp -o hello
make: warning:  Clock skew detected.  Your build may be incomplete.
Score: 9 out of 9 = 100%

*************Original submission*************

/*
 * CSc103 Project 1: (hello_world++)
 *
 */

#include <iostream>
using std::cin;
using std::cout;
using std::string;
#include <string>
...
~~~~~~~~~~~~~~~~~~~~~~~~~

### Python Code; Python Test Script

For this example, suppose the students submit a python module that exports a
few classes, perhaps for a red-black tree.  We can then import that module
from another python script and write the tests there, producing a delimited
output file.  In this case, there are only a few modifications required to the
default arguments.  We no longer need a makefile, and we can run our python
script as the test program.  Hence, the call to the autograder would look
something like this:

~~~~~~~~~~~~~~~~~~~~~~~~~ {.bash}
$ autograder.py --maindir "~/Grading/103/" --makestr "" \
  --testscript "python -B rbtest.py" rbtree.py
~~~~~~~~~~~~~~~~~~~~~~~~~

The `-B` flag to the python interpreter is necessary to prevent the generation
of byte code, which ensures that every students' work is graded (else, the old
byte code may be used instead of the very recently moved python code).

## Other Notes

### The `--delimiter` option

The script simply uses python's [`split()` function][pysplit] to parse the
output file, using the `--delimiter` option for the `sep` argument.  Hence,
the delimiter does not need to be a single character (see [the
documentation][pysplit]).  *Note:*  if you supply the empty string
(`--delimiter=""`), then python's default split (based on whitespace /
newlines) will be used.

### Makefiles

For compiled code, the use of makefiles is highly recommended.  If your
makefile supports a `clean` target, it will be executed at the start of every
iteration to clean up the build output from the previous student.  If not, you
may want to ensure that there are no other leftover object files, etc. lying
around that might affect the build of the next student's code; only the actual
source files will be removed by the autograder script.  *Note:* the `make`
program might handle this without intervention if you can guarantee that the
newly copied source file has a modification date which is later than the other
files;  however, I find it safer to just erase all the build output
completely.  After all, correctness is paramount.


## Known Limitations

The following items are not currently configurable, mainly due to the author's
lack of time.

* The solutions output must be named `soutput` and the output file from the
  students' answers must be named `output`.
* If any part of a multi-part project fails to build, or if one or more of the
  files are not submitted, the assignment will receive a 0.  In most cases,
  this can be easily be remedied by distributing a project skeleton which
  compiles (but of course fails all of the tests).
* The output (for the student) is constructed from the first implementation
  file's name, concatenated with the string "_result.txt".  This is currently
  not configurable (but not too hard to change via the python source).

## Dependencies / Requirements

* Python 2.7
* A compiler / interpreter for whatever code you are testing
* Some version of `make` will make life easier

## Credits

The `compare()` function was adapted from code by [David Branner][david].

<!--  links  -->

[pysplit]: http://docs.python.org/library/stdtypes.html#str.split
[david]: https://bitbucket.org/dpb/
