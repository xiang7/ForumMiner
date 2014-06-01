import WLZW
import FreqEst
import SQLiteWrapper
import POS
import ClassTagger
import unittest

class tests(unittest.TestCase):

	def setUp(self):
		self.corpus='test_data/corpus'
		self.patterns='test_data/patterns'
		self.entries='test_data/entries'
		self.tag='test_data/tags'
		self.tagged='test_data/tagged'
		self.pattern=None

	def test_WLZW(self):
		wlzw=WLZW.WLZWCompressor()
		wlzw.compress_file(self.corpus,separator='$')
		pattern=wlzw.get_pattern()
		self.pattern=pattern
		with open(self.patterns,'w') as f:
			for w in pattern:
				f.write(w.strip()+'\n')
		self.assertEqual(len(pattern),102)
		
	
	def test_Parallel_WLZW(self):
		pwlzw=WLZW.ParallelWLZW()
		pattern=pwlzw.compress_file(self.corpus,4,separator='$')
		self.assertEqual(len(pattern),69)

	def test_FreqEst(self):
		self.test_WLZW()
		fe=FreqEst.FreqEst(list(self.pattern))
		fe.search_file(self.corpus)
		fe.export_to_file(self.entries)
		self.assertEqual(len(fe.get_freq()),102)

	def test_SQLiteWrapper(self):
		sql=SQLiteWrapper.SQLiteWrapper()
		en=sql.entries_from_file(self.entries)
		sql.insert_many_entry(en)
		en_new=sql.select_criteria()
		self.assertEqual(len(en_new),102)

	def test_POS(self):
		sql=SQLiteWrapper.SQLiteWrapper()
		en=sql.entries_from_file(self.entries)
		pos=POS.POSTagger(self.corpus,'$')
		t=pos.tag(en[0])
		if 'PRP$ NN' != t.strip():
			raise Error('POS error')

	def test_ClassTagger(self):
		pt=ClassTagger.PhraseTagger()
		pt.tag_from_file(self.tag,'\t')
		ct=ClassTagger.ClassTagger()
		ct.tag_new_file(self.corpus,self.tagged)
		text=open(self.tagged,'r').read()
		if 'ACTION' not in text:
			raise Error('ClassTagger error')
		if 'ENTITY' not in text:
			raise Error('ClassTagger error')
		if 'NONE' in text:
			raise Error('ClassTagger error')

if __name__=='__main__':
	unittest.main()
