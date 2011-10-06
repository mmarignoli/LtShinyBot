from settings import *
import threading
import datetime
import socket
import functions
import time
import MySQLdb
import dbm
import os
import random

#global variables
repeat_buffer = {}
keywords = []
whinewords = []
ban_words = []
mods = []
voice_list = dbm.open('voice', 'c')
user_list = dbm.open('users', 'c')
logging = 0

#setting up IRC stream
irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
irc.connect ( ( network, port ) )
#add joke to database
def add_joke(joke):
	conn = MySQLdb.connect (host = db_server,user = db_username,passwd = db_password,db = db_name)
	cursor = conn.cursor ()
	cursor.execute ("INSERT INTO joke(ID, joke)VALUES(NULL, %s)",(joke))
	cursor.close()
	conn.close()
#pulls all the mods authname from the database
def update_mods():
    global mods
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
    cursor.close ()
    conn.close ()

#pulls all the keywords from the database
def update_keywords():
    global keywords
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
    cursor.close ()
    conn.close ()

#pulls all the whinewords from the database
def update_whinewords():
    global whinewords
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
    cursor.close ()
    conn.close ()

#checks if the user is mod
def is_mod(name):
    global mods
    irc.send('WHOIS ' + name + '\r\n')
    data = irc.recv (4096)
    print data
    pos = data.find(' :is authed as')
    pos = pos - 1
    name = ""
    while data[pos] != ' ':
        name = name + str(data[pos])
        pos = pos - 1
    result = name[::-1]
    if result in mods:
        return True
    else:
        return False
    
#updates all the banned words from the database
def update_banwords():
    global ban_words
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
    cursor.close ()
    conn.close ()

#join channel function takes 1 parameter: name of the channel
def join_channel(chan_name):
    irc.send('JOIN ' + chan_name + '\r\n')

#send message to channel, takes 2 arguments: channel name and message
def send_to_channel(name,message):
    irc.send('PRIVMSG '+ str(name) +' :'+ str(message) +'\r\n')
    
#kicks user from a channel, takes 3 argument: username, channel name and message    
def kick_user(name,chan_name,message):
    irc.send('KICK ' + chan_name + ' ' + name + ' :' + message +'\r\n')
    
#mute a user sending a message to Q as well to prevent the player from recieving voice again
def mute_user(name,ip,chan_name):
    global voice_list
    voice_list[ip] = '5'
    irc.send('MODE '+ chan_name +' -v '+ name + '\r\n')

#quakenet Q auth, takes 2 parameters username and password
def auth_q(uname,passwd):
    irc.send('PRIVMSG Q@CServe.quakenet.org :AUTH ' + uname + ' ' + passwd + '\r\n')

#whine bot
def whine_bot(name,ip,chan_name,words):
    global voice_list
    global keywords
    for x in words:
        if x.rstrip('\r\n') in keywords:
            for y in words:
                if y.rstrip('\r\n') in whinewords:
                    if ip in voice_list:
                        voice_list[ip] = str(int(voice_list[ip]) + 1)
                    else:
                        voice_list[ip] = '1'

                    if voice_list[ip] == '1':
                        send_to_channel(chan_name,name + ' is that QQ I hear?\r\n')
                    elif voice_list[ip] == '2':
                        send_to_channel(chan_name,name + ' no balance whine\r\n')
                    elif voice_list[ip] == '3':
                        send_to_channel(chan_name,name + ' gonna mute ya for now\r\n')
                        mute_user(name,ip,chan_name)

#banned words initiate kick if triggered takes 3 parameters, name, channel name, and words
def banned_words(name,chan_name,words):
    for x in words:
        for y in ban_words:
            if x.find(y) != -1:
                kick_user(name,chan_name,'No racism')
#starts logging, takes 2 parameters name of the file and channel
def start_log(filename,chan_name):
    global filehandle
    global logging
    global logged_channel
    if logging == 0:
        logging = 1
        logged_channel = chan_name
        filehandle = open(filename, 'w',0)
        send_to_channel(chan_name,'Started logging')
    else:
        print sent_to_channel(chan_name,'Already logging')
