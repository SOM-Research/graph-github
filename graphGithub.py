# -*- coding: utf-8 -*-
import getpass, sys
from datetime import datetime
import json, urllib2
from pygithub3 import Github
import module_3Dgraph as mod
import metric as m 

#----------------------------------------------------------------------
# Function to send and receive from github API
# simple wrapper function to encode the username & pass
def encodeUserData(user, password):
	return "Basic " + (user + ":" + password).encode("base64").rstrip()
#--------------------
# simple function to make the url request 
# to github and parse the result in Json  
def sendRequest(url):
	global u
	global logged

	data=[]
	req = urllib2.Request(url)
	req.add_header('Accept', 'application/json')
	req.add_header("Content-type", "application/x-www-form-urlencoded")
	if logged:
		print 'Sending request as '+u 
		req.add_header('Authorization', encodeUserData(u, p))
	else:
		print 'Sending request as annonimous'
	# make the request and print the results
	try:
		res = urllib2.urlopen(req)
		return json.loads(res.read())
	except urllib2.HTTPError, e:
		print '\033[91m'+"\n----Error----\n"+e.fp.read()+"\n-------------\n"+'\033[0m'
		print "Request failed !"
		return False
	# print res.read()
	# parse the result in json format
#----------------------------------------------------------------------


#----------------------------------------------------------------------
# To get the repository content 
def getContent(directory):
	print '\033[4m'+"----Collecting contribution data: /"+org+'/'+repo+"/"+directory+" ----"+'\033[0m'
	print "[*]Getting project content..."
	url='https://api.github.com/repos/'+org+'/'+repo+'/contents/'+directory+'/'
	data = sendRequest(url)

	if data==False:
		return False
	else:
		content={}
		# get the number of elements in the repository and print it
		for file in data:
			content[file['name']] = {'name':directory+'/'+file['name'],'size':file['size'],'author':'','type':file['type']}
		print '\033[92m'+"[Done]"+'\033[0m'
		return content
#--------------------
# To get all the contributors of a   
# file and their number of commits   
#--------------------
def commitersOfFile(contributorsList,repo,file):

	UnknownUser_id=1 #Will be used to identify a Unknown user

	# This URL shows what iformation can be get about commits (email addresses, etc...)
	# curl -i -u AlexFabre https://api.github.com/repos/twbs/grunt-bootlint/commits/ae31bb28f74b306437ca6cb34662935c3910434e

	fileContributors={} # The Commiters of the file
	print '    '+file, # the file we are going to list the commits
	# Let's get the entire commit's hirstory of the file
	commitList=gh.repos.commits.list(user=org, repo=repo, path=file).all()
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

		if contributorsList.has_key(contributor_login.encode('ascii', 'replace')): # The contributors has allready touched this file
			contributorsList[contributor_login]['commits']+=1
			contributorsList[contributor_login]['name']=committer_name.encode('ascii', 'replace')
			contributorsList[contributor_login]['committers'][committer_name.encode('ascii', 'replace')]={'name': committer_name.encode('ascii', 'replace'), 'email':committer_email.encode('ascii', 'replace'), 'message':committer_message.encode('ascii', 'replace'), 'date':commit_date, 'sha': commit_sha}
		else:
			contributorsList[contributor_login]={'num':0 ,'login': contributor_login.encode('ascii', 'replace'), 'id': contributor_id, 'url': contributor_url, 'commits': 1, 'name':committer_name.encode('ascii', 'replace'), 'committers':{}}
			contributorsList[contributor_login.encode('ascii', 'replace')]['committers'][committer_name.encode('ascii', 'replace')]={'name': committer_name.encode('ascii', 'replace'), 'email':committer_email.encode('ascii', 'replace'), 'message':committer_message.encode('ascii', 'replace'), 'date':commit_date, 'sha': commit_sha}

		if fileContributors.has_key(contributor_login):
			fileContributors[contributor_login]+=1
		else:
			fileContributors[contributor_login]=1

	return num_commit, author_name, contributorsList, fileContributors
