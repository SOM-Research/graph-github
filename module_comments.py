from pygithub3 import Github

gh = Github(login='AlexFabre', password='Srp043k1')



issue_list = gh.issues.list_by_repo(user='twbs', repo='bootstrap',state='open').all()
for resource in issue_list:
	print resource.number
	print resource.user.login
	data=gh.issues.comments.list(number=resource.number, user='twbs', repo='bootstrap').all()
	for comment in data:
		print "    ",comment.user.login
	
