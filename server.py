# -*- coding: utf-8 -*-
from flask import Flask, request, Response
import graphGithub as gph

app = Flask(__name__)

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

	return Response(layout1, mimetype='text/json')

@app.route("/getComm")
def getComments():
	
	user = request.values.get('user')
	org = request.values.get('org')
	repo = request.values.get('repo')
	p='Srp043k1'
	
	gph.Prepare(user,p,org,repo)
	layout2, data2=gph.graphComments()

	return Response(layout2, mimetype='text/json')

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