#--------------------
# To get all the contributors of all 
# files and their number of commits  
def commitersOfDirectory(contributorsList,repo,content):
	print "[*]Getting the commiters..."
	fileList={}
	for file in content:
		fileList[content[file]['name']]={'name':content[file]['name'],'type':content[file]['type'],'size':content[file]['size'],'num':0}
		fileList[content[file]['name']]['commits'], fileList[content[file]['name']]['author'], contributorsList, fileList[content[file]['name']]['committers']=(commitersOfFile(contributorsList,repo,content[file]['name']))
	print '\033[92m'+"[Done]"+'\033[95m', str(len(contributorsList))+' contributors'+'\033[0m'
	return fileList, contributorsList
#--------------------
# Making the json file of graph 1 
def makeContribution(file_list,contributers_list):

	max_file_commit=1
	max_user_commit=1
	# Giving a single number for the graph drawing to each node according to python's order of dictionary
	node_number=0

	print '\033[4m'+"----Making contribution json file: "+fileName+"----"+'\033[0m'

	print "[files]",
	json=''
	json=json+ '{"type":"contribution","organisation":"'+org+'","repository":"'+repo+'","directory":"'+directory+'","nodes":[';
	for file in file_list:
		file_list[file]['num']=node_number
		if file_list[file]['commits']>max_file_commit:
			max_file_commit=file_list[file]['commits']
		node_number+=1
		json=json+'{"name":"'+file_list[file]['name']+'","type":"'+file_list[file]['type']+'","num":"'+str(file_list[file]['num'])+'","size":"'+str(file_list[file]['size'])+'","commits":"'+str(file_list[file]['commits'])+'","group":1},'
	print '\033[92m'+" ok"+'\033[0m'


	print "[contributors]",
	cemaphore=True
	for contributor in contributers_list:
		contributers_list[contributor]['num']=node_number
		if contributers_list[contributor]['commits']>max_user_commit:
			max_user_commit=contributers_list[contributor]['commits']
		node_number+=1
		if cemaphore:
			json=json+'{"login":"'+contributers_list[contributor]['login']+'","num":"'+str(contributers_list[contributor]['num'])+'","commits":"'+str(contributers_list[contributor]['commits'])+'","name":"'+contributers_list[contributor]['name']+'","type":"user","id":"'+str(contributers_list[contributor]['id'])+'","group":'+str((contributers_list[contributor]['commits']/20)+4)+'}'
			cemaphore=False
		else:
			json=json+',{"login":"'+contributers_list[contributor]['login']+'","num":"'+str(contributers_list[contributor]['num'])+'","commits":"'+str(contributers_list[contributor]['commits'])+'","name":"'+contributers_list[contributor]['name']+'","type":"user","id":"'+str(contributers_list[contributor]['id'])+'","group":'+str((contributers_list[contributor]['commits']/20)+4)+'}'
				  
	print '\033[92m'+" ok"+'\033[0m'


	print "[links]",
	json=json+'],"links":['
	cemaphore=True
	for file in file_list:
		for committer in file_list[file]['committers']:
			if cemaphore:
				json=json+'{"source":'+str(file_list[file]['num'])+',"target":'+str(contributers_list[committer]['num'])+',"value":'+str(file_list[file]['committers'][committer])+'}'
				cemaphore=False
			else:
				json=json+',{"source":'+str(file_list[file]['num'])+',"target":'+str(contributers_list[committer]['num'])+',"value":'+str(file_list[file]['committers'][committer])+'}'

	json=json+'],"max1":'+str(max_user_commit)+',"max2":'+str(max_file_commit)+'}'
	print '\033[92m'+" ok"+'\033[0m'



	##########################
	# Display the 3D graph 1 #
	##########################

	# jsonfile = open(fileName, "wb+")
	# jsonfile.write(json)
	# jsonfile.close()

	return mod.make_3d_graph(json)
