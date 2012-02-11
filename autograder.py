#!/usr/bin/env python
"""
Autograder.  Compiles and runs student programs, comparing
output with a standard output file.
"""

# use print() instead of plain print
from __future__ import print_function 
import os
import shutil as SH
import subprocess
import threading as TH
import argparse as ap


# Setup the arguments to the script

parser = ap.ArgumentParser(description='Autograder script.')
parser.add_argument('-d','--maindir',dest='maindir', default='./',
        help='The main directory containing student directories.')
parser.add_argument('-t','--toolong',dest='toolong', type=int, default=5,
        help='No. of seconds before program is determined non-responsive.')
parser.add_argument('-l','--logfile',dest='logfile', default='clog',
        help='Temporary file to store compiler output.')
parser.add_argument('-m','--makestr',dest='makestr', default='/usr/bin/make',
        help="Command to run in order to build students' code.")
parser.add_argument('-s','--testscript',dest='testscript', default='./test.sh',
        help='Test script to produce delimited output of tests.')
parser.add_argument('-k','--delimiter',dest='delimiter', default='@',
        help='Delimiter used to separate tests in the output files.')
parser.add_argument('-o','--scoresfile',dest='scoresfile', default='scores',
        help="Filename to store the tab-delimited scores.")
parser.add_argument('implfiles', nargs='+',
        help="Name of students' implementation file, e.g. 'hello.cpp'.")
args = parser.parse_args()

implFiles = args.implfiles
implFile = args.implfiles[0]
mainDir = args.maindir
tooLong = args.toolong
logFile = args.logfile
makestr = args.makestr
testScript = args.testscript
delim = args.delimiter if args.delimiter != "" else None
scoresFile = args.scoresfile

# if a makestring and log file are supplied, redirect output of make command:
if makestr != "" and logFile != "":
    makestr = makestr + " &> " + logFile

tmpProc = None # hack; using a global to pass data around

# TODO: test.


def threadWrap():
    global tmpProc
    tmpProc = subprocess.Popen(testScript)
    tmpProc.communicate()

def main():
    os.chdir(mainDir)
    scores = {} #empty dictionary for scores.
    for root,dirs,files in os.walk("."):
        for d in dirs:
            scores[d] = 0
            resultMsg = ""
            # run tests, and update the grades.
            # move files one by one to the current directory (if they exist)
            # and run the test script on each one.  To prevent the previous
            # student's work from affecting the test, remove the old output
            # and make sure the interpreter does not produce compiled
            # bytecode.
            try:
                # clear the log and the output file:
                f = open(logFile,'w')
                f.close()
                f = open("output",'w')
                f.close()
                # try to run make clean; if it fails, just move on
                if makestr != "":
                    os.spawnl(os.P_WAIT,makestr,"make","clean")
            except:
                pass
            print("Processing " + d)
            try:
                for ifile in implFiles:
                    sfile = os.path.join(d,ifile)
                    if os.path.exists(sfile):
                        SH.copyfile(sfile,ifile)
                    else:
                        print(d + " didn't do their work")
                        resultMsg = "Assignment not turned in."
                        raise UserWarning

                # now, if applicable, try to build the program using the
                # specified make string:
                if makestr != "":
                    retcode = subprocess.call(makestr, shell=True)
                    if retcode:
                        print(d + " failed to build x_x")
                        resultMsg = "Failed to build x_x"
                        raise UserWarning

                # now run the test script and compare output
                # we want something simple, like the following:
                # subprocess.call("python -B " + testScript)
                # resultMsg,nRight,nTotal = compare("")
                # however, this is no good when people's programs break,
                # or run into infinite loops.  So we must monitor the
                # thread in which it runs, and kill it after too much
                # time has passed.

                ranForever = False
                th = TH.Thread(target=threadWrap)
                th.start()
                th.join(tooLong)
                if th.is_alive():
                    print ("infinite loop. killing thread...")
                    tmpProc.terminate()
                    th.join() # wait for thread to terminate
                    ranForever = True
                del th
                if ranForever:
                    resultMsg = "Program ran too long. Infinite loop?\n"
                    raise UserWarning
                else:
                    resultMsg,nRight,nTotal = compare("")
            except UserWarning:
                # something went horribly wrong, so set the score to be 0:
                nRight = 0
                nTotal = 1
                # if needed, we can get some error info here?
                # Note: nothing special about UserWarning; it sounded
                # nice and I needed an exception.  That's all.
            finally:
                # write a report of whatever happened.
                score = int(round((float(nRight)/nTotal)*100))
                scores[d] = score
                with open(os.path.join(d,implFile + "_result.txt"),'w') as f:
                    f.write(resultMsg + "\n\n")
                    f.write("Compiler output:\n\n")
                    with open(logFile,'r') as fs:
                        f.write(fs.read())
                    f.write("Score: " + str(nRight) + " out of " + \
                            str(nTotal) + " = " + str(score) + "%\n\n")
                    f.write("*************Original submission*************\n\n")
                    # there might not be a file here, so just ignore any
                    # errors that are raised.
                    try:
                        for ifile in implFiles:
                            sfile = os.path.join(d,ifile)
                            f.write("\n\n### " + ifile + ":\n\n")
                            with open(sfile,'r') as fs:
                                f.write(fs.read())
                    except:
                        pass
            # return
    with open(scoresFile,'w') as fscores:
        for k in sorted(scores.keys()):
            fscores.write(k + "\t" + str(scores[k]) + "\n")
    print ("Scores written to " + scoresFile)
    return

def declare_path():
    """This function is currently a dummy but can later be used to grade a
    whole set of student work, one directory per student in the same path.
    """
    
    # "the_student" is name of a directory in the path
    the_path = the_student = ''
    return the_path + the_student

def compare(full_path):
    """Evaluate student's output file against authenticated output file
    and report the results.
    """

    solutionOutput = "soutput"
    output = "output"
    # First evaluate tests and store results.
    # "counter" will hold True/False in each index, each representing a test
    counter = [] 
    try:
        # remember, U recognizes all newlines
        with open(full_path + solutionOutput, 'U') as filename: 
            off_content = filename.read().split(delim)
            off_length = len(off_content)
        with open(full_path + output, 'U') as filename:
            stu_content = filename.read().split(delim)
            stu_length = len(stu_content)
    except IOError:
        print('\nIOError reported; exiting. \n\nAre the files "output"'
            'and "soutput" in the right place?\n\nPath was given as',
            full_path)
        return "Program failed to produce output",0,1
    # print('\nDetected', off_length, 'tests in authenticated output file.')
    # pad the student output if necessary
    for i in xrange(off_length - stu_length):
        stu_content.append(delim) # this should never be a right answer.
    counter = [off_content[i] == stu_content[i] for i in xrange(off_length)]
    
    # Now report results.
    resultstr = ""
    if all(counter):
        resultstr = 'Summary: All tests passed.'
    else:
        # must make plural noun agree with counter
        if counter.count(False) == 1:
            failure_spelling = ' failure '
        else:
            failure_spelling = ' failures '
        resultstr = '\nSummary: Student output has ' + \
                str(counter.count(False)) + failure_spelling + \
                'in ' + str(len(counter)) + ' tests.\n\nDetailed report:\n\n'
        for i in xrange(len(counter)):
            if counter[i]==False:
                resultstr += ' Test ' + str(i) + ' failed:\n   Student had:\n\t' + \
                        stu_content[i] + '\n   Should have:\n\t' + off_content[i]
            else:
                resultstr += ' Test ' + str(i) + ' succeeded.'
    return resultstr,counter.count(True),off_length

if __name__ == '__main__':
  main()