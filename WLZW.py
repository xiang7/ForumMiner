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
		self._dict_size = 0 #256
		self._dictionary = dict()# dict((chr(i), chr(i)) for i in xrange(dict_size))
		# in Python 3: dictionary = {chr(i): chr(i) for i in range(dict_size)}

	def compress_sent(self,uncompressed):
		"""construct the dictionary using the sentence. dictionary is shared on same object accross multiple calls. this assumes single sentence to be passed"""

		s=uncompressed.split() #using simple white space split for now
		 
		w = ""
		#result = []
		for c in s:
			#add all the unigrams into the dictionary
			if c not in self._dictionary:
				self._dictionary[c]=self._dict_size
				self._dict_size += 1
			wc = w + " " + c
			if wc.strip() in self._dictionary:
				w = wc
			else:
				#result.append(dictionary[w])
				# Add wc to the dictionary.
				self._dictionary[wc.strip()] = self._dict_size
				self._dict_size += 1
				w = c
		 
		# Output the code for w.
		#if w:
		#	result.append(dictionary[w])
		#return result
	
	
	def compress(self,uncompressed):
		"""construct the dictionary for a chunk of text"""
		#sentence tokenizer
		tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
		s=tokenizer.tokenize(uncompressed)

		for c in s:
			self.compress_sent(c)
	
	#corpus: file name
	#p: number of processes
	def compress_file(self,corpus, np):
		"""construct WLZW pattern out of a corpus, parallelism is an option"""
		p=Pool(processes=np)
		l=[]
		for i in range(0,np):
			l.append((corpus,i,np))
#		curr=time.time()
		result=[]
		result=p.imap_unordered(_compress_file,l,1)
#		print "compress time ", time.time()-curr
#		curr=time.time()
		if np==1:
			return result.next()
		else:
#			final_set=_union(result)
			l=[]
			for i in range(0,np):
				l.append(set(result.next()))
			final_set=_union_binary_tree(l,np)
#			unit=4
#			new_result=[]
#			i=0
#			while i<np:
#				temp=[]
#				for j in range(0,unit):
#					temp.append(result.next())
#				i+=unit
#				print "temp ",len(temp)
#				new_result.append(temp)
#			print "new_result",len(new_result)
#			r=p.imap_unordered(_union,new_result,1)
#			final_set=_union(r)
		#final_set=set(final)
#		print "union time ",time.time()-curr
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
	print 'np: ',np
	while len(curr)>1:
		new=[]
		for i in range(0,len(curr),2):
			new.append(curr[i:i+2])
		print len(new)
		ct=time.time()
		with concurrent.futures.ThreadPoolExecutor(max_workers=np) as executor:
			result=executor.map(_union_two,new)
			print "map: ", time.time()-ct
			ct=time.time()
			curr=[]
			for re in result:
				curr.append(re)
			print "append: ",time.time()-ct
	return curr[0]

def _union_two(l):
	curr=time.time()
	re=l[0] | l[1]
	print time.time()-curr
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

def _compress_file(tup):
#	curr=time.time()
	filename=tup[0]
	rank=tup[1]
	p=tup[2]
	f=open(filename,'r')
	s=os.path.getsize(filename)
	wlzw=WLZWCompressor()
	tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
	if rank!=0:
		f.seek(s/p*rank)
		f.readline()
	for line in f:
		sents=tokenizer.tokenize(line)
		for sent in sents:
			wlzw.compress_sent(sent)
		if f.tell()>=s/p*(rank+1):
			break
	result=wlzw.get_pattern()
#	print "in compress file: ",time.time()-curr
	return result
