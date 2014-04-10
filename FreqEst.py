#estimates frequency of key words given a text, output is a dictionary with <Ngram, NgramEntry>
#assume the raw text format is <DOCID Separator Document>
import esm
from NgramEntry import NgramEntry
import time
import math


class FreqEst:
	"""This is the class to count frequency of patterns from a corpus. 
	It also computes importance metrics, RIDF, TFIDF, MI.
	It operates on one set of patterns. 
	Multiple calls of search functions can be called on different strings/corpus.
	Dictionary persists across these search calls.
	Call export to file or get frequency to retrieve the results"""
	
	def __init__(self,key_list,separator='$'):
		"""Initialize the estimator.
		@param key_list - a list of patterns, the estimator will search on this list of patterns
		@param separator - the separator string that separates doc id and documents"""
		print len(key_list)
		self._key_list=key_list
		prev=time.time()
		self._index = esm.Index()
		for r in self._key_list:
			self._index.enter(r)
		self._index.fix()
		print "build automata: ", time.time()-prev
		self._table = dict()
		self._N=0 #total number of documents
		self._separator=separator

	def _isBlankSpace(self,w):
		if w==' ' or w=='\t' or w=='\n':
			return True

	#search a document
	def search(self, text):
		"""Search a document
		@param text - the string to be searched
		@return None - call get freq or export to file"""
		#increment total number of documents
		self._N+=1

		#peel off the DOCID
		s=text.split(self._separator)
		docid=s[0]
		text=self._separator.join(s[1:])

		#a set to record the ngrams in this document so that no duplicate will be counted into df
		ngrams=set()
		#search the document
		#no need to chop the document into sentence since all ngrams are obtained after document is chopped into sentence. so not possible to match ngram across sentences
		for (f,e),w in self._index.query(text):
			if (f!=0 and (not self._isBlankSpace(text[f-1]))) or (f+len(w)<len(text) and (not self._isBlankSpace(text[f+len(w)]))):
				continue
			if w not in self._table:
				self._table[w]=NgramEntry(w,tf=1,position=[])
			else:
				self._table[w].tf+=1
			if w not in ngrams:
				self._table[w].df+=1
				ngrams.add(w)
			self._table[w].position.append(docid+":"+str(f))

	#search a list
	def search_list(self,text_list):
		"""Search a list of documents
		@param text_list - a list of strings
		@return None - call get freq or export to file"""
		for l in text_list:
			self.search(l)

	#search a file
	def search_file(self,filename):
		"""Search a file
		@param filename - the path to the file
		@return None, call get freq or export to file
		"""
		f=open(filename,'r')
		for line in f:
			self.search(line)

	def get_freq(self):
		"""Get the match results
		@return table, <ngram (string), NgramEntry>, see definition of NgramEntry"""
		return self._table

	#export the resulting dictionary into a file
	def export_to_file(self,filename):
		"""Export the search result to file
		@filename - string, output file path
		@return None
		"""
		keys = self._table.keys()
		with open(filename,'w') as f:
			for k in keys:
				item=self._table[k]
				#compute tf-idf, implemented as TF(t,D)*IDF(t,D), where t is the term and D is the corpus
				tfidf=item.tf*math.log(float(self._N)/float(item.df))
				#compute ridf
				ridf=math.log(float(self._N)/float(item.df))+math.log(1-math.exp(-float(item.tf)/float(self._N)))
				#compute mi TODO
				mi=0.0
				item.importance=[tfidf,mi,ridf]
				f.write(item.to_str()+'\n')
		
