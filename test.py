from WLZW import WLZWCompressor
from WLZW import DistributedWLZW
from WLZW import ParallelWLZW
from FreqEst import FreqEst 
from NgramEntry import NgramEntry
from SQLiteWrapper import SQLiteWrapper
import operator
import time
###############test for WLZW
#s1="This is the test case for analyzing the WLZW. I'm not sure if it comples with the standard. One, if WLZW should contain all the unigrams or the words. Second, if the entire compress can be omitted. Third, we don't even need the decompress module. Fourth, if the algorithm is implemeted correctly. Fifth, if the python syntax now is even correct. Let's test and figure it out. I finally learned how to use the python syntax now haha. I mean the python syntax now seems easy for me. Get on working. Get on working. Get on working."
s="This is a good sentence. This is a very good sentence. This is a bad sentence."

def test_compress():
	compressor=WLZWCompressor()
	compressor.compress(s)
	sorted_x = sorted(compressor.get_dict().iteritems(), key=operator.itemgetter(1))
	print sorted_x

###############test for FreqEst
#s='a b c a b c a b c'
def test_freq(filename,outputfile):
	prev=time.time()
	compressor=WLZWCompressor()
	compressor.compress_file(filename)
	k=compressor.get_pattern()
	print "compress, ",time.time()-prev
	prev=time.time()
	fe=FreqEst(list(k)[1:10000])
	fe.search_file(filename)
	fe.export_to_file(outputfile)
	print 'freq, ',time.time()-prev

def test_freq_file(word_file,text_file):
	word_list=[]
	f=open(word_file,'r')
	for line in f:
		word_list.append(line.trim())
	fe=FreqEst(word_list)
	fe.search_file(text_file)
	sorted_x = sorted(fe.get_freq().iteritems(), key=operator.itemgetter(1))
	for a,b in sorted_x:
		print a,b

def test_parallel(p):
#	curr=time.time()
	compressor=ParallelWLZW()
	result=compressor.compress_file('kb.txt',p)
#	print "compress time in test", time.time()-curr
#	curr=time.time()
	f=open('wlzw_out_shared','w')
	for re in result:
		f.write(re+'\n')
	f.close()
#	print "write time ",time.time()-curr

def test_sql_wraper(filename):
	l=[]
	with open(filename,'r') as f:
		for line in f:
			entry=NgramEntry()
			entry.from_str(line)
			l.append(entry)
	wraper=SQLiteWrapper()
	wraper.insert_many_entry(l)
	entry=wraper.select_ngram('about whether it')
	print entry.to_str()

def test_distributed_wlzw():
	#test:
	curr=time.time()
	dwlzw=DistributedWLZW()
	final=dwlzw.compress_file('kb.txt')
	print len(final)
	print time.time()-curr


test_sql_wraper('result')
#test_freq("kb.txt","result")
#test_distributed_wlzw()
"""
The class for WLZW Compressor. 

This class takes in text as string or file and runs WLZW on it. Upon completion, the dictionary can be obtained.
"""
#start=time.time()
#test_parallel(1)
#print "1: ",time.time()-start
#start=time.time()
#test_parallel(2)
#print "2: ",time.time()-start
#start=time.time()
#test_parallel(4)
#print "4: ",time.time()-start
#start=time.time()
#test_parallel(8)
#print "8: ",time.time()-start
#start=time.time()
#test_parallel(16)
#print "16: ",time.time()-start
#start=time.time()
#test_parallel(32)
#print "32: ",time.time()-start
