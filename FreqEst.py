#estimates frequency of key words given a text
from acora import AcoraBuilder


class FreqEst:
	
	def __init__(self,key_list):
		self._key_list=key_list
		self._builder = AcoraBuilder(self._key_list)
		self._ac = self._builder.build()
		self._table = dict()

	def _isBlankSpace(self,w):
		if w==' ' or w=='\t' or w=='\n':
			return True

	#search a string
	def search(self, text):
		for w, f in self._ac.findall(text):
			if (f!=0 and (not self._isBlankSpace(text[f-1]))) or (f+len(w)<len(text) and (not self._isBlankSpace(text[f+len(w)]))):
				continue
			if w not in self._table:
				self._table[w]=1
			else:
				self._table[w]+=1

	#search a list
	def search_list(self,text_list):
		for l in text_list:
			self.search(l)

	def get_freq(self):
		return self._table
