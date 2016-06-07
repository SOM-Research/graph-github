# -*- coding: utf-8 -*-
import getpass, sys
from datetime import datetime, timedelta
import json, urllib2
from pygithub3 import Github
import metric as m 

#----------------------------------------------------------------------
# Function to send and receive from github API
# wrapper function to encode the username & pass
def encodeUserData(user, password):
	return "Basic " + (user + ":" + password).encode("base64").rstrip()
#--------------------
# simple function to make the url request 
# to github and parse the result in Json  
def sendRequest(url,user):

	data=[]
	req = urllib2.Request(url)
	req.add_header('Accept', 'application/json')
	req.add_header("Content-type", "application/x-www-form-urlencoded")
	if user.logged:
		print '(Sending request as '+user.login+')'
		req.add_header('Authorization', encodeUserData(user.login, user.p))
	else:
		print '(Sending request as annonimous)'
	# make the request and print the results
	try:
		res = urllib2.urlopen(req)
		return json.loads(res.read())
	except urllib2.HTTPError, e:
		print '\033[91m'+"\n----Error----\n"+e.fp.read()+"\n-------------\n"+'\033[0m'
		print "Request failed !"
		return False
#----------------------------------------------------------------------


#----------------------------------------------------------------------
# To get all the contributors of a file and their number of commits 
def commitersOfFile(user,repo,file):
	#contributorsList is now repo.contributers_list
	UnknownUser_id=1 #Will be used to identify a Unknown user
	# This URL shows what iformation can be get about commits (email addresses, etc...)
	# curl -i -u AlexFabre https://api.github.com/repos/twbs/grunt-bootlint/commits/ae31bb28f74b306437ca6cb34662935c3910434e

	fileContributors={} # The Commiters of the file
	print '    '+file, # the file we are going to list the commits
	# Let's get the entire commit's hirstory of the file
	commitList=user.gh.repos.commits.list(user=repo.org, repo=repo.name, path=file).all()
	num_commit=len(commitList)
	print str(num_commit)+' commits' # The length of the list id: number of commits

	author_date = datetime.now()
	author_name=''

	for commit in commitList:
		# # Let's get all the infos aboout a commit
		#    url='https://api.github.com/repos/'+org+'/'+repo+'/commits/'+str(commit)[12:-2]
		#    data = sendRequest(url)


		# We get all infos about the committer who approved the commit
		committer_name=commit.commit.committer.name # His real name, not a login
		committer_email=commit.commit.committer.email
		committer_message=commit.commit.message
		commit_date=commit.commit.committer.date # Date of this commit
		if commit_date<author_date: # Will help to know who is the author of the file with the original commit
			author_date=commit_date
			author_name=committer_name
		commit_sha=commit.sha # The id of the commit

			# We get everything about the author of the modifications

		try:
			contributor_login=commit.author.login # login according to Github
			contributor_id=commit.author.id # Github unique id
			contributor_url=commit.author.url # Link to the github profile
		except:
			# If the author is not known, it happens in project bootstrap-blog i think, then it creats an Unknown author with a negative id
			contributor_login='UnknownAuthor'+str(UnknownUser_id)
			contributor_id=0-UnknownUser_id #Declared at the begining
			contributor_url='No url'

		if repo.contributers_list.has_key(contributor_login.encode('ascii', 'replace')): # The contributors has allready touched this file
			repo.contributers_list[contributor_login]['commits']+=1
			repo.contributers_list[contributor_login]['name']=committer_name.encode('ascii', 'replace')
			repo.contributers_list[contributor_login]['committers'][committer_name.encode('ascii', 'replace')]={'name': committer_name.encode('ascii', 'replace'), 'email':committer_email.encode('ascii', 'replace'), 'message':committer_message.encode('ascii', 'replace'), 'date':commit_date, 'sha': commit_sha}
		else:
			repo.contributers_list[contributor_login]={'num':0 ,'login': contributor_login.encode('ascii', 'replace'), 'id': contributor_id, 'url': contributor_url, 'commits': 1, 'name':committer_name.encode('ascii', 'replace'), 'committers':{}}
			repo.contributers_list[contributor_login.encode('ascii', 'replace')]['committers'][committer_name.encode('ascii', 'replace')]={'name': committer_name.encode('ascii', 'replace'), 'email':committer_email.encode('ascii', 'replace'), 'message':committer_message.encode('ascii', 'replace'), 'date':commit_date, 'sha': commit_sha}

		if fileContributors.has_key(contributor_login):
			fileContributors[contributor_login]+=1
		else:
			fileContributors[contributor_login]=1

	return num_commit, author_name, fileContributors
