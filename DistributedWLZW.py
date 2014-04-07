from mpi4py import MPI
from Split import Split
import os
import tempfile
from WLZW import WLZWCompressor
import time

class DistributedWLZW:
	
	def __init__(self,corpus,outputfile='wlzw_out'):
		self._comm=MPI.COMM_WORLD
		self._size=self._comm.Get_size()
		self._rank=self._comm.Get_rank()
		
		self._mode=MPI.MODE_RDONLY

		self._corpus=corpus

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
		result=wlzw.compress_file(self._corpus,np=1)

		#all gather the result to file
		result=self._comm.gather(result,root=0)

		#union the result
		final=set()
		if self._rank==0:
			for re in result:
				final=final | re

		#write the result back to file
		if self._rank==0:
			with open(outputfile,'w') as f:
				for w in final:
					f.write(w+'\n')

		#delete the file
		os.remove(path)

#test:
#curr=MPI.Wtime()
#dwlzw=DistributedWLZW('kb.txt')
#print MPI.Wtime()-curr
