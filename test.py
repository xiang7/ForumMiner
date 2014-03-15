from WLZW import WLZWCompressor
from FreqEst import FreqEst 
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
def test_freq():
	compressor=WLZWCompressor()
	compressor.compress(s)
	k=compressor.get_pattern()
	fe=FreqEst(k)
	fe.search(s)
	sorted_x = sorted(fe.get_freq().iteritems(), key=operator.itemgetter(1))
	for a,b in sorted_x:
		print a,b

def test_parallel(p):
	compressor=WLZWCompressor()
	result=compressor.compress_file('test',p)
	f=open('result','w')
	for re in result:
		f.write(re+'\n')
	f.close()

#test_freq()

start=time.time()
test_parallel(1)
print "1: ",time.time()-start
start=time.time()
test_parallel(2)
print "2: ",time.time()-start
test_parallel(4)
print "3: ",time.time()-start