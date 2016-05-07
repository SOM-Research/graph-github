from igraph import *
import igraph as ig
import cairocffi as cairo
import json, urllib2, sys


def contribution(file):
		

	data = []

	f = open(file, "rb")
	data = json.loads(f.read())

	commiter_list={}
	name_list=[]
	Edges={}
	num=0
	for file in data['files']:
		cemaphore=True
		file_list={}
		for commiter in file['commiters']:
			if commiter_list.has_key(commiter['login']):
				pass
			else:
				commiter_list[commiter['login']]=num
				name_list.append(commiter['login'])
				num+=1
			if cemaphore:
				file_list[commiter['login']]=commiter_list[commiter['login']]
				cemaphore=False
			else:
				for login in file_list:
					Edges[(commiter_list[commiter['login']],file_list[login])]={'one':commiter_list[commiter['login']],'two':file_list[login],'size':1}
				file_list[commiter['login']]=commiter_list[commiter['login']]

	table=[]
	for couple in Edges:
		table.append((Edges[couple]['one'],Edges[couple]['two']))

	Graph=ig.Graph(table, directed=False)

	Graph.vs["name"] = name_list

	# layout = Graph.layout("kk")

	visual_style = {}
	visual_style["vertex_size"] = 20
	visual_style["vertex_label"] = Graph.vs["name"]
	visual_style["layout"] = "kk"
	visual_style["bbox"] = (800, 800)
	visual_style["margin"] = 80

	plot(Graph, 'graph.svg', **visual_style)



if __name__ == "__main__":

	if len(sys.argv)!=2:
		print '\033[91m'+"-------------\nError: expected 1 argument\nusage:\n      python "+sys.argv[0]+"  <file.json>\n-------------"+'\033[0m'
		quit()

	file=sys.argv[1]

	contribution(file)
