"""The module to let user input a list of phrases and their tags. 
It also uses the tagged phrases to tag new text and annotate the tags of matched phrases."""

from NgramEntry import NgramEntry
from SQLiteWrapper import SQLiteWrapper
import esm
import nltk
import string
import os
import sys
import argparse

class PhraseTagger:
	"""Insert tag of given phrases into the DB"""
	
	def __init__(self):
		self._sql=SQLiteWrapper() #the wrapper
	
	def tag(self, tdict):
		"""Update the phrases' tag in DB.
		@param tdict - dictionary of [ngram : tag]"""
		entries=[]
		#for each ngram, select from db, see if it exist
		#if yes insert its tag, else skip
		for k in tdict:
			entry=self._sql.select_ngram(k)
			if entry==None:
				continue
			entry.tag=tdict[k]
			entries.append(entry)
		self._sql.insert_many_entry(entries)
	
	def read_dict(self, filename, separator=' '):
		"""Read the dictionary from a file.
		Format: ngram [separator] tag [newline] ...
		@param filename - the input file name
		@param separator - the separator string between ngram and tag
		@return dict [ngram : tag]"""
		tdict=dict()
		with open(filename,'r') as f:
			for line in f:
				s=line.strip().split(separator,1)
				if len(s)<2:
					print 'error, check separator: ngram [separator] class_tag'
					exit(0)
				tdict[s[0]]=s[1]
		return tdict
			

	def tag_from_file(self, filename, separator=' '):
		"""Read the dictionary from a file and update the tag into DB
		Format: ngram [separator] tag [newline] ...
		@param filename - the input file name
		@param separator - the separator string between ngram and tag
		@return dict [ngram : tag]"""
		self.tag(self.read_dict(filename,separator))


class ClassTagger:
	"""Build a matcher from all tagged ngrams in DB. Match in new text/file. """

	def __init__(self):
		"""Matcher is build in the constructor. Can call tag methods multiple times. 
		If update is made to DB, initiate a new tagger."""
		self._sql=SQLiteWrapper()
		#select all tagged entries
		self._tdict=self._sql.select_tagged_ngram()
		#build the matcher
		self._index=esm.Index()
		for k in self._tdict:
			self._index.enter(k)
		self._index.fix()
		#initialize sentence tokenizer
		self._tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
                #s=tokenizer.tokenize(uncompressed)	
	
	def tag_new_sent(self, sent):
		"""tag a new sentence
		@param sent - str, the sentence to be tagged
		@return str - the tagged sentence"""
		#search the sentence
		s=self._index.query(sent)
		#get all the matched ngrams
		words=set()
		for (stt,end),w in s:	
			words.add(w.strip())
		#replace the text with tagged words
		for w in words:
			sent=string.replace(sent,w,('('+w+') / '+self._tdict[w]))
		return sent

	def tag_new_file(self, filename, outputfile):
		"""tag a new file. 
		@param filename - input file name
		@param outputfile - outputfile name"""
		f = open(filename,'r')
		fout = open(outputfile,'w')
		for line in f:
			tmp=[]
			s=self._tokenizer.tokenize(line.strip())
			for sent in s:
				tmp.append(self.tag_new_sent(sent))
			fout.write(' '.join(tmp))
			fout.write('\n')
		f.close()
		fout.close()


def test():
	#insert taggs
	pt=PhraseTagger()
	pt.tag_from_file('test_tag_phrase','\t')
	
	#tag new sentence
	ct=ClassTagger()
	ct.tag_new_file('test_tag_text','test_tag_out')

#test()

#command line support
#the following provide support for calling from command line
if __name__=='__main__':
        parser=argparse.ArgumentParser(description='Insert tags of ngram into DB and use them to tag new text.')
        parser.add_argument('-i',help='input file for insert tag of ngrams into DB. format: [ngram [separator] tag]')
	parser.add_argument('-s',help='insert tag file separator, default to space')
        parser.add_argument('-t',help='input file for tagging')
        parser.add_argument('-to', help='output file for tagged file')

        #parse args
        args,unknown = parser.parse_known_args(sys.argv)

	if args.i!=None: #insert tags for ngrams
		#check if the file exist
		if not os.path.isfile(args.i):
			print 'input file not exist. check -i file.'
			exit(0)
		#get the separator
		separator=' '
		if args.s != None:
			separator=args.s
		#insert tag into db
		pt=PhraseTagger()
		pt.tag_from_file(args.i, separator)

	if args.t!=None: #tag new file using existing ngrams with tags
		#check if the file exist
		if not os.path.isfile(args.t):
			print 'input file not exist, check -t file.'
			exit(0)
		if args.to is None: #exit if no output needed
			exit(0)
		#tag new file
		ct=ClassTagger()
		ct.tag_new_file(args.t,args.to)
		
