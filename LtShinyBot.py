from Lib import IRCLib
from Lib import db
from Lib import Clients

bla = db.BaseService.session.query(IRCLib.Server)
res = bla.all()
res[0].connect()
db.db()
#bla = IRCLib.connect("local","127.0.0.1")
#bla.create()
#bla.start()