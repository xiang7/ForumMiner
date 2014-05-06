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
		self._c.execute('''CREATE TABLE IF NOT EXISTS ngram (ngram text primary key, tf real, df real, tfidf real, mi real, ridf real, position text, pos text, tag text)''')

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
		self._c.execute('''INSERT OR REPLACE INTO ngram (ngram, tf, df, tfidf, mi, ridf, position, pos, tag) VALUES (?,?,?,?,?,?,?,?,?)''',(entry.ngram,entry.tf,entry.df,entry.importance[0], entry.importance[1], entry.importance[2],position_str,entry.pos, entry.tag))
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
			l.append((entry.ngram,entry.tf,entry.df,entry.importance[0], entry.importance[1],entry.importance[2],entry.position_str(),entry.pos,entry.tag))
		self._c.executemany('''INSERT OR REPLACE INTO ngram (ngram, tf, df, tfidf, mi, ridf, position, pos, tag) VALUES (?,?,?,?,?,?,?,?,?)''',l)
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
		return self._row_to_entry(s)

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

	def select_criteria(self, ngram=None, tf_upper=None, tf_lower=None, df_upper=None, df_lower=None, tfidf_upper=None, tfidf_lower=None, mi_upper=None, mi_lower=None, ridf_upper=None, ridf_lower=None,pos=None, maxnum=None, tag=None):
		"""
		Select ngram by criteria specified.
		If a parameter is None, then ngram is not filtered by this parameter.
		"""
		query="select * from ngram"
		first=True

		if ngram!=None:
			query+=" where ngram=='"+ngram+"'"
			first=False
		if pos!=None:
			if first:
				query+=" where pos=='"+pos+"'"
				first=False
			else:
				query+=" and pos=='"+pos+"'"
		if tag!=None:
			if first:
				query+=" where tag=='"+tag+"'"
				first=False
			else:
				query+=" and tag=='"+tag+"'"

		[query,first]=self._constr_criteria(query,"tf",tf_lower,tf_upper,first)
		[query,first]=self._constr_criteria(query,"df",df_lower,df_upper,first)
		[query,first]=self._constr_criteria(query,"tfidf",tfidf_lower,tfidf_upper,first)
		[query,first]=self._constr_criteria(query,"mi",mi_lower,mi_upper,first)
		[query,first]=self._constr_criteria(query,"ridf",ridf_lower,ridf_upper,first)

		self._c.execute(query)
		count=0
		result=[]
		s=self._c.fetchone()
		while s!=None:
			result.append(self._row_to_entry(s))
			count+=1
			if maxnum!=None and count>=maxnum:
				break
			s=self._c.fetchone()
		return result

	def select_tagged_ngram(self):
		"""Select tagged ngrams from the database
		@return dict [ngram : tag]
		"""
		self._c.execute('''SELECT ngram,tag FROM ngram WHERE tag!=""''')
		tdict=dict()
		s=self._c.fetchone()
		while s!=None:
			tdict[s[0]]=s[1]
			s=self._c.fetchone()
		return tdict

	def _row_to_entry(self,s):
		entry=NgramEntry()
		entry.tf=int(s[1])
		entry.df=int(s[2])
		entry.importance=[float(s[3]),float(s[4]),float(s[5])]
		entry.ngram=s[0]
		entry.position_from_str(s[6])
		entry.pos=s[7]
		entry.tag=s[8]
		return entry

		

	def _constr_criteria(self,query, field, lower=None, upper=None, first=False):
		if first:
			connect=" where"
		else:
			connect=" and"

		if upper!=None and lower!=None:
			query+=connect
			query+=" "+field+"<"+str(upper)+" and "+field+">"+str(lower)
			first=False
		elif upper!=None:
			query+=connect
			query+=" "+field+"<"+str(upper)
			first=False
		elif lower!=None:
			query+=connect
			query+=" "+field+">"+str(lower)
			first=False
		return [query,first]
