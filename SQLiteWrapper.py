import sqlite3
import os
import sys
import argparse
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
		'''Construct query criteria for a single value (e.g. tf). Adding upper and lower bound into the query string.'''
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

	def entries_from_file(self,filename):
		'''Read NgramEntry from file.
		Each line is a NgramEntry in string.
		@param filename - input file name
		@return a list of NgramEntry'''
		l=[]
		with open(filename,'r') as f:
			for line in f:
				entry=NgramEntry()
				entry.from_str(line.strip())
				l.append(entry)
		return l

	def entries_to_file(self, entries, outputfile, ngram_only=False):
		'''Write NgramEntries to output file
		@param entries - a list of NgramEntry
		@param outputfile - the file name to write to
		@param ngram_only - write out only the ngram, default to false (write out the entire entry)
		'''
		with open(outputfile,'w') as f:
			for e in entries:
				if ngram_only:
					f.write(e.ngram+'\n')
				else:
					f.write(e.to_str()+'\n')

#command line support
#the following provide support for calling from command line
if __name__=='__main__':
        parser=argparse.ArgumentParser(description="SQL Module. Insert and select entries to or from sqlite.\n \
	Insert into DB: use -i. \n \
	Select from DB: do not use -i, use -o\n \
	Either -i or -o should be used but not both.\n \
	Select only the ngrams (not the entire entry): use -only_ngram",formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('-i',help='file of NgramEntry to insert into the DB, can be obtained from output of FreqEst.')
	parser.add_argument('-o',help='file to output the selected ngram entries')
	parser.add_argument('-ngram_only',help='only return the ngram rather than the whole entry if specified',action='store_true')
	#parameters for select
        parser.add_argument('-ngram',help='select a single ngram')
        parser.add_argument('-ngram_file',type=int,help='select a list of ngrams from a file, not supporting the parameters below')
        parser.add_argument('-tf_upper', type=float, help='upper bound of term frequency. do not specify if none')
        parser.add_argument('-tf_lower', type=float, help='lower bound of term frequency. do not specify if none')
        parser.add_argument('-df_upper', type=float, help='upper bound of document frequency. do not specify if none')
        parser.add_argument('-df_lower', type=float, help='lower bound of document frequency. do not specify if none')
        parser.add_argument('-tfidf_upper', type=float, help='upper bound of term frequency inverse document frequency. do not specify if none')
        parser.add_argument('-tfidf_lower', type=float, help='lower bound of term frequency inverse document frequency. do not specify if none')
        parser.add_argument('-mi_upper', type=float, help='upper bound of mutual information. do not specify if none')
        parser.add_argument('-mi_lower', type=float, help='lower bound of mutual information. do not specify if none')
        parser.add_argument('-ridf_upper', type=float, help='upper bound of residual inverse document frequency. do not specify if none')
        parser.add_argument('-ridf_lower', type=float, help='lower bound of residual inverse document frequency. do not specify if none')
        parser.add_argument('-pos', help='part of speech type. do not specify if none')
        parser.add_argument('-max_num', type=int, help='maximum number of returned results. do not specify if none')
        parser.add_argument('-tag', help='tag of ngrams to be selected. do not specify if none')

	#parse args
        args,unknown = parser.parse_known_args(sys.argv)

	#check -i and -o
	if (args.i!=None and args.o!=None) or (args.i==None and args.o==None):
		print 'Use either -i (insert entry) or -o (select entry)'
		exit(0)

	sql=SQLiteWrapper()

	if args.i!=None:
		#the insert case
		#check if the input file exists
		if not os.path.isfile(args.i):
			print 'Input file not exist. Check -i file.'
			exit(0)
		#insert into the db
		entries=sql.entries_from_file(args.i)
		sql.insert_many_entry(entries)
		
	elif args.o!=None:
		#the select case
		if args.ngram_file!=None and os.path.isfile(args.ngram_file): #select many ngrams (not supporting params)
			l=[]
			with open(args.ngram_file,'r') as f:
				for line in f:
					#read the ngrams and select
					l.append(line.strip())
			entries=sql.select_many_ngrams(l)
			sql.entries_to_file(entries, args.o, args.ngram_only)
		else: #select by criteria (params supplied)
			entries=sql.select_criteria(args.ngram,args.tf_upper,args.tf_lower,args.df_upper,args.df_lower,args.tfidf_upper,args.tfidf_lower,args.mi_upper,args.mi_lower,args.ridf_upper,args.ridf_lower,args.pos,args.max_num,args.tag)
			sql.entries_to_file(entries,args.o,args.ngram_only)
	
	
