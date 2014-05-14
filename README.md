ForumMiner
==========

HOW TO INSTALL
--------------

Install the follwoing if you haven't installed them:

1. Prerequisites:
+ python:	https://www.python.org/download/

To test, type 'python' in a command line. If the interactive python interface is entered, it is installed. Otherwise, install from the above url.

+ gcc:		http://gcc.gnu.org/install/

To test, type 'gcc' in a command line. If the program asks for input file, it is installed. Otherwise, install from the above url.

2. Python setup tool
+ Linux <code>wget https://bootstrap.pypa.io/ez\_setup.py -O - | sudo python</code>
+ Windows

3. Python-dev
+ Linux <code>sudo apt-get python-dev</code>
+ Windows

4. Run the following:

<code>sudo python setup.py install</code>

5. Install the NLTK data (this will take a while):

<code>sudo python -m nltk.downloader all</code>

6. Install the Numpy:

<code>sudo python easy\_install numpy</code>

HOW TO TEST INSTALLATION
------------------------

<code>sudo python setup.py test</code>

If see 'OK' in the last row of output, the installation is complete. Else, see the error message and try to install whatever is missing.

HOW TO RUN CODE
---------------

Note: For detailed instruction of running a .py file (such as WLZW.py), do 

<code>python WLZW.py -h</code>

Two ways to use code:

+ Use as library, see html/index.html for interface reference
+ Use as command line programs, the following gives example

####WLZW - Extract frequent patterns from a corpus

<code>python WLZW.py -i corpus -np 4 -o patterns</code>

From a file named 'corpus', where each line is a document, extract frequent patterns (ngram) using 4 processes. Output is written to a file named 'patterns' where each line is a pattern (ngram). 

For more details, see
<code>python WLZW.py -h</code>

####FreqEst - Count the frequency of patterns and compute statistics
<code> python FreqEst.py -i corpus -l patterns -o entries</code>

Use the same 'corpus' and 'patterns' file from previous step as input, output the frequency of each pattern and the importance statistics (TFIDF, MI, RIDF). Write the output into a file named 'entries'.

For more details, see
<code> python FreqEst.py -h</code>

####SQLiteWrapper - Insert or query data into or from SQLite database

<code>python SQLiteWrapper.py -i entries</code>

Use the file 'entries' from previous step to insert the ngram entries into the SQLite database. You may select some of the records from the database to verify the correctness or for future use.

Select all entries, write into a file named 'selected':

<code>python SQLiteWrapper.py -o selected</code>

If only the patterns or ngrams themselves are needed, rather than all other statistics:

<code>python SQLiteWrapper.py -o selected -ngram\_only</code>

It is also possible to select ngrams or ngram entries using criteria. E.g. Only select ngrams between certain lower bound and upper bound of mutual information (MI).

<code>python SQLiteWrapper.py -o selected -mi\_lower 0.0 -mi\_upper 1.0</code>

Or even specify more restrictions:

<code>python SQLiteWrapper.py -o selected -mi\_lower 0.0 -mi\_upper 1.0 -tf\_lower 1 -tf\_upper 10 -max\_num 1000 -pos NN</code>

The above command select ngrams that has a MI between 0.0 and 1.0, a term frequency between 1 and 10, and a part-of-speech tag of NN. Max number of returned result is 1000 and the output is written to a file named 'selected'. 

For more detail and a whole list of criteria, see

<code>python SQLiteWrapper.py -h</code>

####POS - Part-of-Speech tagger

<code>python POS.py -i corpus -l tag\_list -s ' ' -o tagged\_list -u -m</code>

'corpus' is the file used to populate the DB (from which the ngrams are extracted). 'tag\_list' is a file of ngrams to be tagged (if any ngram is not in the corpus and thus not in the DB, they'll be ignored). The tagged result will be written to a file named 'tagged\_list'. -u tells the program to update the DB with the POS tags. -m tells the program to output and thus update only the matched results (there is a matcher that matches useful POS patterns). The separator between document id and document content is specified by -s (space ' ' in this case, default to '$').

The -l option can be changed into -a so that no list of words to tag is needed. The program will tag all ngrams in the DB. See the following example:

<code>python POS.py -i corpus -a -s ' ' -o tagged\_list -u -m</code>

For complete detail, see:

<code>python POS.py -h</code>

####ClassTagger - Give tags to patterns and tag the patterns in corpus

<code>python ClassTagger.py -i tagged\_ngram</code>

Insert tags for ngrams into the DB using an input file 'tagged\_ngram'. The file uses a format of 'ngram tag' in each line. Other separators can be specified between ngram and tag. E.g. using $$$$$ as the separator, use:

<code>python ClassTagger.py -i tagged\_ngram -s '$$$$$'</code>

Another functionality is to use tagged ngrams in the DB to tag new documents:

<code>python ClassTagger.py -t file\_to\_tag -to file\_tagged</code>

It uses tagged ngrams in the DB to tag the file named 'file\_to\_tag' and write the output to a file named 'file\_tagged'. The input file could be the corpus.

For more details, see:

<code>python ClassTagger.py -h</code>


FILES
-----
List of files in the directory

+ .py: 		python modules
+ html:		code documentation
+ report:	previous reports
+ config:	config file for doxygen (to generate code documentation)
