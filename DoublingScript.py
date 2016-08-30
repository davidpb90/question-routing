#!/usr/local/bin/python
import matplotlib.pyplot as plt
import csv
import numpy as np
import pandas as pd
#import nltk
import re
import os
import codecs
#from sklearn import feature_extraction
#import mpld3
#import sqlite3
import random
conn=sqlite3.connect('/travel.db')
#conn=sqlite3.connect('/Users/cepardot/GoogleDrive/EP/Stage/stackoverflowanalysis-188/db/travel.db')
#conn=sqlite3.connect('/Volumes/DavidPardo/Stage/math.db')

c=conn.cursor()
def runquery(c,query):
  c.execute(query)
  return c.fetchall()
result=runquery(c,'''SELECT ParentId, Id, PostTypeId, Body, OwnerUserId, AnswerCount FROM posts WHERE Id<50000;''') #ParentId<10000 OR Id<10000;''')
result2=runquery(c,'''SELECT PostId, Id, UserId FROM comments WHERE PostId<5000;''')
result3=runquery(c,'''SELECT PostId, Id, UserId FROM votes WHERE PostId<5000;''')
ParentId=[]
Id=[]
TypeId=[]
Text=[]
UserId=[]
AnswerCount=[]
for row in result:
    ParentId.append(row[0])
    Id.append(row[1])
    TypeId.append(row[2])
    UserId.append(row[4])
    AnswerCount.append(row[5])
    
    
    
    
    #To eliminate code (latex)
    sample=re.sub(r'<pre>(.|\n)*?<\/pre>',r' ',row[3])
    sample=re.sub('((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', ' ', sample)
    
    
    
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
for row in result3:
    VParentId.append(row[0])
    VId.append(row[1])
    VUserId.append(row[2])

df = pd.DataFrame({'Id':Id,'ParentId':ParentId,'TypeId':TypeId,'Text':Text, 'UserId':UserId,'AnswerCount':AnswerCount})

df.UserId.loc[np.isnan(df.UserId)]=-2
df.UserId=df.UserId.astype(int)

dfC = pd.DataFrame({'Id':CId,'ParentId':CParentId, 'UserId':CUserId})

dfC.UserId.loc[np.isnan(dfC.UserId)]=-2
dfC.UserId=dfC.UserId.astype(int)

dfV = pd.DataFrame({'Id':VId,'ParentId':VParentId, 'UserId':VUserId})

dfV.UserId.loc[np.isnan(dfV.UserId)]=-2
dfV.UserId=dfV.UserId.astype(int)

#Given an user it returns the list of questions with which she has interacted in any way, as well as the ID of the 
#answers defining that interaction.

def find_questions_all(user,df,dfC,dfV):
    #Posts where the user has commented
    comments=set(dfC[dfC.UserId==user].ParentId)
    #Posts where the user has voted
    votes=set(dfV[dfV.UserId==user].ParentId)
    #Union of the 2 sets
    com_votes=list(comments.union(votes))
    
    
    answers1=df[np.logical_and(df.UserId==user, df.TypeId==2)]
    answersId=set(answers1.Id)
    #Id of posts where the user has voted, commented or which is an answer by the user
    ans_com_votes=answersId.union(com_votes)
    #ID of questions where the user has answered
    answers1=set(answers1.ParentId)
    #Parent ID of questions for which the user has voted or commented answers
    answers2=set(df[np.logical_and(df.Id.isin(com_votes),df.TypeId==2)].ParentId)
    #Union of both sets
    answers=answers1.union(answers2)
    #Questions that the user has voted or commented in
    questions1=set(df[np.logical_and(df.Id.isin(com_votes),df.TypeId==1)].Id)
   
    #Questions corresponding to all the answers
    questions2=set(df[np.logical_and(df.Id.isin(answers), df.AnswerCount>1)].Id)
    #Union of both sets
    questions=questions1.union(questions2)
    ans_com_votes=ans_com_votes.union(questions)
    return list(ans_com_votes), list(questions)

