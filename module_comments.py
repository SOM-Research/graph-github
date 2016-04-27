from pygithub3 import Github

import shared_data

gh=shared_data.gh
org=shared_data.org
repo=shared_data.repo


issue_list = gh.issues.list_by_repo(user=org, repo=repo,state='close').all()
for resource in issue_list:
	# print resource.number
	# print resource.user.login
	data=gh.issues.comments.list(number=resource.number, user='twbs', repo='bootstrap').all()
	for comment in data:
		# print "    ",comment.user.login
	
