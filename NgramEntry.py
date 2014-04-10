import json
#Data field for a NgramEntry
#Term Frequency | Document Frequency | Importance | N-gram | Positional information
#	Term Frequency: The number of times this n-gram has appeared in all documents in total
#        Document Frequency: The number of documents this n-gram has appeared in.
#        Importance: This should be JSON style as follows: {"TF-IDF": value, "MI": value, "RIDF": value} so that it is extensible in the future
#        N-gram: The n-gram whose statistics are being estimated
#        Positional information: The positions at which the n-gram has appeared in each document in the following format: {doc_id: [begin position, end position], doc_id: [begin position, end position], ...}

class NgramEntry:
	"""
	Represent a ngram entry. Includes the following info:

	tf - Term Frequency (int)

	df - Document Frequency (int)

	importance - [TFIDF,MI,RIDF] (list(float, float, float))

	ngram - ngram (string)

	position - position information (list(string, string, ...)) each string is "doc id:start position"
	
	It also includes utilities to convert importance to/from string, position to/from string

	The object can be turned into a string. Utilities for convert the object to/from string is also provided.
	The string is formated as follows (suppose '|' is used as separator):
	Term Frequency | Document Frequency | Importance | N-gram | Positional information
	where importance is {"TF-IDF": value, "MI": value, "RIDF": value}
	positional information is {doc_id: begin position, doc_id: begin position, ...}

	The separator can be specified by variable separator
	"""
	
	def __init__(self,ngram="",tf=0,df=0,importance=[0,0,0],position=None):
		"""Constructor giving the chance to specify the individual info. 
		@param ngram - string, the ngram itself
		@param tf - int, term frequency
		@param df - int, document frequency
		@param importance - [int,int,int], [TFIDF,MI,RIDF]
		@param position - [string,string,...], position information"""
		self.ngram=ngram
		self.tf=tf
		self.df=df
		self.importance=importance
		self.separator='||||'
		if position==None:
			self.position=[]
		else:
			self.position=position

	#return the position as a string (json like)
	def position_str(self):
		"""turn position information into a string
		@return str - the converted position str
		"""
		return "{%s}" % (",".join(self.position))
	
	def position_from_str(self,string):
		"""convert str to position information (stored in this object)
		@param string - the position string
		@return None
		"""
		self.position=string.split('{')[1].split('}')[0].split(',')

	def importance_str(self):
		"""Convert importance info into string
		@return string - the string converted from the importance info of the current object
		"""
		return "{\"TF_IDF\":%f,\"MI\":%f,\"RIDF\":%f}" % (self.importance[0],self.importance[1],self.importance[2])

	def importance_from_str(self,string):
		"""convert importance string to importance info (stored in this object)
		@param - string, the string to be converted
		"""
		j=json.loads(string)
		self.importance=[float(j['TF_IDF']),float(j['MI']),float(j['RIDF'])]

	def from_str(self,string):
		"""Convert string to NgramEntry object (stored in this object)
		@param string - the string to be converted
		"""
		s=string.split(self.separator)
		self.tf=int(s[0])
		self.df=int(s[1])
		self.ngram=s[3]
		self.importance_from_str(s[2])
		self.position_from_str(s[4])

	def to_str(self):
		"""Convert the object to String
		@return - str, the object representation in string
		"""
		l=[]
		l.append(str(self.tf))
		l.append(str(self.df))
		l.append(self.importance_str())
		l.append(self.ngram)
		l.append(self.position_str())
		return self.separator.join(l)
