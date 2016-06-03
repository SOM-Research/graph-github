# -*- coding: utf-8 -*-
import igraph as ig
from igraph import *
import json, urllib2
from math import *
import plotly.plotly as py
from plotly.graph_objs import *
import plotly

def make_3d_graph(json_file):
	print '\033[4m'+'----Creating Graph:----'+'\033[0m'
	
	print "[extracting json]",

	data = [] # Will receive the content of json_file
	data = json.loads(json_file) # Loads content of the json file in python dictionary

	org=data['organisation'] #Getting informations of the file
	repo=data['repository']
	directory=data['directory']
	graph_type=data['type']

	max_1=data['max1'] #Getting the two maximum values. If graph_type is contribution, max1 is maximum contributers commit and max2 maximum file commits. If graph_type is comments, max1 is maximum comments for a user and max2 for an issue.
	max_2=data['max2']

	print '\033[92m'+" ok"+'\033[0m'

	print "[info]",
	graph_title="Network of "+graph_type+" in <b>"+org+"</b>'s <b>"+repo+'/'+directory+"</b>"
	graph_legend="<a href='https://github.com/"+org+'/'+repo+"/tree/master/"+directory+"'>Repository</a>"
	if directory=='': # If there is no directory. So the root of the project : ex bootstrap to examinate a specific directory (doc for exemple) user must write bootstrap/doc
		graph_title="Network of "+graph_type+" in <b>"+org+"</b>'s <b>"+repo+"</b>"
		graph_legend="<a href='https://github.com/"+org+'/'+repo+"/'>Repository</a>"

	N=len(data['nodes'])
	L=len(data['links'])

	Edges=[] # Will receive copples of nodes linked together. It's how igraph does
	labels_links=[]
	test=[]
	for link in data['links']:
		Edges.append((link['source'], link['target']))
		labels_links.append(str(link['value'])+" commits")
		labels_links.append(str(link['value'])+" commits")
		labels_links.append(str(link['value'])+" commits") # The 3D representation require for each link 3 "labels". Here I want to show on mouseover the number of commits or comments, so the three values are the same.


	G=ig.Graph(Edges, directed=False) # graph object


	#-------------------------------------------------
	# All the graph documentation on plotly web page 
	# https://plot.ly/python/3d-network-graph/       

	labels_1=[] # Name displayed
	group_1 =[] # Color of node
	value_1 =[] # Size of node
	labels_2 =[]
	group_2 =[]
	value_2 =[]
	nu=0 # Each node nu for users, nf for files or issues, will receive a unique id in the plotly setup attribution of labels
	nf=0


	if graph_type=='contribution':
		type_1='Contributors '
		type_2='Files '
		if max_1==0 and max_2==0:
			for node in data['nodes']:
				if node['type']=='user' and int(node['commits'])>max_1:
					max_1=int(node['commits'])
				elif int(node['commits'])>max_2:
					max_2=int(node['commits'])

		for node in data['nodes']:
		  if node['type']=='user':
			labels_1.append(node['login']+" ("+node['id']+") : "+node['commits']+" commits")
			nu+=1
			group_1.append(log(int(node['commits'])+1,20))
			value_1.append((int(node['commits'])*20/max_1)+10)
		  else:
			labels_2.append(node['name']+" ("+node['type']+" ) : "+node['commits']+" commits")
			nf+=1
			group_2.append(1)
			value_2.append((int(node['commits'])*20/max_2)+8)


	elif graph_type=='comments':
		type_1='Participants '
		type_2='Issues '
		if max_1==0 and max_2==0:
			for node in data['nodes']:
				if node['type']=='commenter' and int(node['comments'])>max_1:
					max_1=int(node['comments'])
				elif int(node['comments'])>max_2:
					max_2=int(node['comments'])

		for node in data['nodes']:
		  if node['type']=='commenter':
			labels_1.append(node['login']+" ("+node['id']+") : "+node['comments']+" comments")
			nu+=1
			group_1.append(log(int(node['comments'])+1,20))
			value_1.append((int(node['comments'])*40/max_1)+10)
		  else:
			labels_2.append(node['type']+" ("+node['number']+" ) : "+node['comments']+" comments")
			nf+=1
			group_2.append(1)
			value_2.append((int(node['comments'])*20/max_2)+8)


	print '\033[92m'+" ok"+'\033[0m'
	print "[position]",
	layt=G.layout('kk', dim=3) 

	Xnf=[layt[k][0] for k in range(nf)]# x-coordinates of nodes
	Ynf=[layt[k][1] for k in range(nf)]# y-coordinates
	Znf=[layt[k][2] for k in range(nf)]# z-coordinates


	Xnu=[layt[nf+k][0] for k in range(nu)]# x-coordinates of nodes
	Ynu=[layt[nf+k][1] for k in range(nu)]# y-coordinates
	Znu=[layt[nf+k][2] for k in range(nu)]# z-coordinates


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
	print '    trace1', len(Xnu)
	trace2=Scatter3d(x=Xnu,
				   y=Ynu,
				   z=Znu,  
				   mode='markers',
				   name=type_1+str(nu),
				   marker=Marker(symbol='dot',
								 size=value_1, 
								 color=group_1, 
								 colorscale='Viridis',
								 line=Line(color='rgb(50,50,50)', width=0)
								 ),
				   text=labels_1,
				   hoverinfo='text'
				   )
	print '    trace2', len(Xnf),'\033[0m'
	trace3=Scatter3d(x=Xnf,
				   y=Ynf,
				   z=Znf,  
				   mode='markers',
				   name=type_2+str(nf),
				   marker=Marker(symbol='square',
								 size=value_2, 
								 color='#0074D9', 
								 colorscale='Viridis',
								 line=Line(color='rgb(50,50,50)', width=0)
								 ),
				   text=labels_2,
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

	data=Data([trace1, trace2, trace3])
	
	

	print '\033[92m'+" ok"+'\033[0m'

	print "[terminated]", '\033[0m'

	# return the data and the layout to JS

	return layout, data


	
if __name__ == "__main__":

	if len(sys.argv)!=2:
		print '\033[91m'+"-------------\nError: expected 1 argument\nusage:\n      python "+sys.argv[0]+"  <file.json>\n-------------"+'\033[0m'
		quit()

	jsonfile=sys.argv[1]
	f = open(jsonfile, "rb") # Opening the given file as json

	layout, data = make_3d_graph(f.read()) # Creating graph object

	#----------Displaying the graph---------
	fig=Figure(data=data, layout=layout) 
	plotly.offline.plot(fig, filename=jsonfile[:-5]+".html")
