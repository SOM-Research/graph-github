# -*- coding: utf-8 -*-
import controller.urlRequest
import simplejson as json
#--------------------
# Repository and user objects
class Repository:
	
	def __init__(self,org,repo):
		print "[*]Repository object..."
		self.json_exists=False # Cemaphore to check if we allready have mined this repository within two days
		self.content={}

		self.file_list={}
		self.contributers_list={}

		self.issue_list={}
		self.user_list={}

		self.org=org # The company name the project belongs to
		temp=repo.split('/',1)
		self.name=temp[0] # The project to analyse
		self.directory=''
		self.file_name=org+'-'+repo+'.json'


		if len(temp)>1:  # If there is a specified directory in the path ex: bootlint/src
			self.directory=temp[1] # Where to make the graph
			self.file_name=org+'-'+repo+'>'+self.directory+'.json'
		print '\033[92m'+"[Done]"+'\033[0m'

	def __repr__(self):
		return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)
	def __str__(self):
		return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

	def get_content(self,user):
		print "[*]Getting project content..."
		url='https://api.github.com/repos/'+self.org+'/'+self.name+'/contents/'+self.directory+'/'
		req = controller.urlRequest.send(url,user)

		if req==False:
			self.exists=False
		else:
			# get the number of elements in the repository and print it
			for file in req:
				self.content[file['name']] = {'name':self.directory+'/'+file['name'],'size':file['size'],'author':'','type':file['type']}
			print '\033[92m'+"[Done]"+'\033[0m'
			self.exists=True
		return self.exists
#--------------------