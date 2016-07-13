# -*- coding: utf-8 -*-
import urllib2, json
#----------------------------------------------------------------------
# Function to send and receive from github API
# wrapper function to encode the username & pass
def encode(user, password):
	return "Basic " + (user + ":" + password).encode("base64").rstrip()
#--------------------
# simple function to make the url request 
# to github and parse the result in Json  
def send(url,user):

	data=[]
	req = urllib2.Request(url)
	req.add_header('Accept', 'application/json')
	req.add_header("Content-type", "application/x-www-form-urlencoded")
	if user.logged:
		print '(Sending request as '+user.login+')'
		req.add_header('Authorization', encode(user.login, user.p))
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