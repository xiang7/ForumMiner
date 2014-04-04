import sqlite3
from NgramEntry import NgramEntry

#this class stores the ngram information into sqlite
class SQLiteWrapper:
	
	def __init__(self):
		self._conn=sqlite3.connect('ngram.db')
		self._c=self._conn.cursor()
		self.create_table()

	def create_table(self):
		self._c.execute('''CREATE TABLE IF NOT EXISTS ngram (ngram text primary key, tf real, df real, importance text, position text)''')

	#pass NgramEntry, insert single entry
	def insert_entry(self,entry):
		#convert importance into text
		importance_str=entry.importance_str()
		#convert position into text
		position_str=entry.position_str()
		#insert into db
		self._c.execute('''INSERT OR REPLACE INTO ngram (ngram, tf, df, importance, position) VALUES (?,?,?,?,?)''',(entry.ngram,entry.tf,entry.df,importance_str,position_str))
		self._conn.commit()

	
	#pass a list of entries
	def insert_many_entry(self,entry_list):
		l=[]
		for entry in entry_list:
			l.append((entry.ngram,entry.tf,entry.df,entry.importance_str(),entry.position_str()))
		self._c.executemany('''INSERT OR REPLACE INTO ngram (ngram, tf, df, importance, position) VALUES (?,?,?,?,?)''',l)
		self._conn.commit()

	#pass a ngram string, return a entry
	def select_ngram(self,string):
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
		return entry

	def close(self):
		self._c.close()