#--------------------
# To get all the users of a project  
# that talked on an issue            
# Python Github API
def getUserOnIssue():
	print '\033[4m'+"----Collecting issue data: /"+org+'/'+repo+"/ ----"+'\033[0m'
	print "[*]Getting project issues..."
	issueList={}
	userList={}
	issue_list = gh.issues.list_by_repo(user=org, repo=repo,state='open').all()
	for resource in issue_list:
		issueList[resource.number]={'number':resource.number,'author':resource.user.login,'state':resource.state, 'commenters':{resource.user.login:1}, 'comments':0, 'num':0}
		print '    ',resource.number

		if userList.has_key(resource.user.login):
			userList[resource.user.login]['comments']+=1
		else:
			userList[resource.user.login]={'comments':1,'login':resource.user.login, 'id':resource.user.id, 'num':0}
		# print resource.user.login
		data=gh.issues.comments.list(number=resource.number, user=org, repo=repo).all()
		for comment in data:
			# print "    ",comment.user.login
			issueList[resource.number]['comments']+=1
			if issueList[resource.number]['commenters'].has_key(comment.user.login):
				issueList[resource.number]['commenters'][comment.user.login]+=1
			else:
				issueList[resource.number]['commenters'][comment.user.login]=1

			if userList.has_key(comment.user.login):
				userList[comment.user.login]['comments']+=1
			else:
				userList[comment.user.login]={'comments':1,'login':comment.user.login, 'id':comment.user.id, 'num':0}


	print '\033[92m'+"[Done]"+'\033[0m'
	
	return issueList,userList
#--------------------
def makeComments(issueList,userList):


	#########################
	# Graph of the comments #
	#########################

	fileName=org+'-'+repo+'.comment.json'
	max_file_comment=1
	max_user_comment=1


	# Giving a single number for the graph drawing to each node according to python's order of dictionary
	nodesNumber=0

	cpt=0 # To attribute each node a unique number for the links of the graph

	print '\033[4m'+"----Making comments json file: "+fileName+"----"+'\033[0m'

	print "[issues]",
	json = ''
	json=json+ '{"type":"comments","organisation":"'+org+'","repository":"'+repo+'","directory":"'+directory+'","nodes":['
	for issue in issueList:
		issueList[issue]['num']=cpt
		if issueList[issue]['comments']>max_file_comment:
			max_file_comment=issueList[issue]['comments']
		cpt+=1
		json=json+'{"type":"issue","number":"'+str(issueList[issue]['number'])+'","state":"'+issueList[issue]['state']+'","num":"'+str(issueList[issue]['num'])+'","comments":"'+str(issueList[issue]['comments'])+'","group":1},'
	print '\033[92m'+" ok"+'\033[0m'


	print "[commenters]",
	cemaphore=True
	for commenter in userList:
		userList[commenter]['num']=cpt
		if userList[commenter]['comments']>max_user_comment:
			max_user_comment=userList[commenter]['comments']
		cpt+=1
		if cemaphore:
			json=json+'{"type":"commenter","login":"'+userList[commenter]['login']+'","num":"'+str(userList[commenter]['num'])+'","comments":"'+str(userList[commenter]['comments'])+'","id":"'+str(userList[commenter]['id'])+'","group":'+str((userList[commenter]['comments']/20)+4)+'}'
			cemaphore=False
		else:
			json=json+',{"type":"commenter","login":"'+userList[commenter]['login']+'","num":"'+str(userList[commenter]['num'])+'","comments":"'+str(userList[commenter]['comments'])+'","id":"'+str(userList[commenter]['id'])+'","group":'+str((userList[commenter]['comments']/20)+4)+'}'
				  
	print '\033[92m'+" ok"+'\033[0m'

	print "[links]",
	json=json+'],"links":['
	cemaphore=True
	for issue in issueList:
		for commenter in issueList[issue]['commenters']:
			if cemaphore:
				json=json+'{"source":'+str(issueList[issue]['num'])+',"target":'+str(userList[commenter]['num'])+',"value":'+str(issueList[issue]['commenters'][commenter])+'}'
				cemaphore=False
			else:
				json=json+',{"source":'+str(issueList[issue]['num'])+',"target":'+str(userList[commenter]['num'])+',"value":'+str(issueList[issue]['commenters'][commenter])+'}'

	json=json+'],"max1":'+str(max_user_comment)+',"max2":'+str(max_file_comment)+'}'
	print '\033[92m'+" ok"+'\033[0m'

	# jsonfile = open(fileName, "wb+")
	# jsonfile.write(json)
	# jsonfile.close()

	return mod.make_3d_graph(json)
