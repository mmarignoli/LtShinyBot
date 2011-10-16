from settings import *
import MySQLdb

def hello():
    print "hello function"
    return 'Hello there'
def set_message(message):
	try:
		message_to_update = message.split(' ')[0]
		message = message.split(message_to_update)[1]
		conn = MySQLdb.connect (host = db_server,user = db_username,passwd = db_password,db = db_name)
		cursor = conn.cursor ()
		if cursor.execute ("UPDATE announce SET message = %s WHERE name=%s",(message,message_to_update)):
			cursor.close()
			conn.close()
			return True
		else:
			return False
	except IndexError:
		return False
