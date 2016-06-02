# -*- coding: utf-8 -*-
from igraph import *
import igraph as ig
import json, urllib2, sys


def contribution(file):
		
	# Degree of Authorship (DOA) = 3.293 + 1.098 ∗ FA + 0.164 ∗ DL − 0.321 ∗ ln(1 + AC )
	# first authorship (FA), number of deliveries (DL), number of acceptances (AC)

	data = []

	data = json.loads(file)

	fileName=data['repository']+".graph.svg"
	commiter_list={}
	name_list=[]
	Edges={}
	num=0
	for file in data['files']:
		cemaphore=True
		file_list={}
		author=file['author']
		for commiter in file['commiters']:
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

	# layout = Graph.layout("kk")
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
	for idx, eb in enumerate(ebs):
		if eb == max_eb:
			edge_list.append((Graph.vs.select(Graph.es[idx].source)['name'],Graph.vs.select(Graph.es[idx].target)['name']))
	metrics['edge_betweenness']=edge_list


	visual=True
	print fileName
	if visual:
		
		plot(Graph,fileName, **visual_style)

	return metrics
	

if __name__ == "__main__":

	if len(sys.argv)!=2:
		print '\033[91m'+"-------------\nError: expected 1 argument\nusage:\n      python "+sys.argv[0]+"  <file.json>\n-------------"+'\033[0m'
		quit()

	file=sys.argv[1]

	f = open(file, "rb")

	contribution(f.read())
