import nltk
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
		

	def get_dict(self):	
		""""return the class dictionary. should be called after all text is compressed"""
		return self._dictionary
	
	def get_pattern(self):
		return self._dictionary.keys() 
	 

