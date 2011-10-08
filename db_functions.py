import MySQLdb
from settings import *

#user joins channel, takes 2 arguments name and ip
def add_user(name,ip):
	conn = MySQLdb.connect (host = db_server,user = db_username,passwd = db_password,db = db_name)
	cursor = conn.cursor ()
	if cursor.execute ("SELECT * FROM users WHERE ip=%s",(ip)) or cursor.execute ("SELECT * FROM users WHERE name=%s",(name)):
		user = cursor.fetchone()
		cursor.execute("UPDATE users SET name = %s, ip = %s WHERE ID=%s",(name,ip,user[0]))
	else:
		cursor.execute ("INSERT INTO users(ID,name,ip,strikes)VALUES(NULL, %s, %s, 0)",(name,ip))
		return True
	cursor.close()
	conn.close()
	
#updates user, takes 2 argument orname and newname
def update_user(orname,newname):
	conn = MySQLdb.connect (host = db_server,user = db_username,passwd = db_password,db = db_name)
	cursor = conn.cursor ()
	if cursor.execute ("SELECT * FROM users WHERE name=%s",(orname)):
		user = cursor.fetchone()
		cursor.execute("UPDATE users SET name = %s WHERE ID=%s",(newname,user[0]))
		print "updates"
	cursor.close()
	conn.close()

#clears the user from database, takes name only as argument, it will return true if user was cleared, is mainly to prevent errors if a wrong user is cleared
def clear_user(name):
	conn = MySQLdb.connect (host = db_server,user = db_username,passwd = db_password,db = db_name)
	cursor = conn.cursor ()
	if cursor.execute("SELECT * FROM users WHERE name=%s",(name)):
		user = cursor.fetchone()
		cursor.execute("UPDATE users SET strikes = 0 WHERE ID=%s",(user[0]))
		return True
	else:
		return False
		
#mutes a user, takes in 1 argument, the name
def mute_user(name):
	conn = MySQLdb.connect (host = db_server,user = db_username,passwd = db_password,db = db_name)
	cursor = conn.cursor ()
	if cursor.execute("SELECT * FROM users WHERE name=%s",(name)):
		user = cursor.fetchone()
		cursor.execute("UPDATE users SET strikes = 5 WHERE ID=%s",(user[0]))
		return True
	else:
		return False

#checks if user can have voice
def can_voice(name):
	conn = MySQLdb.connect (host = db_server,user = db_username,passwd = db_password,db = db_name)
	cursor = conn.cursor ()
	if cursor.execute("SELECT * FROM users WHERE name=%s",(name)):
		user = cursor.fetchone()
		if user[3] >= 3:
			return False
		else:
			return True
	cursor.close()
	conn.close()
	
#pulls all the mods authname from the database
def update_mods():
    conn = MySQLdb.connect (host = db_server,
                       user = db_username,
                       passwd = db_password,
                       db = db_name)
    cursor = conn.cursor ()
    cursor.execute ("SELECT name FROM mods")
    numrows = int(cursor.rowcount)
    words_temp = ""
    for i in range(numrows):
        row = cursor.fetchone()
        words_temp += str(row[0]) + ','
    
    words_temp = words_temp.rstrip(',')
    mods = words_temp.split(',')
    return mods
    cursor.close ()
    conn.close ()

#add joke to database
def add_joke(joke):
	conn = MySQLdb.connect (host = db_server,user = db_username,passwd = db_password,db = db_name)
	cursor = conn.cursor ()
	cursor.execute ("INSERT INTO joke(ID, joke)VALUES(NULL, %s)",(joke))
	cursor.close()
	conn.close()

#pulls all the keywords from the database
def update_keywords():
    conn = MySQLdb.connect (host = db_server,
                       user = db_username,
                       passwd = db_password,
                       db = db_name)
    cursor = conn.cursor ()
    cursor.execute ("SELECT word FROM keywords")
    numrows = int(cursor.rowcount)
    words_temp = ""
    for i in range(numrows):
        row = cursor.fetchone()
        words_temp += str(row[0]) + ','
    
    words_temp = words_temp.rstrip(',')
    keywords = words_temp.split(',')
    return keywords
    cursor.close ()
    conn.close ()

#pulls all the whinewords from the database
def update_whinewords():
    conn = MySQLdb.connect (host = db_server,
                       user = db_username,
                       passwd = db_password,
                       db = db_name)
    cursor = conn.cursor ()
    cursor.execute ("SELECT word FROM whinewords")
    numrows = int(cursor.rowcount)
    words_temp = ""
    for i in range(numrows):
        row = cursor.fetchone()
        words_temp += str(row[0]) + ','
    
    words_temp = words_temp.rstrip(',')
    whinewords = words_temp.split(',')
    return whinewords
    cursor.close ()
    conn.close ()

#updates all the banned words from the database
def update_banwords():
    conn = MySQLdb.connect (host = db_server,
                       user = db_username,
                       passwd = db_password,
                       db = db_name)
    cursor = conn.cursor ()
    cursor.execute ("SELECT word FROM ban_words")
    numrows = int(cursor.rowcount)
    words_temp = ""
    for i in range(numrows):
        row = cursor.fetchone()
        words_temp += str(row[0]) + ','
    
    words_temp = words_temp.rstrip(',')
    ban_words = words_temp.split(',')
    return ban_words
    cursor.close ()
    conn.close ()
