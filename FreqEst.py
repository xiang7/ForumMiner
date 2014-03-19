#estimates frequency of key words given a text, output is a dictionary with <Ngram, NgramEntry>
#assume the raw text format is <DOCID Separator Document>
from acora import AcoraBuilder
from NgramEntry import NgramEntry
import time


class FreqEst:
	
	def __init__(self,key_list,separator='$'):
		print len(key_list)
		self._key_list=key_list[1:500]
		prev=time.time()
		self._builder = AcoraBuilder(self._key_list)
		self._ac = self._builder.build()
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
		for w, f in self._ac.findall(text):
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
				#compute tf-idf TODO
				tfidf=0.0
				#compute ridf TODO
				ridf=0.0
				#compute mi TODO
				mi=0.0
				f.write("%d|%d|{\"TF_IDF\":%f,\"MI\":%f,\"RIDF\":%f}|%s|{%s}\n" % (item.tf,item.df,tfidf,mi,ridf,k,",".join(item.position)))
		
