import sqlite3
from NgramEntry import NgramEntry

#this class stores the ngram information into sqlite
class SQLiteWrapper:
	"""The class to access a SQLite database storing NgramEntry

	The table is created automatically when an SQLiteWrapper object is created. 
	Simply call insert or select functions to munipulate the table.
	Call close when done with the munipulation.
	"""
	
	def __init__(self):
		"""Constructor. Table and db is created automatically when called."""
		self._conn=sqlite3.connect('ngram.db')
		self._c=self._conn.cursor()
		self._create_table()

	def _create_table(self):
		self._c.execute('''CREATE TABLE IF NOT EXISTS ngram (ngram text primary key, tf real, df real, importance text, position text, pos text)''')

	#pass NgramEntry, insert single entry
	def insert_entry(self,entry):
		"""Insert a single entry into the table.
		When lots of entries are to be inserted, use insert_many_entry.
		If some ngram already exists in the table, the entry is updated with the newly inserted value.
		@param entry - NgramEntry to be inserted
		@return None"""
		#convert importance into text
		importance_str=entry.importance_str()
		#convert position into text
		position_str=entry.position_str()
		#insert into db
		self._c.execute('''INSERT OR REPLACE INTO ngram (ngram, tf, df, importance, position, pos) VALUES (?,?,?,?,?,?)''',(entry.ngram,entry.tf,entry.df,importance_str,position_str,entry.pos))
		self._conn.commit()

	
	#pass a list of entries
	def insert_many_entry(self,entry_list):
		"""Insert a list of NgramEntry into the table.
		If some ngram already exists in the table, the entry is updated with the newly inserted value.
		@param entry_list - list(NgramEntry)
		@return None
		"""
		l=[]
		for entry in entry_list:
			l.append((entry.ngram,entry.tf,entry.df,entry.importance_str(),entry.position_str(),entry.pos))
		self._c.executemany('''INSERT OR REPLACE INTO ngram (ngram, tf, df, importance, position, pos) VALUES (?,?,?,?,?,?)''',l)
		self._conn.commit()

	#pass a ngram string, return a entry
	def select_ngram(self,string):
		"""Select an Ngram from the database.
		@param - string, the ngram string
		@return NgramEntry"""
		self._c.execute('''SELECT * FROM ngram WHERE ngram=?''',(string,))
		s=self._c.fetchone()
		if s==None:
			return None
		entry=NgramEntry()
		entry.tf=int(s[1])
		entry.df=int(s[2])
		entry.importance_from_str(s[3])
		entry.ngram=s[0]
		entry.position_from_str(s[4])
		entry.pos=s[5]
		return entry

	def select_many_ngrams(self,l):
		"""Select an list of ngrams from the database
		@param l - the list of ngrams
		@return list of NgramEntry"""
		result=[]
		for ngram in l:
			result.append(self.select_ngram(ngram))
		return result

	def close(self):
		"""Close the database connection.
		Should be called when finish using this wrapper.
		@return None"""
		self._c.close()
	
	def update_pos(self,entry):
		"""Update the pos of an entry.
		@param entry - the ngram whose pos is to be updated
		@return None"""
		self.insert_entry(entry)
