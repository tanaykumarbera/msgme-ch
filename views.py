import webapp2
import json

from utils import *

from models import User, Msg, Track

class BaseHandler(webapp2.RequestHandler):
	"""
	Base class for view functions, which provides basic rendering 
	funtionalities
	"""

	def render(self, template, **kw):
		"""
		Render a template with the given keyword arguments
		"""

		self.response.out.write(render_str(template, **kw))

	def set_secure_cookie(self, name, val):
		"""
		Set an encrypted cookie on client's machine
		"""

		cookie_val = make_secure_val(val)
		self.response.headers.add_header(
			'Set-Cookie',
			'%s=%s; Path=/' % (name, cookie_val)
			)

	def read_secure_cookie(self, name):
		"""
		Read a cookie and check it's integrity
		"""

		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)

	def initialize(self, *a, **kw):
		"""
		Override the constuctor for adding user information
		when a request comes
		"""

		webapp2.RequestHandler.initialize(self, *a, **kw)
		user_id = self.read_secure_cookie('user')
		self.user = user_id and User.get_by_id(int(user_id))

class Home(BaseHandler):
	"""
	Handle the homepage
	"""

	def get(self):
		"""
		For a GET request, return the homepage
		"""
		
		self.render("home.html", user=self.user)
		
class FrnList(BaseHandler):
	"""
	Handle the request for loading frn list
	"""

	def get(self):
		if self.user:
			self.redirect('/')
		else:
			self.redirect('/login')
	
	def post(self):
		"""responsible for the name lists in users friend list"""
		usrlist= User.listUsers()
		frn= []
		for usr in usrlist:
			if(usr.key.id()!= self.user.key.id()):
				if(usr.key.id() < self.user.key.id()):
					trid = Track.track_id(usr.key.id(), self.user.key.id())
				else:
					trid = Track.track_id(self.user.key.id(), usr.key.id())
				
				frn.append({'name': usr.username, 'sex': usr.sex, 'uid': usr.key.id(), 'msg': Track.checkNew(trid,self.user.key.id())})
		
		self.response.out.write(json.dumps(frn))
		
	"""
	Handle permalink for the posts
	"""

	def get(self, post_id):
		"""
		For a GET request with a valid post_id, return the post
		Else, return a 404 error
		"""

		post = Post.get_by_id(int(post_id))
		if post:
			self.render("home.html", user=self.user, posts=[post], permalink=True)
		else:
			self.abort(404)

class Login(BaseHandler):
	"""
	Handle login to the blog
	"""

	def get(self):
		"""
		For a GET request, render the login page
		"""

		user = self.user

		if user:
			self.redirect('/')

		self.render('login.html', user=user)

	def post(self):
		"""
		For a POST request, perform the login. If successful, redirect
		to homepage
		"""

		username = self.request.get('username')
		password = self.request.get('password')

		try:
			user_id = User.authenticate(username, password)
			self.set_secure_cookie('user', str(user_id))
			self.redirect('/')
		
		except Exception, e:
			self.render("login.html", user=self.user, error = e)

class Logout(BaseHandler):
	"""
	Log out a user
	"""

	def get(self):
		"""
		Log out the user and redirect her to homepage
		"""
		
		self.set_secure_cookie('user', '')
		self.redirect('/')

class Signup(BaseHandler):
	"""
	Signup a new user
	"""

	def get(self):
		"""
		Render the signup page
		"""

		user = self.user

		if user:
			self.redirect('/')

		self.render('signup.html', user=user)

	def post(self):
		"""
		Create a new user, and redirect to homepage
		"""

		username = self.request.get('username')
		password = self.request.get('password')
		sex = self.request.get('sex')
		try:
			user = User.create_user(username, password, int(sex))
			self.render('login.html', success="Great! You are registered! Please log in.", user=user)

		except Exception, e:
			self.render('signup.html', error=e, user=self.user)

			
class Mesg(BaseHandler):
	"""Handles the request sent to /msg"""
	
	def get(self):
		uid = self.request.get('uid')
		action = self.request.get('action')
		
		if(action=="load"):
			msglist = Msg.get_last_msg(self.user.key.id(),uid)
			if msglist:
				msglist.reverse()
				msgs= []
				for msg in msglist:
					msgs.append({'txt': msg.msgcontent, 'd': msg.direction})
				
				self.response.out.write(json.dumps(msgs))
		
			else:
				self.response.out.write("none")
		else:
			nmsg = self.request.get('nmsg')
			bool= Msg.send_msg(self.user.key.id(), uid, nmsg)
			if bool:
				self.response.out.write("1")
			else:
				self.response.out.write("error")