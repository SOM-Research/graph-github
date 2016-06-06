# -*- coding: utf-8 -*-
from flask import Flask, request, Response, render_template, url_for
import graphGithub as gph
import simplejson as json

app = Flask(__name__)


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route("/getCont",methods=['GET', 'POST'])
def getContribution():
	
	user = request.values.get('user')
	p = request.values.get('pass')
	org = request.values.get('org')
	repo = request.values.get('repo')
	
	rep=gph.prepare(user,p,org,repo)

	if rep['repo_exists']==False: # In case the repository wasn't found
		req={'login_succeded':rep['login_succeded'],'message':rep['message'],'repo_exists':rep['repo_exists']}
		return Response(json.dumps(req), mimetype='text/json')

	req=gph.getContribution(rep['user'],rep['repo'])
	req['login_succeded']=rep['login_succeded']
	req['message']=rep['message']
	req['repo_exists']=rep['repo_exists']

	return Response(json.dumps(req), mimetype='text/json')

@app.route("/getComm",methods=['GET', 'POST'])
def getComments():
	
	user = request.values.get('user')
	p = request.values.get('pass')
	org = request.values.get('org')
	repo = request.values.get('repo')
	
	rep=gph.prepare(user,p,org,repo)
	req=gph.getComments(rep['user'],rep['repo'])

	return Response(json.dumps(req), mimetype='text/json')

if __name__ == "__main__":
	app.run()
	url_for('static', filename='styles.css')
	url_for('static', filename='dessin.svg')
	url_for('static', filename='error.svg')
	url_for('static', filename='unknown.gif')
	url_for('static', filename='ex_comment.png')
	url_for('static', filename='ex_contribution.png')
