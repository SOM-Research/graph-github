from igraph import *
import igraph as ig
import cairocffi as cairo
import json, urllib2

# g = Graph([(0,1), (0,2), (2,3), (3,4), (4,2), (2,5), (5,0), (6,3), (5,6)])

# g.vs["name"] = ["Alice", "Bob", "Claire", "Dennis", "Esther", "Frank", "George"]
# g.vs["age"] = [25, 31, 18, 47, 22, 23, 50]
# g.vs["gender"] = ["f", "m", "f", "m", "f", "m", "m"]
# g.es["is_formal"] = [False, False, True, True, True, False, True, False, False]

# g["date"] = "2009-01-10"

# print g.degree(6)

# print g.vs.select(_degree = g.maxdegree())["name"]

# print g.vs.select(age_lt=30)

# g.vs["label"] = g.vs["name"]
# color_dict = {"m": "blue", "f": "pink"}
# g.vs["color"] = [color_dict[gender] for gender in g.vs["gender"]]

# visual_style = {}
# visual_style["vertex_size"] = 20
# visual_style["vertex_color"] = [color_dict[gender] for gender in g.vs["gender"]]
# visual_style["vertex_label"] = g.vs["name"]
# visual_style["edge_width"] = [1 + 2 * int(is_formal) for is_formal in g.es["is_formal"]]
# visual_style["layout"] = layout
# visual_style["bbox"] = (300, 300)
# visual_style["margin"] = 20

# plot(g, "graph.svg", **visual_style)


data = []
fileName='twbs-bootlint.json'

f = open(fileName, "rb")
data = json.loads(f.read())

commiter_list={}
Edges=[]
num=0
for file in data['files']:
	cemaphore=True
	logins=[]
	for commiter in file['commiters']:
		if commiter_list.has_key(commiter['login']):
			pass
		else:
			commiter_list[commiter['login']]=num
			num+=1
		if cemaphore:
			# it's the first committer nothing to do, just remeber his login
			# logins.append(int(commiter['num'].encode('ascii', 'ignore')))
			logins.append(commiter_list[commiter['login']])
			cemaphore=False
		else:
			for x in xrange(0,len(logins)):
				Edges.append((commiter_list[commiter['login']],logins[x]))
	
	# Edges.append((link['source'], link['target']))

print Edges

G=ig.Graph(Edges, directed=False)

# for user in commiter_list:
# 	G.vs["name"].append(user[name])

layout = G.layout("kk")

plot(G, layout = layout)
