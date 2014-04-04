#estimates frequency of key words given a text, output is a dictionary with <Ngram, NgramEntry>
#assume the raw text format is <DOCID Separator Document>
import esm
from NgramEntry import NgramEntry
import time
import math


class FreqEst:
	
	def __init__(self,key_list,separator='$'):
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
		for l in text_list:
			self.search(l)

	#search a file
	def search_file(self,filename):
		f=open(filename,'r')
		for line in f:
			self.search(line)

	def get_freq(self):
		return self._table

	#export the resulting dictionary into a file
	def export_to_file(self,filename):
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
		
