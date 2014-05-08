ForumMiner
==========

HOW TO INSTALL
--------------

Prerequisites:
+ python:	https://www.python.org/download/
+ gcc:		http://gcc.gnu.org/install/

python setup.py install 

(to be tested)


HOW TO TEST INSTALLATION
------------------------

python setup.py test 

(to be implemented, provide a small test data set)


HOW TO RUN CODE
---------------

Note: For detailed instruction of running a .py file (such as WLZW.py), do 

<code>python WLZW.py -h</code>

####WLZW - Extract frequent patterns from a corpus

<code>python WLZW.py -i corpus -np 4 -o patterns</code>

From a file named 'corpus', where each line is a document, extract frequent patterns (ngram) using 4 processes. Output is written to a file named 'patterns' where each line is a pattern (ngram). For more details, see

<code>python WLZW.py -h</code>

####FreqEst - Count the frequency of patterns and compute statistics
<code> python FreqEst.py -i corpus -l patterns -o entries</code>

Use the same 'corpus' and 'patterns' file from previous step as input, output the frequency of each pattern and the importance statistics (TFIDF, MI, RIDF). For more details, see

<code> python FreqEst.py</code>

####SQLiteWrapper - Insert or query data into or from SQLite database

####POS - Part-of-Speech tagger

####ClassTagger - Give tags to patterns and tag the patterns in corpus


FILES
-----
List of files in the directory

+ .py: 		python modules
+ html:		code documentation
+ report:	previous reports
+ config:	config file for doxygen (to generate code documentation)
