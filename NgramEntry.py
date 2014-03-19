#Data field for a NgramEntry
#Term Frequency | Document Frequency | Importance | N-gram | Positional information
#	Term Frequency: The number of times this n-gram has appeared in all documents in total
#        Document Frequency: The number of documents this n-gram has appeared in.
#        Importance: This should be JSON style as follows: {"TF-IDF": value, "MI": value, "RIDF": value} so that it is extensible in the future
#        N-gram: The n-gram whose statistics are being estimated
#        Positional information: The positions at which the n-gram has appeared in each document in the following format: {doc_id: [begin position, end position], doc_id: [begin position, end position], ...}

class NgramEntry:
	
	def __init__(self,ngram="",tf=0,df=0,importance=[0,0,0],position=None):
		self.ngram=ngram
		self.tf=tf
		self.df=df
		self.importance=importance
		if position==None:
			self.position=[]
		else:
			self.position=position

	
