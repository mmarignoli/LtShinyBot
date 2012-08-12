from IRCLib import *
from db import *
from Clients import *

class protocol:

    @staticmethod
    def call_PING(server, prefix, args):
        server.send('PONG ' + args)

    @staticmethod
    def call_JOIN(server, prefix, args):
        client.set(prefix.split('!~')[0], prefix.split('@')[1])

    @staticmethod
    def call_376(server, prefix, args):
        for channel in server.channels:
            server.send('JOIN '+channel.channel_name+'\r\n')

    @staticmethod
    def call_433(server, prefix, args):
        server.send('NICK Test_\r\n')