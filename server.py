# -*- coding: utf-8 -*-
from flask import Flask, session, redirect, request, Response, render_template, url_for, jsonify
from flask.json import JSONEncoder
from model.User import *
from model.Repository import *
from Application import *
from controller.Draw import *
from datetime import datetime, timedelta
import simplejson as json
from pygithub3 import Github

class CustomJSONEncoder(JSONEncoder):
	def default(self, obj):
		if isinstance(obj, User):
			dic={'login':obj.login,'p':obj.p,'name':obj.name,'logged':obj.logged}
			return dic
		if isinstance(obj, Repository):
			dic={'org':obj.org,'name':obj.name,'directory':obj.directory,'json_exists':obj.json_exists,'exists':obj.exists,'content':obj.content,'file_name':obj.file_name}
			return dic
		else:
			JSONEncoder.default(self, obj)

def CustomDecoder(dic):
	if dic.has_key('login'):
		user = User(dic['login'],dic['p'])
		user.name=dic['name']
		user.logged=dic['logged']
		return user
	if dic.has_key('org'):
		repo = Repository(dic['org'],dic['name'])
		repo.directory=dic['directory']
		repo.json_exists=dic['json_exists']
		repo.exists=dic['exists']
		repo.content=dic['content']
		repo.file_name=dic['file_name']
		return repo
	else:
		print "Error while decoding object, unknown object: ",dic

def github_connexion(user):
		print "[*]Connecting to github..."
		if user.logged:
			# Python Github API
			user.gh = Github(login=user.login, password=user.p)
			return True
		else:
			user.gh = Github()
			return False
		print '\033[92m'+"[Done]"+'\033[0m'


app = Flask(__name__)
app.secret_key = "7z9AHeFNz2p31gn06eh8erj457h4Hl5"
app.json_encoder = CustomJSONEncoder

def logout():
	session.pop('user', None)
	session.pop('repo', None)
	return redirect(url_for('index'))

def check_existing_file(repo):
	print "[*]Checking presence of file..."
	two_days_ago=datetime.now()-timedelta(days=2)
	try:
		jsonfile = open(repo.file_name)
		temp=json.loads(jsonfile.read())
		print "JSON file exists",
		file_date=datetime.strptime(temp['date'], "%Y-%m-%d")
		if file_date>=two_days_ago and temp.has_key('files') and temp.has_key('issues'):
			print "& is complete"
			repo.json_exists=True
			jsonfile.close()
		else:
			repo.json_exists=False
			print 'but too old or incomplete...'
	except Exception, e:
		print e
		repo.json_exists=False
	print '\033[92m'+"[Done]"+'\033[0m'

def prepare(user_login,user_p,repo_org,repo_name):
	print "----Checking data----"

	user = User(user_login,user_p)
	repo = Repository(repo_org,repo_name)
	
	print user.name

	session['user']=user

	if repo.get_content(user):
		check_existing_file(repo)
		session['repo']=repo
	else:
		print "No such repository on Github !"

	return {'user_logged':user.name,'repo_exists':repo.exists}

@app.route('/')
@app.route('/index.html')
def index():
	return render_template('index.html')

@app.route('/log',methods=['GET','POST'])
def login_client():
	if request.method == 'POST':
		user_login = request.form['user']
		user_p = request.form['pass']
		repo_org = request.form['org']
		repo_name = request.form['repo']

	if request.method == 'GET':	
		user_login = ""
		user_p = ""
		repo_org = request.values.get('org')
		repo_name = request.values.get('repo')

	rep=prepare(user_login,user_p,repo_org,repo_name)

	print "[*]Sending Response"
	return Response(json.dumps(rep), mimetype='text/json')


@app.route("/getCont",methods=['GET'])
def getContribution():

	session['user']=CustomDecoder(session['user'])
	session['repo']=CustomDecoder(session['repo'])

	github_connexion(session['user'])

	name = request.values.get('repo')

	if session['repo'].name==name and session['repo'].json_exists==True:
		file=open(session['repo'].file_name)
		rep=draw_contribution(file.read())
		file.close()
	else:
		rep=get_contribution(session['user'],session['repo'])

	print rep.keys()
	return Response(json.dumps(rep), mimetype='text/json')

@app.route("/getComm")
def getComments():

	session['user']=CustomDecoder(session['user'])
	session['repo']=CustomDecoder(session['repo'])

	github_connexion(session['user'])

	name = request.values.get('repo')

	if session['repo'].name==name and session['repo'].json_exists==True:
		file=open(session['repo'].file_name)
		rep=draw_contribution(file.read())
		file.close()
	else:
		rep=get_comments(session['user'],session['repo'])

	return Response(json.dumps(rep), mimetype='text/json')


if __name__ == "__main__":
	app.run()
	url_for('static', filename='styles.css')
	url_for('static', filename='dessin.svg')
	url_for('static', filename='error.svg')
	url_for('static', filename='unknown.gif')
	url_for('static', filename='ex_comment.png')
	url_for('static', filename='ex_contribution.png')