#adds to the log, takes 3 parameters username, channel name, and message
def add_to_log(name,chan_name,message):
    global filehandle
    global logged_channel
    if chan_name == logged_channel:
        filehandle.write('<'+name+'> '+ message + '\n')
#stops the logging takes 1 parameter, channel name
def stop_log(chan_name):
    global filehandle
    global logging
    global logged_channel
    if logged_channel == chan_name:
        logging = 0
        filehandle.close()
        send_to_channel(chan_name,"Stopped Logging")
        
#change bot nick
def change_nick(nick):
	irc.send ( 'NICK ' + nick + '\r\n' )

#random joke
def random_joke(chan_name):
	conn = MySQLdb.connect (host = db_server,user = db_username,passwd = db_password,db = db_name)
	cursor = conn.cursor ()
	cursor.execute ("SELECT joke FROM joke")
	numrows = int(cursor.rowcount)
	jokes = {}
	for i in range(numrows):
		row = cursor.fetchone()
		jokes[i] = row[0]
	ran = random.randint(0, (numrows -1))
	send_to_channel(chan_name, str(jokes[ran]))
	cursor.close()
	conn.close()
#message checker takes 4 arguments: username, ip, channel name and message
def message_read(name,ip,chan_name,message):
	words = message.split()
	try:
		if words[0][0] == '!':
			if words[0] == '!lsb':
				try:
					if words[1] == 'update':
						if words[2] == 'keywords':
							update_keywords()
							send_to_channel(chan_name,'Keywords updated')
						elif words[2] == 'whinewords':
							update_whinewords()
							send_to_channel(chan_name,'Whinewords updated')
						elif words[2] == 'mods':
							update_mods()
							send_to_channel(chan_name,'Mods updated')
						elif words[2] == 'banwords':
							update_banwords()
							send_to_channel(chan_name,'Banwords updated')
					elif words[1] == 'mute':
						if is_mod(name):
							try:
								mute_user(words[2],user_list[words[2]],chan_name)
							except (IndexError, KeyError):
								send_to_channel(chan_name,'No nickname specified')
						else:
							send_to_channel(chan_name,'You are not a mod')
					elif words[1] == 'clear':
						if is_mod(name):
							try:
								clear_user(words[2],user_list[words[2]],chan_name)
							except (IndexError, KeyError):
								send_to_channel(chan_name,'No nickname specified')
						else:
							send_to_channel(chan_name,'You are not a mod')
					elif words[1] == 'time':
						send_to_channel(chan_name,'Coming soon :D')
					elif words[1] == 'log':
						if words[2] == 'start':
							try:
								start_log(words[3],chan_name)
							except IndexError:
								send_to_channel(chan_name,'Specify a filename')
						elif words[2] == 'stop':
							stop_log(chan_name)
					elif words[1] == 'add':
						try:
							if words[2] == 'joke':
								add_joke(message.lstrip('!lsb add joke '))
							else:
								pass
						except IndexError:
							send_to_channel(chan_name,'Add what?')
					elif words[1] == 'joke':
						random_joke(chan_name)
					elif words[1] == 'nick':
						try:
							if is_mod(name):
								change_nick(words[2])
							else:
								send_to_channel(chan_name,'No can do')
						except IndexError:
							send_to_channel(chan_name,'Specify a name')
					elif words[1] == 'quit':
						if is_mod(name):
							irc.close()
							quit()
						else:
							send_to_channel(chan_name,'You wish')
				except IndexError:
					send_to_channel(chan_name,'What?')
			else:
				func = words[0].lstrip('!')
				response = ""
				try:
				   response = getattr(functions, func)()
				except AttributeError:
					pass
				if response == "":
					pass
				else:
					send_to_channel(chan_name,response)
		else:
			words = message.lower().translate(None, '.,;:\'^!?><').split()
			whine_bot(name,ip,chan_name,words)
			banned_words(name,chan_name,words)
	except IndexError:
		pass

