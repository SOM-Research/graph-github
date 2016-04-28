import igraph as ig

G = ig.Graph.Read_GML('Eurovision15.gml')

V=list(G.vs) 
G.vs.attributes()# list node attributes

labels=[v['label']  for v in V] 

G.es.attributes()# the edge attributes

E=[e.tuple for e in G.es]# list of edges
len(E)


ContestantLst=[G.vs[e[1]] for e in E]
Contestant=list(set([v['label'] for  v in ContestantLst]))
len(Contestant)

layt=G.layout('circular') #circular layout


L=len(layt)
layt[7]

Weights= map(int, G.es["weight"])


import numpy as np

def dist (A,B):
    return np.linalg.norm(np.array(A)-np.array(B))
dist(layt[0], layt[5])

Dist=[0, dist([1,0], 2*[np.sqrt(2)/2]), np.sqrt(2),
      dist([1,0],  [-np.sqrt(2)/2, np.sqrt(2)/2]), 2.0]
params=[1.2, 1.5, 1.8, 2.1]

def get_idx_interv(d, D):
    k=0
    while(d>D[k]): 
        k+=1
    return  k-1

class InvalidInputError(Exception):
    pass

def deCasteljau(b,t): 
    N=len(b) 
    if(N<2):
        raise InvalidInputError("The  control polygon must have at least two points")
    a=np.copy(b) #shallow copy of the list of control points 
    for r in range(1,N): 
        a[:N-r,:]=(1-t)*a[:N-r,:]+t*a[1:N-r+1,:]                             
    return a[0,:]

def BezierCv(b, nr=5):
    t=np.linspace(0, 1, nr)
    return np.array([deCasteljau(b, t[k]) for k in range(nr)]) 

import plotly.plotly as py
from plotly.graph_objs import *
import plotly

node_color=['rgba(0,51,181, 0.85)'  if v['label'] in Contestant else '#CCCCCC' for v in G.vs] 
line_color=['#FFFFFF'  if v['label'] in Contestant else 'rgb(150,150,150)' for v in G.vs]
edge_colors=['#d4daff','#84a9dd', '#5588c8', '#6d8acf']

Xn=[layt[k][0] for k in range(L)]
Yn=[layt[k][1] for k in range(L)]

lines=[]# the list of dicts defining   edge  Plotly attributes
edge_info=[]# the list of points on edges where  the information is placed

for j, e in enumerate(E):
    A=np.array(layt[e[0]])
    B=np.array(layt[e[1]])
    d=dist(A, B)
    K=get_idx_interv(d, Dist)
    b=[A, A/params[K], B/params[K], B]
    color=edge_colors[K]
    pts=BezierCv(b, nr=5)
    text=V[e[0]]['label']+' to '+V[e[1]]['label']+' '+str(Weights[j])+' pts'
    mark=deCasteljau(b,0.9)
    edge_info.append(Scatter(x=mark[0], 
                             y=mark[1], 
                             mode='markers', 
                             marker=Marker( size=0.5,  color=edge_colors),
                             text=text, 
                             hoverinfo='text'
                             )
                    )
    lines.append(Scatter(x=pts[:,0],
                         y=pts[:,1],
                         mode='lines',
                         line=Line(color=color, 
                                  shape='spline',
                                  width=Weights[j]/5#The  width is proportional to the edge weight
                                 ), 
                        hoverinfo='none' 
                       )
                )
    
trace2=Scatter(x=Xn,
           y=Yn,
           mode='markers',
           name='',
           marker=Marker(symbol='dot',
                         size=15, 
                         color=node_color, 
                         line=Line(color=line_color, width=0.5)
                         ),
           text=labels,
           hoverinfo='text',
           )

axis=dict(showline=False, # hide axis line, grid, ticklabels and  title
          zeroline=False,
          showgrid=False,
          showticklabels=False,
          title='' 
          )

def make_annotation(anno_text, y_coord):
    return Annotation(showarrow=False, 
                      text=anno_text,  
                      xref='paper',     
                      yref='paper',     
                      x=0,  
                      y=y_coord,  
                      xanchor='left',   
                      yanchor='bottom',  
                      font=Font(size=12)     
                     )

anno_text1='Blue nodes mark the countries that are both contestants and jury members'
anno_text2='Grey nodes mark the countries that are only jury members'
anno_text3='There is an edge from a Jury country to a contestant country '+\
           'if the jury country assigned at least one vote to that contestant'
width=800
height=850
title="A circular graph associated to Eurovision Song Contest, 2015<br>Data source:"+\
"<a href='http://www.eurovision.tv/page/history/by-year/contest?event=2083#Scoreboard'> [1]</a>"
layout=Layout(title= title,
              font= Font(size=12),
              showlegend=False,
              autosize=False,
              width=width,
              height=height,
              xaxis=XAxis(axis),
              yaxis=YAxis(axis),          
              margin=Margin(l=40,
                            r=40,
                            b=85,
                            t=100,
                          ),
              hovermode='closest',
              annotations=Annotations([make_annotation(anno_text1, -0.07), 
                                       make_annotation(anno_text2, -0.09),
                                       make_annotation(anno_text3, -0.11)]
                                     )
              )

data=Data(lines+edge_info+[trace2])
fig=Figure(data=data, layout=layout)
plotly.offline.plot(fig, filename='Eurovision-15')

