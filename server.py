# -*- coding: utf-8 -*-
from flask import Flask, request, Response, render_template, url_for
import graphGithub as gph
import simplejson as json

app = Flask(__name__)


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route("/log",methods=['GET', 'POST'])
def login():
	
	user = request.values.get('user')
	p = request.values.get('pass')
	org = request.values.get('org')
	repo = request.values.get('repo')
	
	logged,message,foundRepo = gph.Prepare(user,p,org,repo)

	rep = {'login_succeded':logged,'message':message,'repo_exists':foundRepo}

	return Response(json.dumps(rep), mimetype='text/json')

@app.route("/getCont")
def getContribution():
	
	layout1, data1=gph.graphContribution()

	rep={'layout':layout1,'data':data1}

	return Response(json.dumps(rep), mimetype='text/json')

@app.route("/getComm")
def getComments():
	
	layout2, data2=gph.graphComments()

	rep={'layout':layout2,'data':data2}

	return Response(json.dumps(rep), mimetype='text/json')

@app.route("/getAll")
def getAllRepo():

	
	rep=gph.graphMetrics()
	
	return Response(json.dumps(rep), mimetype='text/json')

if __name__ == "__main__":
	app.run()
	url_for('static', filename='styles.css')
	url_for('static', filename='dessin.svg')
	url_for('static', filename='error.svg')
	url_for('static', filename='unknown.gif')
	url_for('static', filename='ex_comment.png')
	url_for('static', filename='ex_contribution.png')
