import webapp2

from config import *

app = webapp2.WSGIApplication([
								('/?', 'views.Home'),
								('/login/?', 'views.Login'),
								('/logout/?', 'views.Logout'),
								('/signup/?', 'views.Signup'),
								('/msg/?', 'views.Mesg'),
								('/frnlist/?', 'views.FrnList')
							], debug=False)