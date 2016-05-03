# -*- coding: utf-8 -*-
import time, getpass, sys
import json, urllib2

import shared_data as sh

sh.time = time.time()

if len(sys.argv)<4 or len(sys.argv)>5:
	print '\033[91m'+"-------------\nError: expected at least 3 arguments, "+str(len(sys.argv)-1)+" given\nusage:\n      python "+sys.argv[0]+"  <login(you)>  <user>  <repositoryOfUser/directory>\n-------------"+'\033[0m'
	quit()

u=sys.argv[1]
org=sys.argv[2] # The company name the project belongs to
temp=sys.argv[3].split('/',1)
repo=temp[0] # The project to analyse
directory=''
fileName=org+'-'+repo+'.json'

if len(temp)>1:
	directory=temp[1] # Where to make the graph
	fileName=org+'-'+repo+'>'+directory+'.json'

# Sharing the data in the common 'sh.py' to all modules
sh.fileName=fileName
sh.org=org
sh.directory=directory
sh.org=org
sh.repo=repo
sh.graph_type='contribution'


file=''
user=''
max_user_commit=1
max_file_commit=1
UnknownUser_id=1 #Will be used to identify a Unknown user

p=getpass.getpass()

# simple wrapper function to encode the username & pass
def encodeUserData(user, password):
  return "Basic " + (user + ":" + password).encode("base64").rstrip()
# simple function to make the url request to github and parse the result in Json
def sendRequest(url):
    data=[]
    req = urllib2.Request(url)
    req.add_header('Accept', 'application/json')
    req.add_header("Content-type", "application/x-www-form-urlencoded")
    req.add_header('Authorization', encodeUserData(u, p))
    # make the request and print the results
    try:
        res = urllib2.urlopen(req)
        return json.loads(res.read())
    except urllib2.HTTPError, e:
        print '\033[91m'+"\n----Error----\n"+e.fp.read()+"\n-------------\n"+'\033[0m'
        quit()
    # print res.read()
    # parse the result in json format
    

#################################
# To get the repository content #
#################################
def getContent(directory):
    print "[*]Getting project content..."
    url='https://api.github.com/repos/'+org+'/'+repo+'/contents/'+directory+'/'
    data = sendRequest(url)

    content={}
    # get the number of elements in the repository and print it
    for file in data:
        content[file['name']] = {'name':directory+'/'+file['name'],'size':file['size'],'type':file['type']}
    print '\033[92m'+"[Done]"+'\033[0m'
    return content


######################################
# To get all the contributors of a   #
# file and their number of commits   #
######################################
# Python Github API
from pygithub3 import Github
gh = Github(login=u, password=p)
sh.gh=gh
def commitersOfFile(contributorsList,repo,file):

    # This URL shows what iformation can be get about commits (email addresses, etc...)
    # curl -i -u AlexFabre https://api.github.com/repos/twbs/grunt-bootlint/commits/ae31bb28f74b306437ca6cb34662935c3910434e

    fileContributors={} # The Commiters of the file
    print '    '+file, # the file we are going to list the commits
    # Let's get the entire commit's hirstory of the file
    commitList=gh.repos.commits.list(user=org, repo=repo, path=file).all()
    num_commit=len(commitList)
    print str(num_commit)+' commits' # The length of the list id: number of commits

    for commit in commitList:
    	# # Let's get all the infos aboout a commit
     #    url='https://api.github.com/repos/'+org+'/'+repo+'/commits/'+str(commit)[12:-2]
     #    data = sendRequest(url)


        # We get all infos about the committer who approved the commit
        committer_name=commit.commit.committer.name # His real name, not a login
        committer_email=commit.commit.committer.email
        committer_message=commit.commit.message
        commit_date=commit.commit.committer.date # Date of this commit
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
            contributorsList[contributor_login]={'num':0 ,'login': contributor_login.encode('ascii', 'replace'), 'id': contributor_id, 'commits': 1, 'name':committer_name.encode('ascii', 'replace'), 'committers':{}}
            contributorsList[contributor_login.encode('ascii', 'replace')]['committers'][committer_name.encode('ascii', 'replace')]={'name': committer_name.encode('ascii', 'replace'), 'email':committer_email.encode('ascii', 'replace'), 'message':committer_message.encode('ascii', 'replace'), 'date':commit_date, 'sha': commit_sha}

        if fileContributors.has_key(contributor_login):
            fileContributors[contributor_login]+=1
        else:
            fileContributors[contributor_login]=1

    return num_commit, contributorsList, fileContributors

