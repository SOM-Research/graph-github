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
	Edges=[]
	num=0
	for file in data['files']:
		# print file['name']
		cemaphore=True
		logins=[]
		for commiter in file['commiters']:
			if commiter_list.has_key(commiter['login']):
				pass
				# print '('+commiter['login']+' already in list)'
			else:
				commiter_list[commiter['login']]=num
				name_list.append(commiter['login'])
				# print '('+commiter['login']+' added to the list) '+str(num)
				num+=1
			if cemaphore:
				logins.append(commiter_list[commiter['login']])
				# print '    '+commiter['login']+' added '+str(commiter_list[commiter['login']])
				cemaphore=False
			else:
				for x in xrange(0,len(logins)):
					Edges.append((commiter_list[commiter['login']],logins[x]))
					# print commiter_list[commiter['login']],logins[x]
					logins.append(commiter_list[commiter['login']])
					# print '    '+commiter['login']+' added '+str(commiter_list[commiter['login']])


	Graph=ig.Graph(Edges, directed=False)

	Graph.vs["name"] = name_list

	layout = Graph.layout("kk")

	visual_style = {}
	visual_style["vertex_size"] = 20
	visual_style["vertex_label"] = Graph.vs["name"]
	visual_style["layout"] = layout
	visual_style["bbox"] = (3200, 3200)
	visual_style["margin"] = 400

	plot(Graph, 'graph.png', **visual_style)



if __name__ == "__main__":

	if len(sys.argv)!=2:
		print '\033[91m'+"-------------\nError: expected 1 argument\nusage:\n      python "+sys.argv[0]+"  <file.json>\n-------------"+'\033[0m'
		quit()

	file=sys.argv[1]

	contribution(file)
