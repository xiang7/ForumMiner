import nltk
from SQLiteWrapper import SQLiteWrapper
import re
import argparse
import os
import sys

class POSMatcher:
	"""This class defines POS patterns to be matched"""
	def __init__(self):
		an=re.compile(r'JJ NN[PS]*')
		nn=re.compile(r'NN[PS]* NN[PS]*')
		aan=re.compile(r'JJ JJ NN[PS]*')
		ann=re.compile(r'JJ NN[PS]* NN[PS]*')
		nan=re.compile(r'NN[PS]* JJ NN[PS]*')
		nnn=re.compile(r'NN[PS]* NN[PS]* NN[PS]*')
		npn=re.compile(r'NN[PS]* IN NN[PS]*')
		self._p=[an,nn,aan,ann,nan,nnn,npn]

	def match(self,pos):
		"""If a pos string matchs the template
		@param pos - the pos string
		@return - True of False
		"""
		for p in self._p:
			if p.match(pos.strip()):
				return True
		return False

class POSTagger:
	"""This class matches POS for frequent patterns
	It takes the file of the documents, the ngram table as input. 
	First it scan through the document, get the ID - byte position pair to make file seek easy
	For each ngram, find each document and then the sentence containing the ngram, tag it and vote. store the result.
	"""	

	def __init__(self, filename, separator):
		"""
		@param filename - the path of the file containing the documents
		@param separator - the string between DOC ID and DOC
		"""
		self._file=filename #the path of file containing the documents
		self._table=dict() #the dict storing doc id - byte position pair
		self._separator=separator #separator between Doc ID and doc
                self._tokenizer=nltk.data.load('tokenizers/punkt/english.pickle') #sentence tokenizer

		#scan through the document, store the doc id - position pair
		with open(self._file, 'r') as f:
			curr=f.tell()
			line=f.readline()
			while line != "":
				doc_id=line.split(self._separator,1)[0]
				self._table[doc_id]=curr
				curr=f.tell()
				line=f.readline()
		
		self._f=open(self._file,'r') #read the file
			

	def tag(self, entry):
		"""Tag an NgramEntry"""
		pos_table=dict() #stores pos string and count
		unigrams=nltk.word_tokenize(entry.ngram)

		for p in entry.position:
			[docid, docpos]=p.split(':')
			#seek to the doc
			self._f.seek(self._table[docid])
			#read the doc
			line=self._f.readline();
			#peel off the doc id
			d=line.split(self._separator,1)
			if len(d) !=2:
				continue
			line=d[1]
			#break it into sentences
                	s=self._tokenizer.tokenize(line)
			#find the sentence containing the phrase
			sen=""
			for sen in s:
				if entry.ngram in sen:
					break
			if entry.ngram not in sen:
				continue
			#tag it
			words=nltk.word_tokenize(sen)
			tags=nltk.tag.pos_tag(words)
			#find the tags of the phrase, convert to String and store it
			tag_list=[]
			for i in range(0,len(tags)-len(unigrams)):
				if words[i:i+len(unigrams)] == unigrams:
					for (w,t) in tags[i:i+len(unigrams)]:
						tag_list.append(t)
					break
			tag_str=" ".join(tag_list)
			if tag_str in pos_table:
				pos_table[tag_str]+=1
				if entry.tf/2<pos_table[tag_str]:
					return tag_str
			else:
				pos_table[tag_str]=1
		#find the max string, return it
		curr_max=0
		curr_str=""
		for s in pos_table:
			if pos_table[s]>curr_max:
				curr_max=pos_table[s]
				curr_str=s
		return curr_str


def test(filepath,separator):
	sql=SQLiteWrapper()
	entry=sql.select_criteria(maxnum=1000)
	tagger=POSTagger(filepath,separator)
	count=0
	for e in entry:
		s=tagger.tag(e)
		e.pos=s
		sql.update_pos(e)
		count+=1
		if count%100==0:
			print count

#test('kb.txt','$')

if __name__=='__main__':
        parser=argparse.ArgumentParser(description='Part of Speech tagging. Tag phrases and update the DB.')
        parser.add_argument('-i', help='required, input file (corpus that populated the DB)',required=True)
        parser.add_argument('-l', help='file of list of ngrams to be tagged (words in the corpus), or use -a to tag all words in db')
	parser.add_argument('-s',help='seperator between doc id and doc content, default to $')
	parser.add_argument('-a', help='tag all words in db',action='store_true')
        parser.add_argument('-o', help='output file (of ngrams and their tags), default not print to outfile')
	parser.add_argument('-u', help='update db when specified, default not to update db', action='store_true')
	parser.add_argument('-m',help='only ouput or update matched tags',action='store_true')

        #parse args
        args,unknown = parser.parse_known_args(sys.argv)

	#check input file
	if not os.path.isfile(args.i):
		print 'Input file not exist. Check -i file.'
		exit(0)
	
	#check -a and -l
	if (not args.a and args.l is None) or (args.a and args.l!=None):
		print 'Need to specify either tag all ngram in db (-a) or supply a list of ngrams (-l)'
		exit(0)

	sql=SQLiteWrapper()
	entries=[]	

	if args.a: #get entire db
		entries=sql.select_criteria()
	elif args.l!=None: #read the list in
		if not os.path.isfile(args.l):
			print 'File of list of ngrams does not exist. Check -l file.'
			exit(0)
		l=[]
		with open(args.l,'r') as f:
			for line in f:
				l.append(line.strip())
		entries=sql.select_many_ngrams(l)

	#separator of doc id and doc content
	separator='$'
	if args.s!=None:
		separator=args.s

	tagger=POSTagger(args.i,separator)
	matcher=POSMatcher()
	result=dict()

	for e in entries:
		r=tagger.tag(e)
		if not args.m or (args.m and matcher.match(r)): #if match is needed
			result[e]=r
			e.pos=r
	
	#if update db
	if args.u:
		sql.insert_many_entry(result.keys())

	#if output to file
	if args.o != None:
		with open(args.o,'w') as f:
			for e in result:
				f.write(e.ngram+','+result[e]+'\n')
