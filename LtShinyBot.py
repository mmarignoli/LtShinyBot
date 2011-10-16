from settings import *
import threading
import datetime
import socket
import functions
from functions import *
from db_functions import *
import time
import MySQLdb
import os
import random
import re
from urllib import urlopen
from xml.etree import ElementTree as ET


#global variables
repeat_buffer = {}
keywords = []
whinewords = []
ban_words = []
mods = []
commands = []
logging = 0

#setting up IRC stream
irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
irc.connect ( ( network, port ) )
irc_file = irc.makefile("rb")

#checks if the user is mod
def is_mod(name):
    global mods
    irc.send('WHOIS ' + name + '\r\n')
    data = irc_file.readline()
    parse_data = parsemsg(data)
    to_return = False
    while parse_data[1] != '318':
        data = irc_file.readline()
        parse_data = parsemsg(data)
        if parse_data[1] == '330':
            if parse_data[2][2] in mods:
                to_return = True
        print data
    return to_return

#join channel function takes 1 parameter: name of the channel
def join_channel(chan_name):
    irc.send('JOIN ' + chan_name + '\r\n')

#send message to channel, takes 2 arguments: channel name and message
def send_to_channel(name,message):
    irc.send('PRIVMSG '+ str(name) +' :'+ str(message) +'\r\n')

#kicks user from a channel, takes 3 argument: username, channel name and message
def kick_user(name,chan_name,message):
    irc.send('KICK ' + chan_name + ' ' + name + ' :' + message +'\r\n')

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
        sent_to_channel(chan_name,'Already logging')
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

#Gives voice to user
def give_voice(name,chan_name):
    irc.send('MODE '+ chan_name +' +v '+ name + '\r\n')

#removes voice from user
def remove_voice(name,chan_name):
    irc.send('MODE '+ chan_name +' -v '+ name + '\r\n')
#pulls the video info
def video_info(chan_name,vidid):
    #this allows rickrolls :D
    if vidid == 'oHg5SJYRHA0':
        send_to_channel(chan_name,'YouTube Video: Riddy doing summersault')
    else:
        doc = urlopen("http://gdata.youtube.com/feeds/api/videos?q=" + vidid).read()
        element = ET.XML(doc)
        done = False
        try:
            if done == False:
                for subelement in element:
                    if done == False:
                        for subelement in subelement:
                            if done == False:
                                for values in subelement:
                                    tag = re.sub('{http://search.yahoo.com/mrss/}', '', subelement.tag) + re.sub('{http://search.yahoo.com/mrss/}', '', values.tag)
                                    if tag == 'grouptitle':
                                        video_name =  values.text
                                        send_to_channel(chan_name,'YouTube Video: ' + video_name)
                                        done = True
        except UnicodeEncodeError:
            pass
#check youtube link
def check_youtube(chan_name,words):
    for x in words:
        if x.find('youtube.com') != -1:
            if x.find('youtube.com') != -1:
                if x.find('v=') != -1:
                    x = x[x.find('v=')+2:x.find('v=')+13]
                    print x
                    if len(x) == 11:
                        video_info(chan_name,x)
        elif x.find('youtu.be/') != -1:
            x = x[x.find('youtu.be/')+9:x.find('youtu.be/')+20]
            print x
            if len(x) == 11:
                video_info(chan_name,x)
                
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
                                if mute_user(words[2].rstrip(' ').rstrip('\r\n')):
                                    remove_voice(words[2].rstrip(' ').rstrip('\r\n'),chan_name)
                                else:
                                    irc.send('WHOIS ' + words[2].rstrip(' ').rstrip('\r\n') + '\r\n')
                                    data = irc.recv (4096)
                                    print data
                                    add_user(data.split(' ')[3],data.split(' ')[5])
                                    if mute_user(words[2].rstrip(' ').rstrip('\r\n')):
                                        remove_voice(words[2].rstrip(' ').rstrip('\r\n'),chan_name)
                            except (IndexError, KeyError):
                                send_to_channel(chan_name,'No nickname specified')
                        else:
                            send_to_channel(chan_name,'You are not a mod')
                    elif words[1] == 'clear':
                        if is_mod(name):
                            try:
                                if clear_user(words[2].rstrip(' ').rstrip('\r\n')):
                                    give_voice(words[2].rstrip(' ').rstrip('\r\n'),chan_name)
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
                    elif words[1] == 'set':
                        if is_mod(name):
                            try:
                                if words[2] != '':
                                    if (set_message(message.split('!lsb set ')[1])):
                                        send_to_channel(chan_name,'Done')
                                    else:
                                        pass
                                else:
                                    pass
                            except IndexError:
                                pass
                        else:
                            send_to_channel(chan_name,'No can do')
                    elif words[1] == 'add':
                        try:
                            if words[2] == 'joke':
                                add_joke(re.sub('!lsb add joke ', '', message))
                            elif words[2] == 'command':
                                if words[3] == 'static':
                                    if add_static_command(re.sub('!lsb add command static ', '' , message)):
                                        global commands
                                        commands = update_commands()
                                        send_to_channel(chan_name,'Done')
                                    else:
                                        send_to_channel(chan_name,'Command already exist')
                                elif words[3] == 'dynamic':
                                    pass
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
                            irc.send('QUIT :I will be back, oh yes, you just wait and see\r\n')
                            irc.close()
                            quit()
                        else:
                            send_to_channel(chan_name,'You wish')
                except IndexError:
                    send_to_channel(chan_name,'What?')
            else:
                func = words[0].lstrip('!')
                response = ""
                if func in commands:
                    send_to_channel(chan_name,run_command(func))
        else:
            try:
                words = message.lower().translate(None, '.,;:\'^!?><').split()
            except TypeError:
                pass
            #whine_bot(name,ip,chan_name,words)
            check_youtube(chan_name,message.split())
            banned_words(name,chan_name,words)
    except IndexError:
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

