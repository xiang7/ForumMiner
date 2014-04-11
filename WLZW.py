import nltk
import os
from multiprocessing import Pool
import copy_reg 
import time
import concurrent.futures
from mpi4py import MPI
from Tool import Split
import os
import tempfile

#To construct WLZW
#Dictionary is returned which is the hot pattern
#Dictionary started with empty set
#Index by words for WLZW
#Keep dictionary as class memember since compress is called sentence by sentence
#nltk needed, data in nltk needed as well

class WLZWCompressor:
	"""
	The class for WLZW Compressor. 
	This class takes in text as string or file and runs WLZW on it. 
	Upon completion, the dictionary can be obtained. One dictionary is associated with one compressor instance. 
	Multiple calls of any compress functions would contribute to the same dictionary. 
	At the end, get_pattern can be called to retrieve all the patterns built across all the compress calls. 
	Function compress_file_parallel will return the patterns at the end of the call
	Example:
	@code
	from WLZW import WLZWCompressor

	compressor1=WLZWCompressor()
	patterns=compressor.compress_file_parallel(filename,4)

	compressor2=WLZWCompressor()
	for line in f:
		compressor2.compress(line)
	patters=compressor2.get_patterns
	@endcode
	"""
	
	def __init__(self):
		"""Dictionary is initialized when the constructor is called"""
		# Build the dictionary.
		self._dict_size = 0
		self._dictionary = dict()

	def compress_sent(self,uncompressed):
		"""Process the sentence with WLZW algorithm. 
		At the same time, the dictionary is constructed. Dictionary is shared on same object accross multiple calls. 
		This function does not tokenize sentences.
		@param uncompressed - string, the sentence to be compressed
		@return None, need to call get_pattern to retrieve the dictionary
		"""

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
		"""Process a chunk of text with WLZW algorithm. Dictionary is constructed at the same time. 
		@param uncompressed - string, it is tokenized into sentences with NLTK's tokenizer
		@return None, need to call get_pattern to retrieve the dictionary
		"""
		#sentence tokenizer
		tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
		s=tokenizer.tokenize(uncompressed)

		for c in s:
			self.compress_sent(c)
	
	#corpus: file name
	#p: number of processes
	def compress_file(self,corpus, separator=None):
		"""
		Construct WLZW pattern out of a corpus (a file). 
		Separator is the separator string between doc id and the document if exist. If not exist, don't pass anything to it.
		@param corpus - the path to the file
		@param separator - the string that separates doc id and document. Don't pass anything if no doc id is given
		@return None, need to call get_parttern to retrieve the dictionary
		"""

		#construct a sentence tokenizer here since if load a tokenizer for each line is expensive
		tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
		
		with open(corpus,'r') as f:
			for line in f:
				if separator!=None:
					s=line.split(separator)
					line=separator.join(s[1:])
				sents=tokenizer.tokenize(line)
				for sent in sents:
					self.compress_sent(sent)
			

	def __get_dict(self):	
		"""return the class dictionary. should be called after all text is compressed"""
		return self._dictionary
	
	def get_pattern(self):
		"""Get the frequent patterns out of the compressor
		@return a list of strings, the frequent patterns build through calls of compress functions
		"""
		return self._dictionary.keys() 

class ParallelWLZW:
	"""
	The class to run WLZW in shared memory model

	Example:
	@code
	compressor=ParallelWLZW()
	result=compressor.compress_file('filename.txt',4)
	@endcode
	"""

	#corpus: file name
        #p: number of processes
        def compress_file(self,corpus, np=4,separator=None):
                """
		construct WLZW pattern out of a corpus, parallelism is an option
		@param corpus - string, file path of the corpus
		@param np - number of processes, if np = 1 the algorithm is run in serial
		@param separator - the separator string to separate doc id and document. pass None if no doc id is given
		@return set, the final set containing all frequent patterns
		"""

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

class DistributedWLZW:
	"""
	The class to run WLZW in distributed memory model. 
	Dictionary does not persist through multipul calls of compress_file.
	The parameters related to distributed computing is supplied at run time:
	mpirun -np 4 -machines MachineFile python test.py
	Example:
	@code
	dwlzw=DistributedWLZW()
        final_set=dwlzw.compress_file('filename.txt')
	@endcode
	"""

        def __init__(self):
                self._comm=MPI.COMM_WORLD
                self._size=self._comm.Get_size()
                self._rank=self._comm.Get_rank()

                self._mode=MPI.MODE_RDONLY

	def compress_file(self,corpus,separator=None):
		"""Compress file in distributed memory model
		@param corpus - string, file path of the corpus
		@param separator - the separtor string between doc id and doc, pass None if no doc id
		@return set, the frequent patterns
		"""
                files=[]
                #split the corpus
                if self._rank==0:
                        split=Split(corpus,self._size)
                        files=split.get_filenames()
                else:
                        split=None
                #scatter the corpus
                unit=self._comm.scatter(files,root=0)

                #read the corpus, count lines, print
                f=MPI.File.Open(self._comm,unit,self._mode)
                ba = bytearray(f.Get_size())
                # read the contents into a byte array
                f.Iread(ba)
                # close the file
                f.Close()
                # write buffer to a tempfile
                descriptor, path = tempfile.mkstemp(suffix='mpi'+str(self._rank)+'.txt')
                tf = os.fdopen(descriptor, 'w')
                tf.write(ba)
                tf.close()

		#call WLZW
                wlzw=WLZWCompressor()
                wlzw.compress_file(corpus,separator)
		result=set(wlzw.get_pattern())

                #all gather the result to file
                result=self._comm.gather(result,root=0)

                #union the result
                final=set()
                if self._rank==0:
                        for re in result:
                                final=final | re

                #delete the file
                os.remove(path)
                #write the result back to file or return
		return final


def _union(l):
	"""helper functions to test for a more efficient union. not used in the class code"""
	result=set()
	for re in l:
		result = result | set(re)
	return result

def _union_recur(l):
	"""helper functions to test for a more efficient union. not used in the class code"""
	if len(l)==2:
		return l[1] | l[0]
	return _union_recur(l[0:len(l)/2]) | _union_recur(l[len(l)/2:len(l)])

def _union_binary_tree(l,np):
	"""helper functions to test for a more efficient union. not used in the class code"""
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
	"""helper functions to test for a more efficient union. not used in the class code"""
	re=l[0] | l[1]
	return re

def _union_list(l):
	"""helper functions to test for a more efficient union. not used in the class code"""
	result=[]
	for s in l:
		result.extend(s)
	return set(result)

def _compress_chunk(chunk):
	"""helper functions to test for a more efficient union. not used in the class code"""
	wlzw=WLZWCompressor()
	f=open(chunk,'r')
	for line in f:
		wlzw.compress(line)
	return set(wlzw.get_pattern())

#compress function used for map (shared memory parallelization). 
def _compress_file(tup):
	"""Compress file. This is used because it's much easier to put function not in a class to map function. 
	This is used for parallel computation in shared memory model. Map is applied to this function"""
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