#--------------------
# Making the json file with files, and contribution
def contribution(repo):

	num=0
	# Here we have to make a unique number for each participant
	today=datetime.now()
	
	jsonfile = open(repo.fileName, "wb+")
	print "*new file created"

	print "[writing json contribution]",
	text=''
	text=text+ '{"date":"'+today.strftime("%Y-%m-%d")+'","organisation":"'+repo.org+'","repository":"'+repo.name+'","directory":"'+repo.directory+'","files":[';
	cemaphore=True
	for file in repo.file_list:
		if cemaphore:
			text=text+'{"name":"'+repo.file_list[file]['name']+'","type":"'+repo.file_list[file]['type']+'","size":"'+str(repo.file_list[file]['size'])+'","commits":"'+str(repo.file_list[file]['commits'])+'","author":"'+str(repo.file_list[file]['author'])+'","commiters":['
			cemaphore=False
		else:
			text=text+',{"name":"'+repo.file_list[file]['name']+'","type":"'+repo.file_list[file]['type']+'","size":"'+str(repo.file_list[file]['size'])+'","commits":"'+str(repo.file_list[file]['commits'])+'","author":"'+str(repo.file_list[file]['author'])+'","commiters":['

		cemaphore=True
		for contributor in repo.file_list[file]['committers']:
			if cemaphore:
				text=text+'{"login":"'+str(repo.contributers_list[contributor]['login'])+'","num":"'+str(repo.contributers_list[contributor]['num'])+'","url":"'+str(repo.contributers_list[contributor]['url'])+'","id":'+str(repo.contributers_list[contributor]['id'])+',"total-commits":'+str(repo.contributers_list[contributor]['commits'])+',"file-commits":'+str(repo.file_list[file]['committers'][contributor])+',"commiters-info":['
				cemaphore=False
			else:
				text=text+',{"login":"'+str(repo.contributers_list[contributor]['login'])+'","num":"'+str(repo.contributers_list[contributor]['num'])+'","url":"'+str(repo.contributers_list[contributor]['url'])+'","id":'+str(repo.contributers_list[contributor]['id'])+',"total-commits":'+str(repo.contributers_list[contributor]['commits'])+',"file-commits":'+str(repo.file_list[file]['committers'][contributor])+',"commiter-info":['
			num+=1

			cemaphore=True
			for committer in repo.contributers_list[contributor]['committers']:
				if cemaphore:
					text=text+'{"name":"'+str(repo.contributers_list[contributor]['committers'][committer]['name'])+'","email":"'+str(repo.contributers_list[contributor]['committers'][committer]['email'])+'","sha":"'+str(repo.contributers_list[contributor]['committers'][committer]['sha'])+'","date":"'+str(repo.contributers_list[contributor]['committers'][committer]['date'])+'"}'
					cemaphore=False
					
				else:
					text=text+',{"name":"'+str(repo.contributers_list[contributor]['committers'][committer]['name'])+'","email":"'+str(repo.contributers_list[contributor]['committers'][committer]['email'])+'","sha":"'+str(repo.contributers_list[contributor]['committers'][committer]['sha'])+'","date":"'+str(repo.contributers_list[contributor]['committers'][committer]['date'])+'"}'
			text=text+']}'
		text=text+']}'

	jsonfile.write(text)
	jsonfile.close()

	print '\033[92m'+" ok"+'\033[0m'
	return m.contribution(text+']}')
