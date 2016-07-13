# -*- coding: utf-8 -*-
from controller.cont import *
from controller.com import *

#----------------------------------------------------------------------
def get_contribution(user,repo):
	print "----Mining Repository (contribution)----"
	print "[*]Getting the commiters..."
	for file in repo.content:
		repo.file_list[repo.content[file]['name']]={'name':repo.content[file]['name'],'type':repo.content[file]['type'],'size':repo.content[file]['size'],'num':0}
		repo.file_list[repo.content[file]['name']]['commits'], repo.file_list[repo.content[file]['name']]['author'], repo.file_list[repo.content[file]['name']]['committers']=(commitersOfFile(user,repo,repo.content[file]['name']))
	print '\033[92m'+"[Done]"+'\033[95m', str(len(repo.contributers_list))+' contributors'+'\033[0m'

	return make_contribution(repo)
# Use Github API to get all the issues
def get_comments(user,repo):
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

	return make_comments(repo)
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

