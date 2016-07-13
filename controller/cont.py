from datetime import datetime
from controller.Draw import *

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
def make_contribution(repo):

	num=0
	# Here we have to make a unique number for each participant
	today=datetime.now()
	
	jsonfile = open(repo.file_name, "wb+")
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
	return draw_contribution(text+']}')
#--------------------