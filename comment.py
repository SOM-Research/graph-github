# -*- coding: utf-8 -*-
import time, getpass, sys
import shared_data as sh

sh.time = time.time()

if len(sys.argv)<4 or len(sys.argv)>5:
	print '\033[91m'+"-------------\nError: expected at least 3 arguments, "+str(len(sys.argv)-1)+" given\nusage:\n      python "+sys.argv[0]+"  <login(you)>  <user>  <repositoryOfUser>\n-------------"+'\033[0m'
	quit()

u=sys.argv[1]
org=sys.argv[2] # The company name the project belongs to
repo=sys.argv[3] # The project to analyse
fileName='comment'+org+'-'+repo+'.json'
file=''
user=''
UnknownUser_id=1 #Will be used to identify a Unknown user
# Sharing the data in the common 'sh.py' to all modules
sh.fileName=fileName
sh.org=org
sh.repo=repo

p=getpass.getpass()


######################################
# To get all the users of a project  #
# that talked on an issue            #
######################################
# Python Github API
from pygithub3 import Github
gh = Github(login=u, password=p)

def getUserOnIssue():
    issueList={}
    issue_list = gh.issues.list_by_repo(user=org, repo=repo,state='open').all()
    for resource in issue_list:
        issueList[resource.number]={'number':resource.number,'author':resource.user.login, 'commenter':{}, 'comment':0}
        print resource.number
        # print resource.user.login
        data=gh.issues.comments.list(number=resource.number, user=org, repo=repo).all()
        for comment in data:
            # print "    ",comment.user.login
            issueList[resource.number]['comment']+=1
            issueList[resource.number]['commenter'][comment.user.login]=1
    return issueList
    
issueList=getUserOnIssue()
print issueList

quit()

# Giving a single number for the graph drawing to each node according to python's order of dictionary
nodesNumber=0

cpt=0 # To attribute each node a unique number for the links of the graph

print '\033[4m'+"----Making json file: "+fileName+" ----"+'\033[0m'

print "[issue]",
json = open(fileName, "wb+")
json.write( '{"nodes":[');
for issue in issueList:
    issueList[issue]['num']=cpt
    cpt+=1
    json.write('{"number":"'+issueList[issue]['number']+'","author":"'+issueList[issue]['author']+'","num":"'+str(issueList[issue]['num'])+'","comments":"'+str(issueList[issue]['comments'])+'","group":1},')
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

import module_drawing
