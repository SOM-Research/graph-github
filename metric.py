# -*- coding: utf-8 -*-
import igraph as ig
import json, urllib2, sys, math

import plotly as py
from plotly.graph_objs import *


def contribution(file):

	data = []

	data = json.loads(file)


	#-----------------------------------------------
	# Getting the nodes of the 3D graph (contribution)
	print '\033[4m'+'----Creating 3DGraph of contribution:----'+'\033[0m'
	print "[extracting json]",

	org=data['organisation'] #Getting informations of the file
	repo=data['repository']
	directory=data['directory']
	graph_type='contribution'


	Edges=[]
	user_list={}
	labels_links=[]
	labels_user=[] # Name displayed
	color_user =[] # Color of node
	size_user =[] # Size of node
	labels_file =[]
	size_file =[]
	nu=0 # Each node nu for users, nf for files or issues, will receive a unique id in the plotly setup attribution of labels
	nf=0
	max_size_user=0
	max_size_file=0

	for file in data['files']:
		nu+=1
		if int(file['commits'])>int(max_size_file): # I don't know why but without parsing to int, they are unicode objects and not integer...
			max_size_file=file['commits']
		for commiter in file['commiters']:
			if commiter['total-commits']>max_size_user:
				max_size_user=commiter['total-commits']

	for file in data['files']:
		for commiter in file['commiters']:
			if user_list.has_key(commiter['login']):
				Edges.append((nf,user_list[commiter['login']]))
			else:
				user_list[commiter['login']]=nu
				Edges.append((nf,nu))
				labels_user.append(commiter['login']+" ("+str(commiter['id'])+") : "+str(commiter['total-commits'])+" commits")
				color_user.append(math.log(int(commiter['total-commits'])+1,20))
				size_user.append((int(commiter['total-commits'])*20/max_size_user)+10)
				nu+=1
			labels_links.append(str(commiter['file-commits'])+" commits")
			labels_links.append(str(commiter['file-commits'])+" commits")
			labels_links.append(str(commiter['file-commits'])+" commits")
		labels_file.append(file['name']+" ("+file['type']+" ) : "+str(file['commits'])+" commits")
		size_file.append((int(file['commits'])*20/int(max_size_file))+8)
		nf+=1
	print '\033[92m'+" ok"+'\033[0m'
	#-----------------------------------------------



	Graph=ig.Graph(Edges, directed=False) # Create the graph object

	layout = Graph.layout("kk", dim=3) #Graph layout


	#-----------------------------------------------
	# Plotly layout
	print "[info]",
	graph_title="Network of "+graph_type+" in <b>"+org+"</b>'s <b>"+repo+'/'+directory+"</b>"
	graph_legend="<a href='https://github.com/"+org+'/'+repo+"/tree/master/"+directory+"'>Repository</a>"
	if directory=='': # If there is no directory. So the root of the project : ex bootstrap to examinate a specific directory (doc for exemple) user must write bootstrap/doc
		graph_title="Network of "+graph_type+" in <b>"+org+"</b>'s <b>"+repo+"</b>"
		graph_legend="<a href='https://github.com/"+org+'/'+repo+"/'>Repository</a>"

	N=nu
	E=[e.tuple for e in Graph.es]
	layt=layout

	print '\033[92m'+" ok"+'\033[0m'
	print "[position]",

	Xnf=[layt[k][0] for k in range(nf)]# x-coordinates of nodes
	Ynf=[layt[k][1] for k in range(nf)]# y-coordinates
	Znf=[layt[k][2] for k in range(nf)]# z-coordinates


	Xnu=[layt[nf+k][0] for k in range(nu-nf)]# x-coordinates of nodes
	Ynu=[layt[nf+k][1] for k in range(nu-nf)]# y-coordinates
	Znu=[layt[nf+k][2] for k in range(nu-nf)]# z-coordinates


	Xe=[]
	Ye=[]
	Ze=[]
	for e in Edges:
		Xe+=[layt[e[0]][0],layt[e[1]][0], None]# x-coordinates of edge ends
		Ye+=[layt[e[0]][1],layt[e[1]][1], None]  
		Ze+=[layt[e[0]][2],layt[e[1]][2], None]


	print '\033[92m'+" ok"+'\033[0m'

	print "[draw]"+'\033[95m'
	print '    links', len(Xe)/3

	trace1=Scatter3d(x=Xe,
				   y=Ye,
				   z=Ze,
				   mode='lines',
				   name='Links',
				   line=Line(color='#D3D3F9', width='1'),
				   text=labels_links,
				   hoverinfo='text'
				   )
	
	print '    users', len(Xnu)

	trace2=Scatter3d(x=Xnu,
				   y=Ynu,
				   z=Znu,  
				   mode='markers',
				   name='Contributors '+str(nu),
				   marker=Marker(symbol='dot',
								 size=size_user, 
								 color=color_user, 
								 colorscale='Viridis',
								 line=Line(color='rgb(50,50,50)', width=0)
								 ),
				   text=labels_user,
				   hoverinfo='text'
				   )

	print '    files', len(Xnf),'\033[0m'

	trace3=Scatter3d(x=Xnf,
				   y=Ynf,
				   z=Znf,  
				   mode='markers',
				   name='Files '+str(nf),
				   marker=Marker(symbol='square',
								 size=size_file, 
								 color='#0074D9', 
								 colorscale='Viridis',
								 line=Line(color='rgb(50,50,50)', width=0)
								 ),
				   text=labels_file,
				   hoverinfo='text'
				   )

	axis=dict(showbackground=False,
			  showline=False,  
			  zeroline=False,
			  showgrid=False,
			  showticklabels=False,
			  title='' 
			  )

	layout = Layout(
			 title=graph_title, 
			 showlegend=True,
			 scene=Scene(  
				 xaxis=XAxis(axis,showspikes=False),
				 yaxis=YAxis(axis,showspikes=False), 
				 zaxis=ZAxis(axis,showspikes=False), 
			),
		 margin=Margin(
			t=100
		),
		hovermode='closest',
		annotations=Annotations([
			   Annotation(
			   showarrow=False, 
				text=graph_legend,
				xref='paper',     
				yref='paper',     
				x=0,  
				y=0.1,  
				xanchor='left',   
				yanchor='bottom',  
				font=Font(
				size=14 
				)     
				)
			]),    )

	print '\033[92m'+" ok"+'\033[0m'

	datas=Data([trace1, trace2, trace3])


	metrics={}

	metrics['layout_3D']=layout
	metrics['data_3D']=datas

	print "[terminated]", '\033[0m'
	#-----------------------------------------------















	#-----------------------------------------------
	# Getting the nodes of the 2D graph (Who knows who)
	print '\033[4m'+'----Creating 2DGraph of users connexion:----'+'\033[0m'
	print "[extracting json]",
	commiter_list={} # Will receive the commiters already treated
	name_list=[] # To store the name as labels in the same order we treat the nodes
	Edges={} # Will store copples (x,y) and make sure it's the same as (y,x) so the graph is undirected
	num=0 # To assign a unique id to each node

	for file in data['files']:
		cemaphore=True
		file_list={}
		author=file['author']
		for commiter in file['commiters']:
			if commiter['total-commits']>1:
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
	print '\033[92m'+" ok"+'\033[0m'
	#-----------------------------------------------



	Graph=ig.Graph(table, directed=False) # Create the graph object

	Graph.vs["name"] = name_list #To associate name to nodes

	layout = Graph.layout("kk") #Graph layout
	


	#-----------------------------------------------
	# To see the igraph as png
	# Juste write if True: to display it ;)
	if False:

		wi=1000
		visual_style = {}
		visual_style["vertex_size"] = 20
		visual_style["vertex_label"] = Graph.vs["name"]
		visual_style["layout"] = "kk"
		visual_style["bbox"] = (wi, wi)
		visual_style["margin"] = (wi/10)

		ig.plot(Graph, **visual_style)
	#-----------------------------------------------


	#-----------------------------------------------
	print "[info]",
	# The metrics calculation

	# Degree of Authorship (DOA) = 3.293 + 1.098 ∗ FA + 0.164 ∗ DL − 0.321 ∗ ln(1 + AC )
	# first authorship (FA), number of deliveries (DL), number of acceptances (AC)

	metrics['max_degree']=Graph.vs.select(_degree = Graph.maxdegree())["name"]
	
	if len(metrics['max_degree'])==len(Graph.vs['name']):
		metrics['max_degree']=['No maximum !','They all have same value']
	
	metrics['node_betweenness']=Graph.vs.select(_betweenness = max(Graph.betweenness()))['name']
	
	if len(metrics['node_betweenness'])==len(Graph.vs['name']):
		metrics['node_betweenness']=['No maximum !','They all have same value']
	
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
	
	if len(metrics['edge_betweenness'])==len(ebs):
		metrics['edge_betweenness']=['No maximum !','They all have same value']
	#-----------------------------------------------

	print '\033[92m'+" ok"+'\033[0m'
	print "[position]",

	#-----------------------------------------------
	# Plotly layout
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

	print '\033[92m'+" ok"+'\033[0m'

	print "[draw]"+'\033[95m'
	print '    links', len(Xe)/2

	trace1=Scatter(x=Xe,
				   y=Ye,
				   mode='lines',
				   name='Links',
				   line=Line(color='#9efbdd', width=1),
				   text=labels_links,
				   hoverinfo='text'
				   )
	print '    users', len(Xn)
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
	layout=Layout(title= "Network of contributers<br>(they worked same file and have more than 1 commit):",
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

	datas=Data([trace1, trace2])

	print '\033[92m'+" ok"+'\033[0m'

	metrics['layout_metrics']=layout
	metrics['data_metrics']=datas
	#-----------------------------------------------
	print "[terminated]", '\033[0m'


	# We return a dictionnary that contain the metrics and the two graphs (3d & 2d)
	return metrics
	




if __name__ == "__main__":

	if len(sys.argv)!=2:
		print '\033[91m'+"-------------\nError: expected 1 argument\nusage:\n      python "+sys.argv[0]+"  <file.json>\n-------------"+'\033[0m'
		quit()

	file=sys.argv[1]

	f = open(file, "rb")

	result = contribution(f.read()) # Creating graph object

	#----------Displaying the graph---------

	fig=Figure(data=result['data_3D'], layout=result['layout_3D']) 

	py.offline.plot(fig, filename=file+".3DMetrics.html")