#Given an user it returns the list of questions with which she has interacted in any way except voting, as well as the ID of the 
#answers defining that interaction.
def find_questions_no_votes(user,df,dfC):
    #Posts where the user has commented
    comments=set(dfC[dfC.UserId==user].ParentId)
    #Posts where the user has voted
    #votes=set(dfV[dfV.UserId==user].ParentId)
    #Union of the 2 sets
    com_votes=list(comments)
    
    #ID of questions where the user has answered
    answers1=df[np.logical_and(df.UserId==user, df.TypeId==2)]
    answersId=set(answers1.Id)
    ans_com=answersId.union(com_votes)
    answers1=set(answers1.ParentId)
    #Parent ID of questions for which the user has voted or commented answers
    answers2=set(df[np.logical_and(df.Id.isin(com_votes),df.TypeId==2)].ParentId)
    #Union of both sets
    answers=answers1.union(answers2)
    #Questions that the user has voted or commented in
    questions1=set(df[np.logical_and(df.Id.isin(com_votes),df.TypeId==1)].Id)
   
    #Questions corresponding to all the answers
    questions2=set(df[np.logical_and(df.Id.isin(answers), df.AnswerCount>1)].Id)
    #Union of both sets
    questions=questions1.union(questions2)
    ans_com=ans_com.union(questions)
    return list(ans_com), list(questions)

#Given an user it returns the list of questions which she has answered, as well as the ID of the respective
#answers.
def find_questions_answers(user,df):
    
    #ID of questions where the user has answered
    answers1=df[np.logical_and(df.UserId==user, df.TypeId==2)]
    answersId=set(answers1.Id)
    
    answers1=set(answers1.ParentId)
   
    #Parent ID of questions for which the user has voted or commented answers
    answers2=set(df[np.logical_and(df.Id.isin(com_votes),df.TypeId==2)].ParentId)
    #Union of both sets
    answers=answers1.union(answers2)
    
    
   
    #Questions corresponding to all the answers
    questions=set(df[np.logical_and(df.Id.isin(answers), df.AnswerCount>1)].Id)
    #Union of both sets
    answersId=answersId.union(questions)
    return list(answersId), list(questions)

#Given an user it returns the list of questions for which she has voted it or one of its answers, as well as the ID of the respective
#answers.
def find_questions_votes(user,df,dfV):
    
    #Posts where the user has voted
    votes=set(dfV[dfV.UserId==user].ParentId)
    
    
    
    #Parent ID of questions for which the user has voted answers
    questions1=set(df[np.logical_and(df.Id.isin(votes),df.TypeId==2)].ParentId)
    #Union of both sets
   
    #Questions that the user has voted or commented in
    questions2=set(df[np.logical_and(df.Id.isin(votes),df.TypeId==1)].Id)
   
    #Questions corresponding to all the answers
    #questions2=set(df[df.Id.isin(answers)].Id)
    #Union of both sets
    questions=questions1.union(questions2)
    votes=votes.union(questions)
    return list(votes), list(questions)

#Given a sequence it returns a list of the duplicated elements
def list_duplicates(seq):
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set( x for x in seq if x in seen or seen_add(x) )
    # turn the set into a list (as requested)
    return list( seen_twice )

#Given an user it returns the list of questions for which she has voted it or one of its answers at least twice, as well 
#as the ID of the respective
#answers.
def find_questions_more_votes(user,df,dfV):
    
    #Posts where the user has voted
    votes=set(dfV[dfV.UserId==user].ParentId)
    
    #Parent ID of questions for which the user has voted answers
    questions1=list(df[np.logical_and(df.Id.isin(votes),df.TypeId==2)].ParentId)
    #Union of both sets
   
    #Questions that the user has voted or commented in
    questions2=list(df[np.logical_and(df.Id.isin(votes),df.TypeId==1)].Id)
    questions =questions1+questions2
    questions=set(list_duplicates(questions))
    votes=votes.union(questions)
    return list(votes), list(questions)

#Given an user it returns the list of questions for which she has commented it or one of its answers, as well 
#as the ID of the respective answers.
def find_questions_comments(user,df,dfC):
    
    #Posts where the user has voted
    comments=set(dfC[dfC.UserId==user].ParentId)
    
    
    
    #Parent ID of questions for which the user has voted answers
    questions1=set(df[np.logical_and(df.Id.isin(comments),df.TypeId==2)].ParentId)
    #Union of both sets
   
    #Questions that the user has voted or commented in
    questions2=set(df[np.logical_and(df.Id.isin(comments),df.TypeId==1)].Id)
   
    #Questions corresponding to all the answers
    #questions2=set(df[df.Id.isin(answers)].Id)
    #Union of both sets
    questions=questions1.union(questions2)
    comments=comments.union(questions)
    return comments, list(questions)


