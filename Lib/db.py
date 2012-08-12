import sqlalchemy
from sqlalchemy import orm
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
Session = sessionmaker()

class BaseService(object):
        engine = create_engine('mysql://root:hello@localhost/test_alchemy')
        Session = sessionmaker(bind = engine)
        session = Session()

class AlchemyExtend():

    def update(self):
        BaseService.session.commit()

    
class db:

    def __init__(self):
    #    engine = create_engine('mysql://root:hello@localhost/test_alchemy')
    #    Session.configure(bind=engine)
        print "in DB"
        print BaseService.engine
        Base.metadata.create_all(BaseService.engine)
        print "Done"
