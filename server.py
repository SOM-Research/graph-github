# -*- coding: utf-8 -*-
from flask import Flask, request, Response, render_template, url_for
import graphGithub as gph
import simplejson as json

app = Flask(__name__)


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route("/getAll")
def getAllRepo():
	
	user = request.values.get('user')
	org = request.values.get('org')
	repo = request.values.get('repo')
	p='Srp043k1'
	
	gph.Prepare(user,p,org,repo)
	rep=gph.graphMetrics()
	
	return Response(rep, mimetype='text')

@app.route("/getCont")
def getContribution():
	
	user = request.values.get('user')
	org = request.values.get('org')
	repo = request.values.get('repo')
	p='Srp043k1'
	
	gph.Prepare(user,p,org,repo)
	layout1, data1=gph.graphContribution()

	rep={'layout':layout1,'data':data1}

	return Response(json.dumps(rep), mimetype='text/json')

@app.route("/getComm")
def getComments():
	
	user = request.values.get('user')
	org = request.values.get('org')
	repo = request.values.get('repo')
	p='Srp043k1'
	
	gph.Prepare(user,p,org,repo)
	layout2, data2=gph.graphComments()

	rep={'layout':layout2,'data':data2}

	return Response(json.dumps(rep), mimetype='text/json')

@app.route("/refreshCont")
def reloadContribution():
	
	user = request.values.get('file')
	rep='reloading contribution 3D'
	
	return Response(rep, mimetype='text')

@app.route("/reloadComm")
def reloadComments():
	
	user = request.values.get('file')
	rep='reloading comments 3D'
	
	return Response(rep, mimetype='text')

@app.route("/reloadM")
def reloadMetrics():
	
	user = request.values.get('file')
	rep='reloading metrics'
	
	return Response(rep, mimetype='text')


if __name__ == "__main__":
	app.run()
	url_for('static', filename='styles.css')
	url_for('static', filename='dessin.svg')