from settings import *
import threading
import datetime
import socket
import functions

#setting up IRC stream
irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
irc.connect ( ( network, port ) )

#join channel function takes 1 parameter: name of the channel
def join_channel(chan_name):
    irc.send('JOIN ' + chan_name + '\r\n')

#send message to channel, takes 2 arguments: channel name and message
def send_to_channel(name,message):
    irc.send('PRIVMSG '+ str(name) +' :'+ str(message) +'\r\n')

#message checker takes 4 arguments: username, ip, channel name and message
def message_read(name,ip,chan_name,message):
    print "message_read function"
    words = message.split()
    if words[0][0] == '!':
        if words[0] == '!lsb':
            print "triggered lsb"
        else:
            print "cought ! char"
            func = words[0].lstrip('!')
            response = "Unknown command"
            try:
               response = getattr(functions, func)()
            except AttributeError:
                pass
            send_to_channel(chan_name,response)
    message_low_nopunc = message.lower().translate(None, '.,;:\'^!?><')
    words = message_low_nopunc.split()
    print words
        
class ircThread(threading.Thread):
    def run(self):
        print irc.recv(4096)
        irc.send ( 'NICK ' + botname + '\r\n' )
        irc.send ( 'USER lsb lsb lsb :LtShinyBot IRC BOT\r\n' )
        while True:
            data = irc.recv(4096)
            #PONG reponse to PING
            if data.find('PING') != -1:
                irc.send('PONG ' + data.split()[1] + '\r\n')
            #when /end of MOTD is recognised the bot will join channels
            if data.find ( 'End of /MOTD command' ) != -1:
                join_channel(channel)
            #when a channel is joined bot can greet here
            if data.find( 'End of /NAMES list') != -1:
                #data.lstrip(':')
                lines = data.rstrip('\r\n').split('\r\n')
                chan = lines[len(lines)-1].split()[3]
                send_to_channel(chan,'BOT IS HERE')  
            if data.find ('bot quit') != -1:
                irc.close()
            if data.find ('PRIVMSG #') != -1:
                name = data.lstrip(':').split('!~')[0]
                ip = data.lstrip(':').split('!~')[1].split()[0]
                chan_name = data.lstrip(':').split('!~')[1].split(':')[0].split()[2]
                message = data.lstrip(':').split(chan_name + ' :')[1].rstrip('\r\n').lstrip(' ')
                message_read(name,ip,chan_name,message)
            print data
i = ircThread()
i.start()