#--------------------
# Completting json file with issues and commenters
def comments(repo):
	#--------------------
	# Graph of the comments 

	jsonfile = open(repo.fileName,'a')

	print "[writing json issues]",
	jsonfile.write("],")
	text='"issues":['
	cemaphore=True
	for issue in repo.issue_list:
		if cemaphore:
			text=text+'{"number":'+str(repo.issue_list[issue]['number'])+',"state":"'+repo.issue_list[issue]['state']+'","author":"'+str(repo.issue_list[issue]['author'])+'","comments":'+str(repo.issue_list[issue]['comments'])+',"commenters":['
			cemaphore=False
		else:
			text=text+',{"number":'+str(repo.issue_list[issue]['number'])+',"state":"'+repo.issue_list[issue]['state']+'","author":"'+str(repo.issue_list[issue]['author'])+'","comments":'+str(repo.issue_list[issue]['comments'])+',"commenters":['

		cemaphore=True
		for commenter in repo.issue_list[issue]['commenters']:
			if cemaphore:
				text=text+'{"login":"'+str(repo.user_list[commenter]['login'])+'","id":'+str(repo.user_list[commenter]['id'])+',"comments":'+str(repo.issue_list[issue]['commenters'][commenter])+',"total-comments":'+str(repo.user_list[commenter]['comments'])+'}'
				cemaphore=False
			else:
				text=text+',{"login":"'+str(repo.user_list[commenter]['login'])+'","id":'+str(repo.user_list[commenter]['id'])+',"comments":'+str(repo.issue_list[issue]['commenters'][commenter])+',"total-comments":'+str(repo.user_list[commenter]['comments'])+'}'
		text=text+']}'

	text=text+']}'
	
	print '\033[92m'+" ok"+'\033[0m'

	jsonfile.write(text)
	jsonfile.close()

	return m.comments('{"organisation":"'+repo.org+'","repository":"'+repo.name+'","directory":"'+repo.directory+'",'+text)
#----------------------------------------------------------------------


#--------------------
# Repository and user objects
class Repository:
	
	def __init__(self,org,repo):
		print "[*]Creating Repository object..."
		self.json_exists=False # Cemaphore to check if we allready have mined this repository within two days
		self.content={}
		# for contribution:
		self.contributers_list={}
		self.file_list={}
		# for issues:
		self.issue_list={}
		self.user_list={}

		self.org=org # The company name the project belongs to
		temp=repo.split('/',1)
		self.name=temp[0] # The project to analyse
		self.directory=''
		self.fileName=org+'-'+repo+'.json'


		if len(temp)>1:  # If there is a specified directory in the path ex: bootlint/src
			self.directory=temp[1] # Where to make the graph
			self.fileName=org+'-'+repo+'>'+directory+'.json'
		print '\033[92m'+"[Done]"+'\033[0m'

	def getContent(self,user):
		print "[*]Getting project content..."
		url='https://api.github.com/repos/'+self.org+'/'+self.name+'/contents/'+self.directory+'/'
		req = sendRequest(url,user)

		if req==False:
			return False
		else:
			# get the number of elements in the repository and print it
			for file in req:
				self.content[file['name']] = {'name':self.directory+'/'+file['name'],'size':file['size'],'author':'','type':file['type']}
			print '\033[92m'+"[Done]"+'\033[0m'
			return True
#--------------------
class User:
	def __init__(self, login, p):
		print "[*]Creating User object..."
		self.login = login
		self.p = p

		self.logged=True
		if self.login!='':
			url='https://api.github.com/users/'+self.login
			response=sendRequest(url,self)
		if response==False:
			self.logged=False
			self.name='Annonimous'
			self.idnumber=0
		else:
			if response['name']=='':
				self.name=login
			else:
				self.name=response['name']
			self.idnumber=response['id']
		print '\033[92m'+"[Done]"+'\033[0m'

	def getStatus(self):
		print "[*]Getting user status..."
		if self.logged:
			# Python Github API
			self.gh = Github(login=self.login, password=self.p)
			message='Logged as '+self.name
		else:
			self.gh = Github()
			message='Login failed ! Annonimous request...'
		print '\033[92m'+"[Done]"+'\033[0m'
		return self.logged, message