######################################
# To get all the contributors of all #
# files and their number of commits  #
######################################
def commitersOfDirectory(contributorsList,repo,content):
    print "[*]Getting the commiters..."
    fileList={}
    for file in content:
        fileList[content[file]['name']]={'name':content[file]['name'],'type':content[file]['type'],'size':content[file]['size'],'num':0}
        fileList[content[file]['name']]['commits'], contributorsList, fileList[content[file]['name']]['committers']=(commitersOfFile(contributorsList,repo,content[file]['name']))
    print '\033[92m'+"[Done]"+'\033[95m', str(len(contributorsList))+' contributors'+'\033[0m'
    return fileList, contributorsList
        

print '\033[4m'+"----Collecting data: /"+org+'/'+repo+"/"+directory+" ----"+'\033[0m'


content = getContent(directory)
contributorsList={}
commitsPerFile, contributersList = commitersOfDirectory(contributorsList,repo,content)

# Giving a single number for the graph drawing to each node according to python's order of dictionary
nodesNumber=0

cpt=0 # To attribute each node a unique number for the links of the graph

print '\033[4m'+"----Making json file: "+fileName+"----"+'\033[0m'

print "[files]",
json = open(fileName, "wb+")
json.write( '{"nodes":[');
for file in commitsPerFile:
    commitsPerFile[file]['num']=cpt
    if commitsPerFile[file]['commits']>max_file_commit:
    	max_file_commit=commitsPerFile[file]['commits']
    cpt+=1
    json.write('{"name":"'+commitsPerFile[file]['name']+'","type":"'+commitsPerFile[file]['type']+'","num":"'+str(commitsPerFile[file]['num'])+'","size":"'+str(commitsPerFile[file]['size'])+'","commits":"'+str(commitsPerFile[file]['commits'])+'","group":1},')
print '\033[92m'+" ok"+'\033[0m'


print "[contributors]",
cemaphore=True
for contributor in contributersList:
    contributersList[contributor]['num']=cpt
    if contributersList[contributor]['commits']>max_user_commit:
    	max_user_commit=contributersList[contributor]['commits']
    cpt+=1
    if cemaphore:
        json.write('{"login":"'+contributersList[contributor]['login']+'","num":"'+str(contributersList[contributor]['num'])+'","commits":"'+str(contributersList[contributor]['commits'])+'","name":"'+contributersList[contributor]['name']+'","type":"user","id":"'+str(contributersList[contributor]['id'])+'","group":'+str((contributersList[contributor]['commits']/20)+4)+'}')
        cemaphore=False
    else:
        json.write(',{"login":"'+contributersList[contributor]['login']+'","num":"'+str(contributersList[contributor]['num'])+'","commits":"'+str(contributersList[contributor]['commits'])+'","name":"'+contributersList[contributor]['name']+'","type":"user","id":"'+str(contributersList[contributor]['id'])+'","group":'+str((contributersList[contributor]['commits']/20)+4)+'}')
              
print '\033[92m'+" ok"+'\033[0m'


print "[links]",
json.write('],"links":[')
cemaphore=True
for file in commitsPerFile:
    for committer in commitsPerFile[file]['committers']:
        if cemaphore:
            json.write('{"source":'+str(commitsPerFile[file]['num'])+',"target":'+str(contributersList[committer]['num'])+',"value":'+str(commitsPerFile[file]['committers'][committer])+'}')
            cemaphore=False
        else:
            json.write(',{"source":'+str(commitsPerFile[file]['num'])+',"target":'+str(contributersList[committer]['num'])+',"value":'+str(commitsPerFile[file]['committers'][committer])+'}')

json.write(']}')
print '\033[92m'+" ok"+'\033[0m'

json.close()

sh.max_user_commit=max_user_commit
sh.max_file_commit=max_file_commit

import module_3Dgraph
