import json
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
		self.seperator='||||'
		if position==None:
			self.position=[]
		else:
			self.position=position

	#return the position as a string (json like)
	def position_str(self):
		return "{%s}" % (",".join(self.position))
	
	def position_from_str(self,string):
		self.position=string.split('{')[1].split('}')[0].split(',')

	def importance_str(self):
		return "{\"TF_IDF\":%f,\"MI\":%f,\"RIDF\":%f}" % (self.importance[0],self.importance[1],self.importance[2])

	def importance_from_str(self,string):
		j=json.loads(string)
		self.importance=[float(j['TF_IDF']),float(j['MI']),float(j['RIDF'])]

	def from_str(self,string):
		s=string.split(self.seperator)
		self.tf=int(s[0])
		self.df=int(s[1])
		self.ngram=s[3]
		self.importance_from_str(s[2])
		self.position_from_str(s[4])

	def to_str(self):
		l=[]
		l.append(str(self.tf))
		l.append(str(self.df))
		l.append(self.importance_str())
		l.append(self.ngram)
		l.append(self.position_str())
		return self.seperator.join(l)
