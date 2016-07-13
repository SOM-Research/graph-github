# -*- coding: utf-8 -*-
import controller.urlRequest
# from pygithub3 import Github
import simplejson as json
#--------------------
class User:
	def __init__(self, login, p):
		print "[*]User object..."
		self.login = login
		self.p = p
		self.gh = None

		self.logged=True
		if self.login!='':
			url='https://api.github.com/users/'+self.login
			response=controller.urlRequest.send(url,self)
			if response==False:
				self.logged=False
				self.name='Annonimous'
			else:
				if response['name']=='':
					self.name=login
				else:
					self.name=response['name']
		else:
			self.logged=False
			self.name='Annonimous'

		print '\033[92m'+"[Done]"+'\033[0m'

	def __repr__(self):
		return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)
	def __str__(self):
		return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

	# def get_status(self):
	# 	print "[*]Getting user status..."
	# 	if self.logged:
	# 		# Python Github API
	# 		self.gh = Github(login=self.login, password=self.p)
	# 		return True
	# 	else:
	# 		self.gh = Github()
	# 		return False
	# 	print '\033[92m'+"[Done]"+'\033[0m'
#--------------------