#Given an user it returns the list of questions for which she has commenteded it or one of its answers at least twice, as well as 
#the ID of the respective answers.
def find_questions_more_comments(user,df,dfC,n):
    
    #Posts where the user has voted
    comments=set(dfC[dfC.UserId==user].ParentId)
    
    
    
    #Parent ID of questions for which the user has voted answers
    questions1=list(df[np.logical_and(df.Id.isin(comments),df.TypeId==2)].ParentId)
    #Union of both sets
   
    #Questions that the user has voted or commented in
    questions2=list(df[np.logical_and(df.Id.isin(comments),df.TypeId==1)].Id)
   
    questions =questions1+questions2
    questions=set(list_duplicates(questions))
    #Questions corresponding to all the answers
    #questions2=set(df[df.Id.isin(answers)].Id)
    #Union of both sets
    comments=comments.union(questions)
    
    return comments, set(questions)

#Given a set of questions, it returns the respective answerers.
def find_answerers(user,questions,df,dfC):
    answerers1=set(dfC[dfC.ParentId.isin(np.array(questions))].UserId)
    answerers2=set(df[df.ParentId.isin(np.array(questions))].UserId)
    answerers=list(answerers1.union(answerers2))
    if(user in answerers):
        answerers.remove(user)
    return answerers

#Given a list of questions and answerers it returns for each answerer a list of the users who have interacted in the 
#same questions, a list of this questions and the number of them.
def common_elements(questions, answerers,df,dfC):
    number_in_common=0
    user_in_common=-1
    in_common=[]
    common_questions=[]
    for answerer in answerers:
            
    #print(answerer)
        comments, questions_comments=find_questions_no_votes(answerer,df,dfC)
        new_questions=set(questions_comments)
        in_common=list(new_questions.intersection(set(questions)))
        number=len(in_common)
        if number>number_in_common:
            number_in_common=number
            common_questions=in_common
            user_in_common=answerer
            answerers.remove(answerer)
    return number_in_common, common_questions, user_in_common,answerers

def common_elements_old(questions, answerers,df):
    number_in_common=0
    user_in_common=-1
    in_common=[]
    common_questions=[]
    for answerer in answerers:
            
    #print(answerer)
        new_answers=df[np.logical_and(df.UserId==answerer, df.TypeId==2)]
            #new_answersId=answers.Id
        new_questions=set(new_answers.ParentId)
        in_common=list(new_questions.intersection(set(questions)))
        number=len(in_common)
        if number>number_in_common:
            number_in_common=number
            common_questions=in_common
            user_in_common=answerer
            answerers.remove(answerer)
    return number_in_common, common_questions, user_in_common,answerers

#Given a set of questions and a set of answerers, it returns for each user a list of the users whose interests cover 
# her set of interests, as well as the number of such users. 
def grow_cover(questions,answerers,total_cover,total_count,df,dfC):
    number_cover=[]
    cover=[]
    while(questions):
        
        number_in_common, common_questions, user_in_common,answerers=common_elements(questions, answerers,df,dfC)
        if(number_in_common==0):
            #print(questions)
            questions=[]
        else:
            cover.append(user_in_common)
            number_cover.append(number_in_common)
            for element in common_questions:
                questions.remove(element)
            
    total_cover.append(cover)
    total_count.append(len(cover))
    return total_cover, total_count

#It finds the cover for all users.
def find_cover(df,dfC,dfV):
    total_cover=[]
    total_count=[]
    i=0
    for user in set(df.UserId):
        if user!=-2:
            #print(i)
            i=i+1
            #questions=df[np.logical_and(df.UserId==user,df.TypeId==1)].Id
            votes, questions=find_questions_all(user,df,dfC,dfV)
    
            answerers=find_answerers(user,votes,df,dfC)
    
            total_cover,total_count=grow_cover(questions,answerers,total_cover,total_count,df,dfC)
        
    return total_cover,total_count

total_cover,total_count=find_cover(df,dfC,dfV)

