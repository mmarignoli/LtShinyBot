import socket
import threading
from db import *
import IRCCommands

class Server(Base, threading.Thread):
    __tablename__ = 'servers'
    

    id = Column(Integer, primary_key=True)
    server_name = Column(String(50))
    server_address = Column(String(50))
    server_port = Column(Integer)

    channels = relationship("Channel", backref="Server")
	    
    def __init__(self, server_name, server_address, server_port=6667):
        threading.Thread.__init__(self)
        self.server_name = server_name
        self.server_address = server_address
        self.server_port = server_port

    @orm.reconstructor
    def init_on_load(self):
        threading.Thread.__init__(self)

    def connect(self):
        self.irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
        self.irc.connect ( ( self.server_address, self.server_port ) )
        self.irc_file = self.irc.makefile("rb")
        self.start()

    def run(self):
        self.send ( 'NICK Test2\r\n' )
        self.send ( 'USER lsb lsb lsb :lsb\r\n' )
        while True:
            data = self.irc_file.readline()
            print data
            try:
                parser.parse(self,data)
            except:
                #Gonna need to add a logging feature here
                pass
    
    def send(self, msg):
        self.irc.send(msg)

    @staticmethod
    def create(server_name, server_address, server_port=6667):
        BaseService.session.add(Server(server_name, server_address, server_port))
        BaseService.session.commit()

class Channel(Base, AlchemyExtend):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, ForeignKey('servers.id'))
    channel_name = Column(String(100))

    server = relationship("Server", backref=backref('servers', order_by=id))

class parser:

    @staticmethod
    def parse(server, msg):
        #Breaks a message from an IRC server into its prefix, command, and arguments.
        prefix = ''
        trailing = []
        if not msg:
            raise IRCBadMessage("Empty line.")
        if msg[0] == ':':
            prefix, msg = msg[1:].split(' ', 1)
        if msg.find(' :') != -1:
            msg, trailing = msg.split(' :', 1)
            args = msg.split()
            args.append(trailing)
        else:
            args = msg.split()
        command = args.pop(0)
        try:
            getattr(IRCCommands.protocol, 'call_' + command )(server, prefix, args)
        except Exception, e:
            print e

        print "Prefix start"
        print prefix
        print "Prefix end"
        print "Args start"
        print args
        print "Args end"