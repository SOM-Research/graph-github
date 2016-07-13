from controller.Draw import *

# Completting json file with issues and commenters
def make_comments(repo):
	#--------------------
	# Graph of the comments 

	jsonfile = open(repo.file_name,'a')

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

	return draw_comments('{"organisation":"'+repo.org+'","repository":"'+repo.name+'","directory":"'+repo.directory+'",'+text)
