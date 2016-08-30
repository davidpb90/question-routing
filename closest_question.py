#Finding the closest questions

from initialize import init_db
import pickle
import numpy as np
import random
from random import randint
import jpype
from jpype import *
startJVM(jpype.getDefaultJVMPath(), "-ea", "-Djava.class.path=/Users/cepardot/GoogleDrive/EP/Stage/stackoverflowanalysis-188/db/CoreJointComplexity/bin")
testPkg = JPackage('com').alblf.jc
Test = testPkg.SuffixTree
def find_distance(question1,question):
    a=Test(question1.Text)
    b=Test(question.Text)
    return a.normalizedJC(b)
    
def ordered_questions(question,set_questions):
    order=np.argsort(np.array(set_questions.apply(find_distance,axis=1,args=(question,))))[::-1]
    return set_questions.iloc[order]
    #return set_questions.reindex(order)
def find_number(question,set_questions,test_set):
    
    set_questions=ordered_questions(question,set_questions)
    found=False
    index=1
    answerers=all_answerers(question.Id,test_set)
    while not found:
        if index>50 or index>=len(set_questions): 
            break
        current=set_questions.iloc[index]
        current_answerers=all_answerers(current.Id,test_set)
        if len(set(current_answerers).intersection(set(answerers)))>0:
            found=True
        else:
            index+=1
    return index
def find_all_numbers(test_set):
    set_questions=test_set[test_set.TypeId==1]
    numbers=set_questions.apply(find_number,axis=1,args=(set_questions,test_set))
    return list(numbers)

def distribution_questions(questions,df,size=0.9):
    training_set,test_set=create_sets(questions,df,size)
    result=find_all_numbers(test_set)
    return result

df, dfC,dfV=init_db()
numbers=distribution_questions(df[df.TypeId==1],df)
pickle.dump(numbers, open( "closest_question.p", "wb" ) )
