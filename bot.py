import socket
import string
 
keywords = ['protoss', 'terran', 'zerg', 'toss', 'mules', 'marines', 'rines', 'mmm', '4gate', '1-1-1', '111', 'infestors', 'imbafestors']
whinewords = ['op', 'up', 'imba', 'imbalanced', 'bullshit', 'balanced']
mods = ['FLDodo', 'LtShinySidesFL', 'DefacedFL', 'HanaSarangFL', 'mcrwvr']
ban_words = [] 
offenders_list = {}
commands = {}


network = 'irc.quakenet.org'
port = 6667
botname= 'LtShinyBot'
channel = '#pybottest'
adminchannel = '#pybottest'
channel_checker = 'PRIVMSG ' + str(channel)
irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
irc.connect ( ( network, port ) )
print irc.recv ( 4096 )
irc.send ( 'NICK ' + botname + '\r\n' )
irc.send ( 'USER lsb lsb lsb :Python IRC BOT\r\n' )
while True:
   data = irc.recv ( 4096 )
   if data.find ( 'PING' ) != -1:
      irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )
      
   ##############BANNED WORDS##########################################
   if data.find ('PRIVMSG ' + str(channel)) != -1:
   	name = data.split('!')
   	name = name[0].lstrip('[\':')
   	print "in banned words"
   	mess = data.split('PRIVMSG ' + str(channel) + ' :')
   	print mess
   	words = mess[1].split(' ')
   	print words
   	for x in words:
   		if x.rstrip('\r\n') in ban_words:
   			print x
   			irc.send ( 'KICK '+ channel + ' ' + name +' :No racism\r\n' )

   ##############HELLO BOT##########################################
   if data.find ( 'hi ' + botname + '' ) != -1:
      irc.send ( 'PRIVMSG '+ channel +' :Hello\r\n' )

   ##############HELLO BOT##########################################
   if data.find ( 'hello ' + botname + '' ) != -1:
      irc.send ( 'PRIVMSG '+ channel +' :Hello\r\n' )

   ##############JOIN COMMANDS##########################################
   if data.find ( 'End of /MOTD command' ) != -1:
      irc.send ( 'JOIN '+ channel +'\r\n' )
      irc.send ( 'JOIN '+ adminchannel +'\r\n' )

   ##############WHOIS COMMANDS##########################################
   if data.find ('lsb whoami') != -1:
      name = data.split('!')
      name = name[0].lstrip('[\':')
      irc.send ( 'WHOIS ' + name + '\r\n' )
      while data.find ( 'End of /WHOIS list' ) != -1:
          pos = 0
      data = irc.recv ( 4096 )
      pos = data.find(' :is authed as')
      pos = pos - 1
      name = ""
      while data[pos] != ' ':
	  name = name + str(data[pos])
	  pos = pos - 1
      result = name[::-1]
      irc.send ( 'PRIVMSG '+ channel +' :the real auth is ' + result + '\r\n' )

   ##############SLAP BOT##########################################
   if data.find ( 'slaps ' + botname + '' ) != -1:
      irc.send ( 'PRIVMSG '+ channel +' :What\'s up with the violence.\r\n' )
      
   ##############SLAP BOT##########################################
   if data.find ( botname ) != -1:
      if data.find('sucks') != -1:
      	irc.send ( 'PRIVMSG '+ channel +' :No i believe YOU suck.\r\n' )
      if data.find('suck') != -1:
      	irc.send ( 'PRIVMSG '+ channel +' :No i believe YOU suck.\r\n' )
      if data.find('boss') != -1:
      	irc.send ( 'PRIVMSG '+ channel +' :I am!\r\n' )
      if data.find('rocks') != -1:
      	irc.send ( 'PRIVMSG '+ channel +' :Most people tend to agree that I do infact rock!\r\n' )

   ##############JOIN VOICE##########################################
   if data.find ('JOIN ' + channel) != -1:
	name = data.split('!')
	name = name[0].lstrip('[\':')
	if name in offenders_list != -1:
		if offenders_list[name] < 3:
			voicegief = 'MODE '+ channel +' +v '+ name + '\r\n'
			irc.send(voicegief)
	else:
		voicegief = 'MODE '+ channel +' +v '+ name + '\r\n'
		irc.send(voicegief)

   ##############QQ BOT##########################################
   if data.find ('PRIVMSG ' + str(channel)) != -1:
	   for x in keywords:
		if data.find(x) != -1:
			for y in whinewords:
				if data.find(y) != -1:
					name = data.split('!')
					name = str(name[0].lstrip('[\':'))
					if name in offenders_list != -1:
						offenders_list[name] = offenders_list[name] + 1
					else:
						offenders_list[name] = 1

					if offenders_list[name] == 1:
						reply = 'PRIVMSG '+ channel +' :' + name + ' All right let\' try and keep it nice\r\n'
						irc.send (reply)
					elif offenders_list[name] == 2:
						reply = 'PRIVMSG '+ channel +' :' + name + ' seriously no balance whine, you getting muted next\r\n'
						irc.send (reply)
					elif offenders_list[name] == 3:
						reply = 'PRIVMSG '+ channel +' :' + name + ' gonna mute ya for now\r\n'
						irc.send (reply)
						voicerem = 'MODE '+ channel +' -v '+ name + '\r\n'
						irc.send (voicerem)
			break
			
   ##############CLEAR PERSON##########################################
   if data.find ('!lsb clear') != -1:
	command = data.split('!lsb clear ')
	try:
		offender = str(command[1])
		offender = offender.rstrip('\r\n')
	except IndexError:
		reply = 'PRIVMSG '+ channel +' :Please put a space after clear\r\n'
		irc.send (reply)
	name = data.split('!')
	name = name[0].lstrip('[\':')
	irc.send ( 'WHOIS ' + name + '\r\n' )
	while data.find ( 'End of /WHOIS list' ) != -1:
	  pos = 0
	data = irc.recv ( 4096 )
	pos = data.find(' :is authed as')
	pos = pos - 1
	name = ""
	while data[pos] != ' ':
	  name = name + str(data[pos])
	  pos = pos - 1
	result = name[::-1]
	if result in mods:
		if offender in offenders_list:
			offenders_list[offender] = 0
			voicegief = 'MODE '+ channel +' +v '+ offender + '\r\n'
			irc.send(voicegief)
			reply = 'PRIVMSG '+ channel +' :' + offender + ' have been cleared!!\r\n'
			irc.send (reply)
		else:
			reply = 'PRIVMSG '+ channel +' :Can\'t find that user\r\n'
			irc.send (reply)
	else:
		reply = 'PRIVMSG '+ channel +' :' + result + ' you are not a mod\r\n'
		irc.send (reply)
			
   ##############ADD COMMAND##########################################
   if data.find ('PRIVMSG ' + str(adminchannel)) != -1:
   	if data.find('!lsb add') != -1:
   		values = data.split('!')
   		values = values[2]
   		values = values.split(' ')
   		desc = ""
   		pos = 0
   		if values[2] not in commands:
   			for x in values:
   				pos += 1
   				if pos > 3:
   					desc += x
   					desc += ' '
   			commands[values[2]] = desc
   			reply = 'PRIVMSG '+ adminchannel +' :done\r\n'
			irc.send (reply)
   			print commands
   		else:
   			name = data.split('!')
			name = name[0].lstrip('[\':')
   			reply = 'PRIVMSG '+ adminchannel +' :' + name + ' That command already exists\r\n'
			irc.send (reply)
			print commands
	
   ##############EDIT COMMAND##########################################
   if data.find ('PRIVMSG ' + str(adminchannel)) != -1:
   	if data.find('!lsb set') != -1:
   		values = data.split('!')
   		values = values[2]
   		values = values.split(' ')
   		desc = ""
   		pos = 0
   		if values[2] in commands:
   			for x in values:
   				pos += 1
   				if pos > 3:
   					desc += x
   					desc += ' '
   			commands[values[2]] = desc
   			reply = 'PRIVMSG '+ adminchannel +' :done\r\n'
			irc.send (reply)
   			print commands
   		else:
   			reply = 'PRIVMSG '+ adminchannel +' :' + name + values[2] + ' command not found\r\n'
			irc.send (reply)
			
   ##############DELETE COMMAND##########################################
   if data.find ('PRIVMSG ' + str(adminchannel)) != -1:
   	if data.find('!lsb delete') != -1:
   		values = data.split('!')
   		values = values[2]
   		values = values.split(' ')
   		if values[2].rstrip('\r\n') in commands:
   			del commands[values[2].rstrip('\r\n')]
   			reply = 'PRIVMSG '+ adminchannel +' :done\r\n'
			irc.send (reply)
   			print commands
   		else:
   			reply = 'PRIVMSG '+ adminchannel +' :' + name + values[2] + ' command not found\r\n'
			irc.send (reply)
   
   ##############SHOW COMMAND##########################################
   if data.find ('PRIVMSG ' + str(channel)) != -1:
	   if data.find('!') !=1:
	   	for x in commands:
	   		if data.find('!' + x) != -1:
	   			values = data.split('!')
		   		values = values[2]
		   		values = values.split(' ')
		   		evname = values[0]
			  	evname = evname.rstrip('\r\n')
			  	reply = 'PRIVMSG '+ channel +' :' + commands[evname] + '\r\n'
				irc.send (reply)
   		
   print data
