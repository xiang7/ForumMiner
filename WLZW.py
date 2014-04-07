import nltk
import os
from multiprocessing import Pool
import copy_reg 
import time
import concurrent.futures
#To construct WLZW
#Dictionary is returned which is the hot pattern
#Dictionary started with empty set
#Index by words for WLZW
#Keep dictionary as class memember since compress is called sentence by sentence
#nltk needed, data in nltk needed as well
class WLZWCompressor:
	
	def __init__(self):
		# Build the dictionary.
		self._dict_size = 0
		self._dictionary = dict()

	def compress_sent(self,uncompressed):
		"""construct the dictionary using the sentence. dictionary is shared on same object accross multiple calls. this assumes single sentence to be passed"""

		s=uncompressed.split() #using simple white space split for now
		 
		w = ""
		for c in s:
			#add all the unigrams into the dictionary
			if c not in self._dictionary:
				self._dictionary[c]=self._dict_size
				self._dict_size += 1
			wc = w + " " + c
			if wc.strip() in self._dictionary:
				w = wc
			else:
				# Add wc to the dictionary.
				self._dictionary[wc.strip()] = self._dict_size
				self._dict_size += 1
				w = c
		 
	
	def compress(self,uncompressed):
		"""construct the dictionary for a chunk of text"""
		#sentence tokenizer
		tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
		s=tokenizer.tokenize(uncompressed)

		for c in s:
			self.compress_sent(c)
	
	#corpus: file name
	#p: number of processes
	def compress_file(self,corpus, np=4,separator=None):
		"""construct WLZW pattern out of a corpus, parallelism is an option"""

		#if only one process, no need for parallelization
		if np==1:
			return set(_compress_file((corpus,0,np,separator)))

		p=Pool(processes=np)
		l=[]
		for i in range(0,np):
			l.append((corpus,i,np,separator))
		result=p.imap_unordered(_compress_file,l,1)

		if np==1:
			final_set=result.next()
		else:
			final_set=_union(result)

		return final_set
			

	def get_dict(self):	
		""""return the class dictionary. should be called after all text is compressed"""
		return self._dictionary
	
	def get_pattern(self):
		return self._dictionary.keys() 
	 

def _union(l):
	result=set()
	for re in l:
		result = result | set(re)
	return result

def _union_recur(l):
	if len(l)==2:
		return l[1] | l[0]
	return _union_recur(l[0:len(l)/2]) | _union_recur(l[len(l)/2:len(l)])

def _union_binary_tree(l,np):
	curr=l
	while len(curr)>1:
		new=[]
		for i in range(0,len(curr),2):
			new.append(curr[i:i+2])
		with concurrent.futures.ThreadPoolExecutor(max_workers=np) as executor:
			result=executor.map(_union_two,new)
			curr=[]
			for re in result:
				curr.append(re)
	return curr[0]

def _union_two(l):
	re=l[0] | l[1]
	return re

def _union_list(l):
	result=[]
	for s in l:
		result.extend(s)
	return set(result)

def _compress_chunk(chunk):
	wlzw=WLZWCompressor()
	f=open(chunk,'r')
	for line in f:
		wlzw.compress(line)
	return set(wlzw.get_pattern())

#compress function used for map (shared memory parallelization). 
def _compress_file(tup):
	filename=tup[0]
	rank=tup[1]
	p=tup[2]
	separator=tup[3]
	f=open(filename,'r')
	s=os.path.getsize(filename)
	wlzw=WLZWCompressor()
	tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
	if rank!=0:
		f.seek(s/p*rank)
		f.readline()
	for line in f:
		if separator!=None:
			s=line.split(separator)
			line=separator.join(s[1:])
		sents=tokenizer.tokenize(line)
		for sent in sents:
			wlzw.compress_sent(sent)
		if f.tell()>=s/p*(rank+1):
			break
	result=wlzw.get_pattern()
	return result