#It returns the distributions of comments, votes, their difference and their ratio. 
def get_distributions(df,dfC,dfV):
    number_comments=[]
    number_votes=[]
    difference=[]
    division=[]
    for user in set(dfV.UserId).union(set(dfC.UserId)):
        if user!=-2:
            comments, questions_comments=find_questions_all(user,df,dfC,dfV)
            votes, questions_votes=find_questions_no_votes(user,df,dfC)
            number_comments.append(len(questions_comments))
            number_votes.append(len(questions_votes))
            difference.append(len(questions_votes)-len(questions_comments))
            if len(questions_votes)>0:
                division.append(len(questions_comments)*1.0/(1.0*len(questions_votes)))
    return number_comments, number_votes, difference, division

number_comments, number_votes, difference, division = get_distributions(df,dfC,dfV)

#It plots the comment distribution. 
def comments_distribution(number_comments):
    number_comments=np.array(number_comments)
    n, bins, patches=plt.hist(number_comments, bins=np.arange(number_comments.min(),20 ))#total_count.max()+1))
    # = plt.hist(x, 50, normed=1, facecolor='g', alpha=0.75)


    plt.xlabel('Number of comments')
    plt.ylabel('Number of Users')
    plt.title('Distribution of QL in the Travel dataset')
    #plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    #plt.axis([0, 200, 0, 250])
    plt.grid(True)
    plt.savefig('comments_distribution.pdf', bbox_inches='tight')
    #plt.show()
comments_distribution(number_comments)
#It plots the vote distribution. 
def votes_distribution(number_votes):
    number_votes=np.array(number_votes)
    n, bins, patches=plt.hist(number_votes, bins=np.arange(0, 20))#total_count.max()+1))
    # = plt.hist(x, 50, normed=1, facecolor='g', alpha=0.75)


    plt.xlabel('Number of votes')
    plt.ylabel('Number of Users')
    plt.title('Distribution of QR in the Travel dataset')
    #plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    #plt.axis([0, 200, 0, 250])
    plt.grid(True)
    plt.savefig('votes_distribution.pdf', bbox_inches='tight')
    # plt.show()
votes_distribution(number_votes)
#It plots the difference distribution. 
def difference_distribution(difference):
    difference=np.array(difference)
    n, bins, patches=plt.hist(difference, bins=np.arange(-20, 20))#total_count.max()+1))
    # = plt.hist(x, 50, normed=1, facecolor='g', alpha=0.75)


    plt.xlabel('Difference')
    plt.ylabel('Number of Users')
    plt.title('Distribution of the difference between QL and QR for Travel')
    #plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    #plt.axis([0, 200, 0, 250])
    plt.grid(True)
    plt.savefig('difference_distribution.pdf', bbox_inches='tight')
    #plt.show()

#It plots the division distribution. 
def division_distribution(division):
    division=np.array(division)
    n, bins, patches=plt.hist(division, bins=np.arange(-20, 20))#total_count.max()+1))
    # = plt.hist(x, 50, normed=1, facecolor='g', alpha=0.75)


    plt.xlabel('Division')
    plt.ylabel('Number of Users')
    plt.title('Distribution of the ratio between QL and QR for Travel')
    #plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    #plt.axis([0, 200, 0, 250])
    plt.grid(True)
    plt.savefig('division_distribution.pdf', bbox_inches='tight')
    #plt.show()
division_distribution(division)
#It plots the cover distribution. 
def cover_distribution(total_count):
    #print(total_count)
    total_count=np.array(total_count)
    n, bins, patches=plt.hist(total_count, bins=np.arange(total_count.min(), 20))#total_count.max()+1))
    # = plt.hist(x, 50, normed=1, facecolor='g', alpha=0.75)


    plt.xlabel('Cover size')
    plt.ylabel('Number of Users')
    plt.title('Distribution of cover size for Travel')
    #plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    #plt.axis([0, 200, 0, 250])
    plt.grid(True)
    plt.savefig('cover_distribution.pdf', bbox_inches='tight')
    #plt.show()
cover_distribution(total_count)
def QL_cover(number_votes,cover):
    number_votes=np.array(number_votes)
    cover=np.array(cover)
    plt.scatter(number_votes,cover)
    # = plt.hist(x, 50, normed=1, facecolor='g', alpha=0.75)


    plt.xlabel('QL')
    plt.ylabel('QR')
    plt.title('Distribution of QR in the Travel dataset')
    #plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    plt.axis([0, 500, 0, 20])
    plt.grid(True)
    plt.savefig('QL_cover.pdf', bbox_inches='tight')
    #plt.show() 

QL_cover(number_comments,total_count)
    
