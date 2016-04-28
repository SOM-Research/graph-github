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
fileName='comments-'+org+'-'+repo+'.json'file=''
user=''
max_file_comment=0
max_user_comment=0
UnknownUser_id=1 #Will be used to identify a Unknown user
# Sharing the data in the common 'sh.py' to all modules
sh.fileName=fileName
sh.org=org
sh.repo=repo
sh.graph_type='comments'

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
    userList={}
    issue_list = gh.issues.list_by_repo(user=org, repo=repo,state='open').all()
    for resource in issue_list:
        issueList[resource.number]={'number':resource.number,'author':resource.user.login,'state':resource.state, 'commenters':{resource.user.login:1}, 'comments':0, 'num':0}
        print resource.number

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


  
    return issueList,userList
    
issueList, userList = getUserOnIssue()

# Giving a single number for the graph drawing to each node according to python's order of dictionary
nodesNumber=0

cpt=0 # To attribute each node a unique number for the links of the graph

print '\033[4m'+"----Making json file: "+fileName+" ----"+'\033[0m'

print "[issues]",
json = open(fileName, "wb+")
json.write( '{"nodes":[');
for issue in issueList:
    issueList[issue]['num']=cpt
    if issueList[issue]['comments']>max_file_comment:
    	max_file_comment=issueList[issue]['comments']
    cpt+=1
    json.write('{"type":"issue","number":"'+str(issueList[issue]['number'])+'","state":"'+issueList[issue]['state']+'","num":"'+str(issueList[issue]['num'])+'","comments":"'+str(issueList[issue]['comments'])+'","group":1},')
print '\033[92m'+" ok"+'\033[0m'


print "[commenters]",
cemaphore=True
for user in userList:
    userList[user]['num']=cpt
    if userList[user]['comments']>max_user_comment:
    	max_user_comment=userList[user]['comments']
    cpt+=1
    if cemaphore:
        json.write('{"type":"user","login":"'+userList[user]['login']+'","num":"'+str(userList[user]['num'])+'","comments":"'+str(userList[user]['comments'])+'","id":"'+str(userList[user]['id'])+'","group":'+str((userList[user]['comments']/20)+4)+'}')
        cemaphore=False
    else:
        json.write(',{"type":"user","login":"'+userList[user]['login']+'","num":"'+str(userList[user]['num'])+'","comments":"'+str(userList[user]['comments'])+'","id":"'+str(userList[user]['id'])+'","group":'+str((userList[user]['comments']/20)+4)+'}')
              
print '\033[92m'+" ok"+'\033[0m'

print "[links]",
json.write('],"links":[')
cemaphore=True
for issue in issueList:
    for user in issueList[issue]['commenters']:
        if cemaphore:
            json.write('{"source":'+str(issueList[issue]['num'])+',"target":'+str(userList[user]['num'])+',"value":'+str(issueList[issue]['commenters'][user])+'}')
            cemaphore=False
        else:
            json.write(',{"source":'+str(issueList[issue]['num'])+',"target":'+str(userList[user]['num'])+',"value":'+str(issueList[issue]['commenters'][user])+'}')

json.write(']}')
print '\033[92m'+" ok"+'\033[0m'

json.close()

sh.max_user_comment=max_user_comment
sh.max_file_comment=max_file_comment

import module_3Dgraph
