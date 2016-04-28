# -*- coding: utf-8 -*-
import igraph as ig
import json, urllib2
import time, sys


print '\033[4m'+'----Graph:----'+'\033[0m'

print "[parsing json]",

data = []

if __name__ == "__main__":

	if len(sys.argv)<2:
		print '\033[91m'+"\n----Error----: expected an argument\nusage:\n      python "+sys.argv[0]+"  file.json\n-------------\n"+'\033[0m'
		quit()
	t0=time.time()
	fileName=sys.argv[1]
	temp=sys.argv[1].split('-',1)
	org=temp[0]
	path=temp[1].split(">",1)
	repo=path[0]
	directory=path[1].split('.')[0]

	f = open(fileName, "rb")

	max_1=0
	max_2=0

else:

	import shared_data as sh

	fileName=sh.fileName
	t0=sh.time
	org=sh.org
	repo=sh.repo
	directory=sh.directory
  graph_type=sh.graph_type

	f = open(fileName, "rb")

	max_1=sh.max_1
	max_2=sh.max_2


data = json.loads(f.read())

print '\033[92m'+" ok"+'\033[0m'


print "[info]",

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


if max_1==0 and max_2==0:
	for node in data['nodes']:
	    if node['type']=='user' and int(node['commits'])>max_1:
	    	max_1=int(node['commits'])
	    elif int(node['commits'])>max_2:
	    	max_2=int(node['commits'])



for node in data['nodes']:
    if node['type']=='user':
    	labels_user.append(node['login']+" ("+node['id']+") : "+node['commits']+" commits")
    	nu+=1
    	group_user.append(node['group'])
    	commits_user.append((int(node['commits'])*80/max_1)+8)
    else:
    	labels_file.append(node['name']+" ("+node['type']+" ) : "+node['commits']+" commits")
    	nf+=1
    	group_file.append(node['group'])
    	commits_file.append((int(node['commits'])*50/max_2)+8)
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

import plotly.plotly as py
from plotly.graph_objs import *
import plotly

print "[draw]"+'\033[95m'
print '    links', len(Xe)/3
trace1=Scatter3d(x=Xe,
               y=Ye,
               z=Ze,
               mode='lines',
               name='Links',
               line=Line(color='rgb(185,185,185)', width=0.8),
               text=labels_links,
               hoverinfo='text'
               )
print '    contributors', len(Xnu)
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
print '    files', len(Xnf),'\033[0m'
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
         title="Network of contributors in <b>"+org+"</b>'s project <b>"+repo+'/'+directory+"</b> (generated in "+str(execution_time)[:-8]+" sec)", 
         width=1200,
         height=900,
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
            text="<a href='https://github.com/"+org+'/'+repo+"/tree/master/"+directory+"'>Repository</a>",
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

plotly.offline.plot(fig, filename=fileName[:-5]+".html")

print '\033[92m'+" ok"+'\033[0m'

print "[Finished]", '\033[95m',execution_time, 'sec'+'\033[0m'