#Gives voice to user, also checks if the user has been removed voice
def give_voice(name,ip,chan_name):
    global voice_list
    if ip in voice_list:
        if int(voice_list[ip]) >= 3:
            pass
        else:
            irc.send('MODE '+ chan_name +' +v '+ name + '\r\n')
    else:
        irc.send('MODE '+ chan_name +' +v '+ name + '\r\n')

#clear a user from the voice_list
def clear_user(name,ip,chan_name):
    global voice_list
    if ip in voice_list:
        voice_list[ip] = '0'
        irc.send('MODE '+ chan_name +' +v '+ name + '\r\n')
        send_to_channel(chan_name,'Done')
    else:
        pass

#Checks if a user is spamming the same message takes 3 argument: name, message and channel name
def repeat_protection(name,message,chan_name,timest):
    if name in repeat_buffer:
        if repeat_buffer[name][0] == message:
            num = repeat_buffer[name][2] + 1
            repeat_buffer[name] = [message,repeat_buffer[name][1], num]
            if repeat_buffer[name][1]+30 > timest and repeat_buffer[name][2] > 3:
                kick_user(name,chan_name,'Stop repeating')
                del repeat_buffer[name]
        else:
            temp_buffer = [message, timest, 1]
            repeat_buffer[name] = temp_buffer
    else:
        temp_buffer = [message, timest, 1]
        repeat_buffer[name] = temp_buffer
    
class ircThread(threading.Thread):
    def run(self):
        print irc.recv(4096)
        irc.send ( 'NICK ' + botname + '\r\n' )
        irc.send ( 'USER lsb lsb lsb :lsb\r\n' )
        update_keywords()
        update_whinewords()
        update_banwords()
        update_mods()
        while True:
            data = irc.recv(4096)
            global logging
            print data
            #PONG reponse to PING
            if data.find('PING') != -1:
                irc.send('PONG ' + data.split()[1] + '\r\n')
            #when /end of MOTD is recognised the bot will join channels
            if data.find ( 'End of /MOTD command' ) != -1:
                auth_q(q_username,q_password)
                join_channel(channel)
            if data.find ( 'End of MOTD command' ) != -1:
                #auth_q(q_username,q_password)
                join_channel(channel)
            #when a channel is joined bot can greet here
            if data.find( 'End of /NAMES list') != -1:
                data.lstrip(':')
                lines = data.rstrip('\r\n').split('\r\n')
                chan = lines[len(lines)-1].split()[3]
                send_to_channel(chan,'BOT IS HERE')
            #gives voice to user that joins
            if data.find('JOIN ' + channel) != -1:
                global user_list
                name = data.lstrip(':').split('!')[0]
                ip = data.lstrip(':').split('!')[1].split()[0].split('@')[1]
                give_voice(name,ip,channel)
                user_list[name] = ip
            #checks if a user has been given voice, and if that user is muted it will remove it
            if data.find('MODE ' + channel + ' +v') != -1:
                global user_list
                global voice_list
                name = data.split(channel + ' +v')[1].lstrip(' ').rstrip('\r\n')
                ip = data.lstrip(':').split('!')[1].split()[0].split('@')[1]
                if name in user_list:
                    if str(user_list[name]) in voice_list:
                        if int(voice_list[user_list[name]]) >= 3:
                            irc.send('MODE '+ channel +' -v '+ name + '\r\n')
            if data.find ('PRIVMSG #') != -1:
                name = data.lstrip(':').split('!')[0]
                ip = data.lstrip(':').split('!')[1].split()[0].split('@')[1]
                chan_name = data.lstrip(':').split('PRIVMSG ')[1].split()[0]
                message = data.lstrip(':').split(chan_name + ' :')[1].rstrip('\r\n').lstrip(' ')
                if logging == 1:
                    add_to_log(name,chan_name,message)
                message_read(name,ip,chan_name,message)
                repeat_protection(name,message,chan_name,time.time())
i = ircThread()
i.start()
