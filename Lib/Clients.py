from db import BaseService
from db import *

class client(Base, AlchemyExtend):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    nickname = Column(String(200))
    ip = Column(String(200))
    warn_level = Column(Integer)


    def __init__(self, nickname, ip, warn_level = 0):
        self.nickname = nickname
        self.ip = ip
        self.warn_level = warn_level

    def voice_enabled(self):
        #the max warn level needs to be a variable set on the database
        return self.warn_level > 2

    def warn(self):
        #need to add a check if a user is already not voice enabled, then it would make no sense to increase the
        #warning level
        self.warn_level += 1
        self.update()

    @staticmethod
    def set(nickname, ip):
        #This is just simply crap, it will need to be reworked because it cant handle
        #more then one client from the same ip, but seeing that it's not 100% necessary
        #It will just do for now.
        user = BaseService.session.query(client).filter(client.ip == ip).first()
        if user:
            user.nickname = nickname
        if not user:
            user = BaseService.session.query(client).filter(client.nickname == nickname).first()
        if not user:
            client.create(nickname,ip)
            #this part is again just wrong, would be better to persist the object from the create method
            #but seeing as that should be going into another class it would be better to wait first
            user = BaseService.session.query(client).filter(client.ip == ip).first()
        user.ip = ip
        user.update()
        return user


    #this will need to go into the alchemy_extend class, as it is a commonly used function, but it will need to be
    #made to work with all types of objects
    @staticmethod
    def create(nickname, ip):
        BaseService.session.add(client(nickname, ip))
        BaseService.session.commit()