#--------------------


#----------------------------------------------------------------------
# The three functions that are called by the server (server.py)
# Create user and repo objects
def prepare(login,p,org,repo_name):
	print "----Preparing datas----"

	user = User(login,p)  # Create object user
	user_logged, message = user.getStatus()# Check wether user is logged or Annonimous

	repo = Repository(org,repo_name) # Create object Repository

	yesterday=datetime.now()-timedelta(days=2)
	try:
		jsonfile = open(repo.fileName)
		temp=json.loads(jsonfile.read())
		print "[*]json file exists on server",
		file_date=datetime.strptime(temp['date'], "%Y-%m-%d")
		if file_date>=yesterday and temp.has_key('files') and temp.has_key('issues'):
			print "and the file is recent"
			repo.json_exists=True
			jsonfile.close()
		else:
			print 'but file is too old'
	except Exception, e:
		print e

	repo_exists=True
	if repo.getContent(user)==False:
		error="Error: Unable to find repository ! "
		print error
		message=message+' '+error
		repo_exists=False

	return {'user':user,'repo':repo,'message':message,'login_succeded':user.logged,'repo_exists':repo_exists,'jsonfile_exists':repo.json_exists,'jsonfile_name':repo.fileName}

# Use Github API to get all the commits
def getContribution(user,repo):
	print "----Mining Repository (contribution)----"
	print "[*]Getting the commiters..."
	for file in repo.content:
		repo.file_list[repo.content[file]['name']]={'name':repo.content[file]['name'],'type':repo.content[file]['type'],'size':repo.content[file]['size'],'num':0}
		repo.file_list[repo.content[file]['name']]['commits'], repo.file_list[repo.content[file]['name']]['author'], repo.file_list[repo.content[file]['name']]['committers']=(commitersOfFile(user,repo,repo.content[file]['name']))
	print '\033[92m'+"[Done]"+'\033[95m', str(len(repo.contributers_list))+' contributors'+'\033[0m'

	return contribution(repo)
# Use Github API to get all the issues
def getComments(user,repo):
	print "----Mining Repository (comments)----"
	print "[*]Getting project issues..."

	all_issues = user.gh.issues.list_by_repo(user=repo.org, repo=repo.name,state='open').all()
	for resource in all_issues:
		repo.issue_list[resource.number]={'number':resource.number,'author':resource.user.login,'state':resource.state, 'commenters':{resource.user.login:1}, 'comments':0, 'num':0}
		print '    ',resource.number

		if repo.user_list.has_key(resource.user.login):
			repo.user_list[resource.user.login]['comments']+=1
		else:
			repo.user_list[resource.user.login]={'comments':1,'login':resource.user.login, 'id':resource.user.id, 'num':0}
		# print resource.user.login
		data=user.gh.issues.comments.list(number=resource.number, user=repo.org, repo=repo.name).all()
		for comment in data:
			repo.issue_list[resource.number]['comments']+=1
			if repo.issue_list[resource.number]['commenters'].has_key(comment.user.login):
				repo.issue_list[resource.number]['commenters'][comment.user.login]+=1
			else:
				repo.issue_list[resource.number]['commenters'][comment.user.login]=1

			if repo.user_list.has_key(comment.user.login):
				repo.user_list[comment.user.login]['comments']+=1
			else:
				repo.user_list[comment.user.login]={'comments':1,'login':comment.user.login, 'id':comment.user.id, 'num':0}


	print '\033[92m'+"[Done]"+'\033[0m'

	return comments(repo)
#---------------------------------------------------------------------- 


#----------------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv)!=4:
		print '\033[91m'+"-------------\nError: expected 3 argument, "+str(len(sys.argv)-1)+" given\nusage:\n      python "+sys.argv[0]+"  <login(you)>  <user>  <repositoryOfUser/directory>\n-------------"+'\033[0m'
		quit()

	p=getpass.getpass()
	rep=prepare(sys.argv[1],p,sys.argv[2],sys.argv[3])
	getContribution(rep['user'],rep['repo'])
	getComments(rep['user'],rep['repo'])

