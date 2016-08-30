import initialize
import numpy as np
import random
import jpype
from jpype import *
from random import randint

startJVM(jpype.getDefaultJVMPath(), "-ea", "-Djava.class.path=/Users/cepardot/GoogleDrive/EP/Stage/stackoverflowanalysis-188/db/CoreJointComplexity/bin")
testPkg = JPackage('com').alblf.jc
Test = testPkg.SuffixTree
numText=len(df.Text[df.TypeId==2])-2

def greedy(radius,points,df):
    #cluster_centers=[]
    cluster_center=points[0]
    data=points[1]
    clusters=[]
    new_cluster_centers=[]
    
    ind=0
    #for i in range(len(cluster_centers)):
    new_cluster_centers.append([cluster_center,[]])
    #print(new_cluster_centers)
    for i in data:
        if i!=cluster_center:
            #a=Test(df.Text[df.TypeId==2][i])
            a=Test(df.Text[df.TypeId==2].iloc[i])
            #if not cluster_centers:
            #    cluster_centers.append(i)
            #    clusters.append(ind)
            #    ind+=1
            #else:
            dist=[]
            taken=False
            for j in range(len(new_cluster_centers)):
                #b=Test(df.Text[df.TypeId==2][center])
                b=Test(df.Text[df.TypeId==2].iloc[new_cluster_centers[j][0]])
                similarity=a.normalizedJC(b)
                similarity=(similarity/0.005 if similarity<0.005 else 1)
                if similarity<radius:
                    cluster=new_cluster_centers[j][0]
                    clusters.append(cluster)
                    ###TODO###
                    new_cluster_centers[j][1].append(i)
                    taken=True
                    break
                    #dist.append(similarity)
                    #if np.min(dist)<radius:
                    #    cluster=np.argmin(dist)
                    #    clusters.append(cluster)
                
            if not taken:
                new_cluster_centers.append([i,[]])
                #print(new_cluster_centers)
                clusters.append(i)
                
    return new_cluster_centers, clusters

def build_tree(df,n):
    tree=[]
    radius=1
    number_points=len(df.Text[df.TypeId==2])
    data=list(range(number_points))
    cluster_center=0#randint(0,number_points)
    points=[[cluster_center,data]]
    for i in range(n):
        new_points=[]
        for point in points:
            new_cluster_centers, clusters=greedy(radius,point,df)
            tree.append([point[0],[child[0] for child in new_cluster_centers]])
            new_points=new_points+new_cluster_centers
        points=new_points
        radius=radius*0.5
        if len(set(clusters))==len(clusters):
            break
    return tree

#Returns the degree distribution of the tree built by build_tree.
def calculate_degrees(df, n):
    tree=build_tree(df,n)
    print tree
    degrees=[]
    for level in tree:
        #print(level)
        degrees.append(len(level[1]))
    return degrees
