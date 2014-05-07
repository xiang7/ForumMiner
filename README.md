ForumMiner
==========


Current task:
=============

test setup script on windows and linux

write command line support on py files (now written: WLZW.py, FreqEst.py, SQLiteWrapper, POS)

WLZW - FreqEst - SQLiteWrapper - POS - ClassTagger


Future task:
=============

Frequency and Importance estimation (for now, let us implement three metrics: TF-IDF, MI, RIDF)
    Input: Unstructured data + List of n-grams
    Output: File whose structure is as follows: Term Frequency | Document Frequency | Importance | N-gram | Positional information
        Term Frequency: The number of times this n-gram has appeared in all documents in total
        Document Frequency: The number of documents this n-gram has appeared in. 
        Importance: This should be JSON style as follows: {"TF-IDF": value, "MI": value, "RIDF": value} so that it is extensible in the future
        N-gram: The n-gram whose statistics are being estimated
        Positional information: The positions at which the n-gram has appeared in each document in the following format: {doc_id: [begin position, end position], doc_id: [begin position, end position], ...}

Implement a sqlite wrapper in Python to query the data
Implement distributed + shared computing. For instance, the user will be able to provide an option -distributed in which case, the code should look for a list of servers in a configuration file. If the user provides -shared, the code should just run in parallel on the current machine. Both LZW and RIDF/MI should be allowed to run in parallel. Running LZW in parallel will result in loss of accuracy but should be fine as long as we warn the user.
Write code documentation (compatible with Doxygen) + add as many comments as you can (e.g., before each function, inside functions and at the beginning of each module)
Add a make file and test it by building on Linux + Windows
Run the algorithms on large datasets and get some statistics on system scalability. I've attached a dataset to get you started. This dataset contains knowledge base articles from Microsoft. The format is as follows: KB Identifier $ Title $ Systems that this article applies to $ Description. But it is enough if you treat documents as follows: Document ID $ Any other stuff here.


Questions:
=========

may need to add update to SQLite wrapper later

References:
==========
Tag list of doxygen

@author
@brief
@bug
@code and @endcode
@date
@file
@package
@param
@return
@see
@todo
@version
@warning
