# -*- coding: utf-8 -*-
from igraph import *
import igraph as ig
import json, urllib2, sys

import plotly.plotly as py
from plotly.graph_objs import *


def contribution(file):


	# Degree of Authorship (DOA) = 3.293 + 1.098 ∗ FA + 0.164 ∗ DL − 0.321 ∗ ln(1 + AC )
	# first authorship (FA), number of deliveries (DL), number of acceptances (AC)

	data = []

	data = json.loads(file)

	commiter_list={}
	name_list=[]
	Edges={}
	num=0
	for file in data['files']:
		cemaphore=True
		file_list={}
		author=file['author']
		for commiter in file['commiters']:
			if commiter['commits']>1:
				if commiter_list.has_key(commiter['login']):
					pass
				else:
					commiter_list[commiter['login']]={'num':num,'FA':0,'DL':0,'AC':0}
					name_list.append(commiter['login'])
					num+=1
				if cemaphore:
					file_list[commiter['login']]=commiter_list[commiter['login']]['num']
					cemaphore=False
				else:
					for login in file_list:
						if commiter_list[commiter['login']]['num']<file_list[login]:
							one=commiter_list[commiter['login']]['num']
							two=file_list[login]
						else:
							one=file_list[login]
							two=commiter_list[commiter['login']]['num']

						Edges[(one,two)]={'one':one,'two':two,'size':1}
					file_list[commiter['login']]=commiter_list[commiter['login']]['num']

	table=[]
	for couple in Edges:
		table.append((Edges[couple]['one'],Edges[couple]['two']))


	Graph=ig.Graph(table, directed=False)

	Graph.vs["name"] = name_list

	layout = Graph.layout("kk")

	wi=1000

	visual_style = {}
	visual_style["vertex_size"] = 20
	visual_style["vertex_label"] = Graph.vs["name"]
	visual_style["layout"] = "kk"
	visual_style["bbox"] = (wi, wi)
	visual_style["margin"] = (wi/10)

	metrics={'data':table,'labels':name_list}

	metrics['max_degree']=Graph.vs.select(_degree = Graph.maxdegree())["name"]

	metrics['node_betweenness']=Graph.vs.select(_betweenness = max(Graph.betweenness()))['name']

	ebs = Graph.edge_betweenness()
	max_eb = max(ebs)
	edge_list=[]

	labels_links=[]

	for idx, eb in enumerate(ebs):
		labels_links.append(str((Graph.vs.select(Graph.es[idx].source)['name'],Graph.vs.select(Graph.es[idx].target)['name'])))
		labels_links.append(str((Graph.vs.select(Graph.es[idx].source)['name'],Graph.vs.select(Graph.es[idx].target)['name'])))
		if eb == max_eb:
			edge_list.append((Graph.vs.select(Graph.es[idx].source)['name'],Graph.vs.select(Graph.es[idx].target)['name']))
	metrics['edge_betweenness']=edge_list

	labels=list(Graph.vs['name'])
	N=len(labels)
	E=[e.tuple for e in Graph.es]
	layt=layout

	Xn=[layt[k][0] for k in range(N)]
	Yn=[layt[k][1] for k in range(N)]
	Xe=[]
	Ye=[]
	for e in Edges:
		Xe+=[layt[e[0]][0],layt[e[1]][0], None]
		Ye+=[layt[e[0]][1],layt[e[1]][1], None]

	trace1=Scatter(x=Xe,
				   y=Ye,
				   mode='lines',
				   name='Links',
				   line=Line(color='#9efbdd', width=1),
				   text=labels_links,
				   hoverinfo='text'
				   )
	trace2=Scatter(x=Xn,
				   y=Yn,
				   mode='markers',
				   name='Users',
				   marker=Marker(symbol='dot',
								 size=10,
								 color='#6A5ACD',
								 line=Line(color='rgb(50,50,50)', width=0)
								 ),
				   text=labels,
				   hoverinfo=''
				   )
	axis=dict(showline=False, # hide axis line, grid, ticklabels and  title
		  zeroline=False,
		  showgrid=False,
		  showticklabels=False,
		  title=''
		  )
	layout=Layout(title= "Network of contributers (if they worked on the same file and have more than one commit):",
		font= Font(size=12),
		showlegend=False,
		xaxis=XAxis(axis),
		yaxis=YAxis(axis),
		margin=Margin(
			l=40,
			r=40,
			b=85,
			t=100,
		),
		hovermode='closest',
		annotations=Annotations([
				Annotation(
				showarrow=False,
				text="",
				xref='paper',
				yref='paper',
				x=0,
				y=-0.1,
				xanchor='left',
				yanchor='bottom',
				font=Font(
				size=14
				)
				)
			]),
		)

	data=Data([trace1, trace2])


	metrics['layout']=layout
	metrics['data']=data


	return metrics
	

if __name__ == "__main__":

	if len(sys.argv)!=2:
		print '\033[91m'+"-------------\nError: expected 1 argument\nusage:\n      python "+sys.argv[0]+"  <file.json>\n-------------"+'\033[0m'
		quit()

	file=sys.argv[1]

	f = open(file, "rb")

	contribution(f.read())