def parsemsg(s):
    """Breaks a message from an IRC server into its prefix, command, and arguments.
    """
    prefix = ''
    trailing = []
    if not s:
        raise IRCBadMessage("Empty line.")
    if s[0] == ':':
        prefix, s = s[1:].split(' ', 1)
    if s.find(' :') != -1:
        s, trailing = s.split(' :', 1)
        args = s.split()
        args.append(trailing)
    else:
        args = s.split()
    command = args.pop(0)
    return prefix, command, args

class ircThread(threading.Thread):
    def run(self):
        global mods,keywords,ban_words,whinewords,commands
        print irc.recv(4096)
        irc.send ( 'NICK ' + botname + '\r\n' )
        irc.send ( 'USER lsb lsb lsb :lsb\r\n' )
        keywords = update_keywords()
        whinewords = update_whinewords()
        ban_words = update_banwords()
        mods = update_mods()
        commands = update_commands()
        while True:
            data = irc_file.readline()
            print data
            parsed_data = parsemsg(data)
            if parsed_data[1] == 'PRIVMSG':
                global logging
                name = parsed_data[0].split('!')[0]
                ip = parsed_data[0].split('@')[1]
                if parsed_data[2][0][0] == '#':
                    if logging == 1:
                        add_to_log(name,parsed_data[2][0],parsed_data[2][1])
                    message_read(name,ip,parsed_data[2][0],parsed_data[2][1].rstrip('\r\n'))
                    repeat_protection(name,parsed_data[2][1],parsed_data[2][0],time.time())
                else:
                    message_read(name,ip,name,parsed_data[2][1].rstrip('\r\n'))
            #PONG reponse to PING
            elif parsed_data[1] == 'PING':
                irc.send('PONG ' + parsed_data[2][0] + '\r\n')
            #when /end of MOTD is recognised the bot will join channels
            elif parsed_data[1] == '376':
                auth_q(q_username,q_password)
                join_channel(channel)
            #when a channel is joined bot can greet here
            elif parsed_data[1] == '366':
                pass
                #send_to_channel(parsed_data[2][1],'BOT IS HERE')
            #gives voice to user that joins
            elif parsed_data[1] == 'JOIN':
                name = parsed_data[0].split('!')[0]
                ip = parsed_data[0].split('@')[1]
                add_user(name,ip)
                if can_voice(name):
                    give_voice(name,parsed_data[2][0].rstrip('\r\n'))
            #checks if a user has been given voice, and if that user is muted it will remove it
            elif parsed_data[1] == 'MODE':
                if parsed_data[2][1] == '+v':
                    if can_voice(parsed_data[2][2]):
                        pass
                    else:
                        remove_voice(parsed_data[2][2],parsed_data[2][0])
            elif parsed_data[1] == 'NICK':
                oriname = parsed_data[0].split('!')[0]
                update_user(oriname,parsed_data[2][0])
i = ircThread()
i.start()