#--------------------
def finalJson(file_list,contributers_list,issueList,userList):

	print '\033[4m'+"----Making final json file: "+org+"/"+repo+".json----"+'\033[0m'

	###################
	# final json file #
	###################

	fileName=org+'-'+repo+'.json'

	num=0
	# Here we have to make a unique number for each participant

	print "[files]",
	json=''
	json=json+ '{"organisation":"'+org+'","repository":"'+repo+'","directory":"'+directory+'","files":[';
	cemaphore=True
	for file in file_list:
		if cemaphore:
			json=json+'{"name":"'+file_list[file]['name']+'","type":"'+file_list[file]['type']+'","size":"'+str(file_list[file]['size'])+'","commits":"'+str(file_list[file]['commits'])+'","author":"'+str(file_list[file]['author'])+'","commiters":['
			cemaphore=False
		else:
			json=json+',{"name":"'+file_list[file]['name']+'","type":"'+file_list[file]['type']+'","size":"'+str(file_list[file]['size'])+'","commits":"'+str(file_list[file]['commits'])+'","author":"'+str(file_list[file]['author'])+'","commiters":['

		cemaphore=True
		for contributor in file_list[file]['committers']:
			if cemaphore:
				json=json+'{"login":"'+str(contributers_list[contributor]['login'])+'","num":"'+str(contributers_list[contributor]['num'])+'","url":"'+str(contributers_list[contributor]['url'])+'","id":'+str(contributers_list[contributor]['id'])+',"commits":'+str(file_list[file]['committers'][contributor])+',"commiters-info":['
				cemaphore=False
			else:
				json=json+',{"login":"'+str(contributers_list[contributor]['login'])+'","num":"'+str(contributers_list[contributor]['num'])+'","url":"'+str(contributers_list[contributor]['url'])+'","id":'+str(contributers_list[contributor]['id'])+',"commits":'+str(file_list[file]['committers'][contributor])+',"commiter-info":['
			num+=1

			cemaphore=True
			for committer in contributers_list[contributor]['committers']:
				if cemaphore:
					json=json+'{"name":"'+str(contributers_list[contributor]['committers'][committer]['name'])+'","email":"'+str(contributers_list[contributor]['committers'][committer]['email'])+'","sha":"'+str(contributers_list[contributor]['committers'][committer]['sha'])+'","date":"'+str(contributers_list[contributor]['committers'][committer]['date'])+'"}'
					cemaphore=False
					
				else:
					json=json+',{"name":"'+str(contributers_list[contributor]['committers'][committer]['name'])+'","email":"'+str(contributers_list[contributor]['committers'][committer]['email'])+'","sha":"'+str(contributers_list[contributor]['committers'][committer]['sha'])+'","date":"'+str(contributers_list[contributor]['committers'][committer]['date'])+'"}'
			json=json+']}'
		json=json+']}'
		


	print '\033[92m'+" ok"+'\033[0m'


	print "[issues]",
	json=json+ '],"issues":['
	cemaphore=True
	for issue in issueList:
		if cemaphore:
			json=json+'{"number":'+str(issueList[issue]['number'])+',"state":"'+issueList[issue]['state']+'","author":"'+str(issueList[issue]['author'])+'","comments":'+str(issueList[issue]['comments'])+',"commenters":['
			cemaphore=False
		else:
			json=json+',{"number":'+str(issueList[issue]['number'])+',"state":"'+issueList[issue]['state']+'","author":"'+str(issueList[issue]['author'])+'","comments":'+str(issueList[issue]['comments'])+',"commenters":['

		cemaphore=True
		for commenter in issueList[issue]['commenters']:
			if cemaphore:
				json=json+'{"login":"'+str(userList[commenter]['login'])+'","id":'+str(userList[commenter]['id'])+',"comments":'+str(issueList[issue]['commenters'][commenter])+',"total-comments":'+str(userList[commenter]['comments'])+'}'
				cemaphore=False
			else:
				json=json+',{"login":"'+str(userList[commenter]['login'])+'","id":'+str(userList[commenter]['id'])+',"comments":'+str(issueList[issue]['commenters'][commenter])+',"total-comments":'+str(userList[commenter]['comments'])+'}'
		json=json+']}'

	json=json+']}'
	print '\033[92m'+" ok"+'\033[0m'

	try:
		jsonfile = open(fileName)
		print "Json file exists !"
	except Exception, e:
		jsonfile = open(fileName, "wb+")
		jsonfile.write(json)
		jsonfile.close()
		print "Json file created !"

	print "[finished]", '\033[0m'

	print 'Done'

	return m.contribution(json)
