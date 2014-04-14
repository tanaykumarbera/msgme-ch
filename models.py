from google.appengine.ext import ndb

from utils import *

class User(ndb.Model):
	"""
	A registered user
	"""

	username = ndb.StringProperty(required=True)
	password = ndb.StringProperty(required=True)
	sex = ndb.IntegerProperty(required=True)
	joined = ndb.DateTimeProperty(auto_now_add=True)

	@classmethod
	def create_user(cls, username, password, sex):
		"""
		Create a new user with the provided credentials,
		and throw an exception if something's wrong
		"""

		if not is_username_valid(username):
			raise ValidationError("That's not a valid username.")

		user = cls.query(cls.username==username).fetch()
		if user:
			raise UserError("User already exists!")

		if not is_password_valid(password):
			raise ValidationError("That's not a valid password.")
	
		new_user = cls(username=username, password=encrypt(password), sex=sex).put()
		
		return new_user.id()

	@classmethod
	def authenticate(cls, username, password):
		"""
		Check if the provided username and password are valid
		"""

		try:
			user = cls.query(cls.username==username).fetch()[0]

		except:
			raise UserError("User does not exist!")

		if user.username == username and user.password == encrypt(password):
			return str(user.key.id())
		else:
			raise AuthenticationError("Invalid username/password!")
			
	@classmethod
	def listUsers(cls):
		""" get the users list """
		usrs = cls.query().order(-cls.joined).fetch()
		return list(usrs)
		
class Track(ndb.Model):
	"""
		Keeping track of conversation list and their users
	"""
	user1 = ndb.IntegerProperty(required=True)
	user2 = ndb.IntegerProperty(required=True)
	
	lastMsg = ndb.IntegerProperty()
	lastU1 = ndb.IntegerProperty()
	lastU2 = ndb.IntegerProperty()
	
	@classmethod
	def track_id(cls, u1, u2):
		
		try:
			trid = cls.query(cls.user1==u1, cls.user2==u2).fetch()[0]
		except:
			trid = False
			
		if trid :
			return trid.key.id()
		else:
			new_t = cls(user1=u1, user2=u2, lastMsg=None, lastU1= None, lastU2= None).put()
			return new_t.id()
			
	@classmethod
	def checkNew(cls, tid, usr):
		trObj = Track.get_by_id(tid)
		if(int(usr)==trObj.user1 and trObj.lastMsg==trObj.lastU1):
			return  False
		if(int(usr)==trObj.user2 and trObj.lastMsg==trObj.lastU2):
			return  False

		return True
		
class Msg(ndb.Model):
	"""
		Conversation in between user 1 and user 2
	"""
	
	user1 = ndb.IntegerProperty(required=True)
	user2 = ndb.IntegerProperty(required=True)
	msgcontent = ndb.StringProperty(required=True)
	direction= ndb.IntegerProperty(required=True)
	tid= ndb.IntegerProperty(required=True)
	moment= ndb.DateTimeProperty(auto_now_add=True)
	
	@classmethod
	def get_last_msg(cls, u1, u2):
	
		usr1 = int(u1)
		usr2 = int(u2)
		
		if usr1 > usr2:
			usr1 , usr2 = usr2 , usr1
		
		trid= Track.track_id(usr1, usr2)
		
		last_msgs = cls.query(cls.tid == trid).order(-cls.moment).fetch(10)
		
		
		if last_msgs:
			last_msgs = list(last_msgs)
			
			trObj = Track.get_by_id(trid)
			
			if(trObj.user1 == int(u1)):
				trObj.lastU1 = last_msgs[0].key.id()
			if(trObj.user2 == int(u1)):
				trObj.lastU2 = last_msgs[0].key.id()
			
			trObj.put()
			
			return last_msgs
		else:
			return False
	
	
	@classmethod
	def send_msg(cls, u1, u2, txt):
		
		usr1 = int(u1)
		usr2 = int(u2)
		dirc = 0
		
		if usr1 > usr2:
			usr1 , usr2 = usr2 , usr1
			dirc = 1
		
		trid= Track.track_id(usr1, usr2)
		
		convo= cls(user1= usr1, user2= usr2, msgcontent= str(txt), direction=dirc, tid=trid).put()
		
		
		if convo:
			
			trObj = Track.get_by_id(trid)
			
			trObj.lastMsg = convo.id()
			if(trObj.user1 == int(u1)):
				trObj.lastU1 = convo.id()
			if(trObj.user2 == int(u1)):
				trObj.lastU2 = convo.id()
			
			trObj.put()
			
			return True
		else:
			return False
