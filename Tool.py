"""Provide simple tools for processing text"""
class Split:
	"""Split files by line.
	
	File is split once the object is initialized. 
	Output file names can be specified. 
	If not, file names will be generated automatically.
	A list of output filenames can be obtained by calling get_filenames."""

	def __init__(self,corpus,n=1,filenames=None):
		"""File is split by initializing the function.
		@param corpus - string, file path of the corpus
		@param n - number of files into which the corpus will be split
		@param filenames - a list of output filenames. Number of elements in filenames should be equal to n"""
		self._corpus=corpus
		self._n=n

		if filenames == None:
			self._filenames=[str(x) for x in range(0,n)]
		else:
			self._filenames=filenames

		if len(self._filenames) != n:
			raise Exception("Error from split: number of file names should be the same with n")

		self.__split_lines()
		
		

	def __split_lines(self):
		#count number of lines
		count=0
		with open(self._corpus,'r') as f:
			for line in f:
				count+=1

		#split the file
		local_count=0
		local_i=0
		local_f=None
		with open(self._corpus,'r') as f:
			for line in f:
				if local_count==0 and local_i<self._n:
					if local_f is not None:
						local_f.close()
					local_f=open(self._filenames[local_i],'w')
#					print local_i,self._filenames
					local_i+=1
				local_f.write(line)
				local_count = (local_count+1) % (count/self._n)
		
#       to be implemented
#	def __split_bytes(self):

	def get_filenames(self):
		"""Get the output file names
		@return list - list of filenames"""
		return self._filenames

#test:
#split=Split('kb.txt',3,['11','22','33'])
#print split.get_filenames()