#----------------------------------------------------------------------


#----------------------------------------------------------------------
def Prepare(puser,pp,porg,prepo):
	
	#######################################
	# Prepare all the infos and variables #
	#######################################
	global u
	global p
	global org
	global repo
	global directory
	global fileName
	global logged
	global gh
	global repo_content
	
	u=puser
	p=pp

	logged=True

	org=porg # The company name the project belongs to
	temp=prepo.split('/',1)
	repo=temp[0] # The project to analyse
	directory=''
	fileName=org+'-'+repo+'.contribution.json'

	if len(temp)>1:
		directory=temp[1] # Where to make the graph
		fileName=org+'-'+repo+'>'+directory+'.json'


	if u!='':
		url='https://api.github.com/users/'+u
		data=sendRequest(url)
		if data==False:
			logged=False


	if logged:
		# Python Github API
		# gh = Github()
		gh = Github(login=u, password=p)
		name=data['name']
		idnumber=data['id']
		if name=='':
			name=u
		message='Logged as '+name
	else:
		gh = Github()
		message='Login failed ! annonimous...'

	repo_content = getContent(directory)

	foundRepo=True

	if repo_content==False:
		error="Error: Unable to find repository ! "
		print error
		message=message+' '+error
		foundRepo=False

	return logged,message,foundRepo

	#############
	# Execution #
	#############

def graphContribution():
	global file_list
	global contributers_list

	
	contributers_list={}
	file_list, contributers_list = commitersOfDirectory(contributers_list,repo,repo_content)

	layout1, data1=makeContribution(file_list,contributers_list)

	return layout1, data1

def graphComments():
	global issueList
	global userList

	issueList, userList = getUserOnIssue()

	layout2, data2=makeComments(issueList,userList)

	return layout2, data2

def graphMetrics():

	rep = finalJson(file_list,contributers_list,issueList,userList)

	return rep
#---------------------------------------------------------------------- 


#----------------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv)!=4:
		print '\033[91m'+"-------------\nError: expected 3 argument, "+str(len(sys.argv)-1)+" given\nusage:\n      python "+sys.argv[0]+"  <login(you)>  <user>  <repositoryOfUser/directory>\n-------------"+'\033[0m'
		quit()

	global p
	p=getpass.getpass()
	Prepare(sys.argv[1],p,sys.argv[2],sys.argv[3])
	graphContribution()
	graphComments()
	graphMetrics()

