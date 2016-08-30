import csv
import numpy as np
import pandas as pd
import nltk
import re
import os
import codecs
from sklearn import feature_extraction
#import mpld3
import sqlite3
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.externals import joblib
import random


def runquery(c,query):
  c.execute(query)
  return c.fetchall()
def init_db():
  conn=sqlite3.connect('travel.db')
  #conn=sqlite3.connect('/Users/cepardot/GoogleDrive/EP/Stage/stackoverflowanalysis-188/db/travel.db')
#conn=sqlite3.connect('/Volumes/DavidPardo/Stage/math.db')

  c=conn.cursor()

  result=runquery(c,'''SELECT ParentId, Id, PostTypeId, Body, OwnerUserId, AnswerCount, AcceptedAnswerId, Score FROM posts;''') #ParentId<10000 OR Id<10000;''')
  result2=runquery(c,'''SELECT PostId, Id, UserId FROM comments;''')
  result3=runquery(c,'''SELECT PostId, Id, UserId, CreationDate FROM votes;''')
  ParentId=[]
  Id=[]
  TypeId=[]
  Text=[]
  UserId=[]
  AnswerCount=[]
  AcceptedAnswer=[]
  Score=[]
  for row in result:
    ParentId.append(row[0])
    Id.append(row[1])
    TypeId.append(row[2])
    UserId.append(row[4])
    AnswerCount.append(row[5])
    AcceptedAnswer.append(row[6])
    Score.append(row[7])
    
    
    
    
    #To eliminate code (latex)
    sample=re.sub(r'<pre>(.|\n)*?<\/pre>',r' ',row[3])
    sample=re.sub('((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?]))', ' ', sample)
    
    
    
    #To eliminate URL's
    
    #sample=re.sub('<a href="?\'?([^"\'>]*)', ' ', sample)
    sample=re.sub('<[^<]+?>', ' ', sample)
    
    
    sample=re.sub(r'$(.*?)$',r' ',sample)
    sample=re.sub(r'[^a-zA-Z ]', ' ', sample)
    # sample=re.sub(r'[?|$|.|!|{|}|\^|/]',r'',sample)
    # sample=re.sub(r"['|\\]",r' ',sample)
    # sample=re.sub(r'\w*\d\w*', r' ', sample)
    sample=re.sub(r" [a-zA-Z] ",r' ',sample)
    sample.encode('utf-8').strip()
    Text.append(sample)
    
  CParentId=[]
  CId=[]
  CUserId=[]
  for row in result2:
    CParentId.append(row[0])
    CId.append(row[1])
    CUserId.append(row[2])
    
  VParentId=[]
  VId=[]
  VUserId=[]
  VCreationDate=[]
  for row in result3:
    VParentId.append(row[0])
    VId.append(row[1])
    VUserId.append(row[2])
    VCreationDate.append(row[3])

  df = pd.DataFrame({'Id':Id,'ParentId':ParentId,'TypeId':TypeId,'Text':Text, 'UserId':UserId,'AnswerCount':AnswerCount,
                   'AcceptedAnswer':AcceptedAnswer,'Score':Score})

#df.set_value(df.loc[np.isnan(df.UserId)],UserId)=-2
  df.UserId.loc[np.isnan(df.UserId)]=-2
  df.UserId=df.UserId.astype(int)

  dfC = pd.DataFrame({'Id':CId,'ParentId':CParentId, 'UserId':CUserId})

  dfC.UserId.loc[np.isnan(dfC.UserId)]=-2
  dfC.UserId=dfC.UserId.astype(int)

  dfV = pd.DataFrame({'Id':VId,'ParentId':VParentId, 'UserId':VUserId, 'CreationDate':VCreationDate})

  dfV.UserId.loc[np.isnan(dfV.UserId)]=-2
  dfV.UserId=dfV.UserId.astype(int)
  return df, dfC, dfV
