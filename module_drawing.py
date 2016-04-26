# -*- coding: utf-8 -*-

import igraph as ig
import json
import urllib2

import time
import sys

data = []

if __name__ == "__main__":
	
	# req = urllib2.Request("https://raw.githubusercontent.com/plotly/datasets/master/miserables.json")
	# opener = urllib2.build_opener()
	# f = opener.open(req)
	if len(sys.argv)<2:
		print "Error: expected an argument\nusage:\n      python "+sys.argv[0]+"  file.json\n"
		quit()
	t0=time.time()
	temp=sys.argv[1].split('-',1)
	org=temp[0]
	repo=temp[1]
	directory=''

	f = open(org+"-"+repo, "rb")

	max_user_commit=0
	max_file_commit=0

else:

	import shared_data

	t0=shared_data.time
	org=shared_data.org
	repo=shared_data.repo
	directory=shared_data.directory

	f = open(org+"-"+repo+".json", "rb")

	max_user_commit=shared_data.max_user_commit
	max_file_commit=shared_data.max_file_commit



data = json.loads(f.read())


N=len(data['nodes'])

L=len(data['links'])
Edges=[]
labels_links=[]
for link in data['links']:
	Edges.append((link['source'], link['target']))
	labels_links.append(link['value'])
	labels_links.append(link['value'])
	labels_links.append(link['value'])


# Edges=[(data['links'][k]['source'], data['links'][k]['target']) for k in range(L)]

G=ig.Graph(Edges, directed=False)


print '----Graph:----\n',G


##################################################
# All the graph documentation on plotly web page #
# https://plot.ly/python/3d-network-graph/       #
##################################################


labels_file=[]
group_file=[]
commits_file=[]
labels_user=[]
group_user=[]
commits_user=[]
nu=0
nf=0

if max_user_commit==0 and max_file_commit==0:
	for node in data['nodes']:
	    if node['type']=='user' and int(node['commits'])>max_user_commit:
	    	max_user_commit=int(node['commits'])
	    elif int(node['commits'])>max_file_commit:
	    	max_file_commit=int(node['commits'])



for node in data['nodes']:
    if node['type']=='user':
    	labels_user.append(node['login']+" ("+node['id']+") : "+node['commits']+" commits")
    	nu+=1
    	group_user.append(node['group'])
    	commits_user.append((int(node['commits'])*80/max_user_commit)+8)
    else:
    	labels_file.append(node['name']+" ("+node['type']+" ) : "+node['commits']+" commits")
    	nf+=1
    	group_file.append(node['group'])
    	commits_file.append((int(node['commits'])*50/max_file_commit)+8)


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



import plotly.plotly as py
from plotly.graph_objs import *
import plotly

trace1=Scatter3d(x=Xe,
               y=Ye,
               z=Ze,
               mode='lines',
               name='Links',
               line=Line(color='rgb(185,185,185)', width=0.8),
               text=labels_links,
               hoverinfo='text'
               )
trace2=Scatter3d(x=Xnu,
               y=Ynu,
               z=Znu,  
               mode='markers',
               name='Contributors : '+str(nu),
               marker=Marker(symbol='dot',
                             size=commits_user, 
                             color=commits_user, 
                             colorscale='Viridis',
                             line=Line(color='rgb(50,50,50)', width=0.5)
                             ),
               text=labels_user,
               hoverinfo='text'
               )
trace3=Scatter3d(x=Xnf,
               y=Ynf,
               z=Znf,  
               mode='markers',
               name='Files : '+str(nf),
               marker=Marker(symbol='square',
                             size=commits_file, 
                             color=group_file, 
                             colorscale='Viridis',
                             line=Line(color='rgb(50,50,50)', width=0.5)
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

execution_time = time.time() - t0

layout = Layout(
         title="Network of contributors (committers) in "+org+"'s project /"+repo+"/"+directory+" (generated in "+str(execution_time)+" sec)", 
         width=900,
         height=900,
         showlegend=True,
         scene=Scene(  
         xaxis=XAxis(axis),
         yaxis=YAxis(axis), 
         zaxis=ZAxis(axis), 
        ),
     margin=Margin(
        t=100
    ),
    hovermode='closest',
    annotations=Annotations([
           Annotation(
           showarrow=False, 
            text="Data source: <a href='https://github.com/"+org+"/"+repo+"'>[1]</a>",
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
fig=Figure(data=data, layout=layout)

plotly.offline.plot(fig, filename=org+"-"+repo+".html")
