# -*- coding: utf-8 -*-
from flask import Flask, request, Response
import metric as m

app = Flask(__name__)

@app.route("/get")
def getRepo():
	
	org = request.values.get('org')
	repo = request.values.get('repo')
	
	rep=m.contribution('twbs-bootstrap-blog.json')

	# return Response(rep, mimetype='text/json')
	return Response(rep)

if __name__ == "__main__":
	app.run()