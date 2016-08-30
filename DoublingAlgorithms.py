import initialize
import numpy as np
import random

#Creates training and test datasets
def create_sets(questions,df,size):
    training_questions=questions.sample(frac=size)
    test_questions = questions.loc[~questions.index.isin(training_questions.index)]
    #print(training_questions)
    training_set=df.loc[np.logical_or(df.Id.isin(training_questions.Id), df.ParentId.isin(training_questions.Id))]
    #print(training_set)
    #test_questions=questions[(int(n*size)):]
    test_set=df.loc[np.logical_or(df.Id.isin(test_questions.Id),df.ParentId.isin(test_questions.Id))]
    #print(df.loc[np.logical_or(df.Id.isin(test_questions.Id),df.ParentId.isin(test_questions.Id))])
    #print(test_set)
    return training_set,test_set
#Given a training and a test set it returns the proportion of questions in the test set for which the answerers 
#(or accepted answerer) lie in the set of interest of the asker in the training set
def ratios(questions, df,dfC,dfV,options_questions=None,options_answerers=None,size=0.9):
    training_set,test_set=create_sets(questions,df,size)
    count_list=percentage(training_set,test_set,df,dfC,dfV,options_questions,options_answerers)
    count=0
    count_random=0
    count_accepted=0
    count_accepted_random=0
    number_answerers_question=[]
    number_answerers=[]
    for row in count_list:
        if row:
            row=np.array(row)
            count+=row[0]
            count_random+=row[1]
            count_accepted+=row[2]
            count_accepted_random+=row[3]
            number_answerers_question.append(row[4])
            number_answerers.append(row[5])
    number_questions=len(test_set[test_set.TypeId==1])
    number_accepted=len(test_set[np.logical_and(test_set.TypeId==1,test_set.AcceptedAnswer>0)])
    return (number_questions, number_accepted, count*1./number_questions, count_random*1./number_questions, 
count_accepted*1./number_accepted, count_accepted_random*1./number_accepted, number_answerers_question,number_answerers)

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
    #answers2=set(df[np.logical_and(df.Id.isin(com_votes),df.TypeId==2)].ParentId)
    #Union of both sets
    #answers=answers1.union(answers2)
    
    
   
    #Questions corresponding to all the answers
    questions=set(df[np.logical_and(df.Id.isin(answers1), df.AnswerCount>1)].Id)
    #Union of both sets
    answersId=answersId.union(questions)
    return list(answersId), list(questions)

#Given an user it returns the list of questions for which she has voted it or one of its answers, as well as the ID 
#of the respective answers.
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


#Given an user it returns the list of questions for which she has commenteded it or one of its answers at least twice, 
#as well as the ID of the respective answers.
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
    #if(user in answerers):
        #answerers.remove(user)
    return answerers

def find_answerers_no_comments(user,questions,df):
    #answerers1=set(dfC[dfC.ParentId.isin(np.array(questions))].UserId)
    answerers=set(df[df.ParentId.isin(np.array(questions))].UserId)
    #answerers=list(answerers1.union(answerers2))
    #if(user in answerers):
        #answerers.remove(user)
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
        comments, questions_comments=find_questions_answers(answerer,df)
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


import heapq
#... etc

# replace greedy_set_cover
#@timer
def greedy_set_cover(subsets, parent_set):
    parent_set = set(parent_set)
    max = len(parent_set)
    # create the initial heap. Note 'subsets' can be unsorted,
    # so this is independent of whether remove_redunant_subsets is used.
    heap = []
    for s in subsets:
        # Python's heapq lets you pop the *smallest* value, so we
        # want to use max-len(s) as a score, not len(s).
        # len(heap) is just proving a unique number to each subset,
        # used to tiebreak equal scores.
        heapq.heappush(heap, [max-len(s), len(heap), s])
    results = []
    result_set = set()
    while result_set < parent_set:
        #logging.debug('len of result_set is {0}'.format(len(result_set)))
        best = []
        unused = []
        while heap:
            score, count, s = heapq.heappop(heap)
            if not best:
                best = [max-len(set(s) - result_set), count, s]
                continue
            if score >= best[0]:
                # because subset scores only get worse as the resultset
                # gets bigger, we know that the rest of the heap cannot beat
                # the best score. So push the subset back on the heap, and
                # stop this iteration.
                heapq.heappush(heap, [score, count, s])
                break
            score = max-len(set(s) - result_set)
            if score >= best[0]:
                unused.append([score, count, s])
            else:
                unused.append(best)
                best = [score, count, s]
            #print(best)
        if best:
            add_set = best[2]
        #logging.debug('len of add_set is {0} score was {1}'.format(len(add_set), best[0]))
            results.append(add_set)
            result_set.update(add_set)
        # subsets that were not the best get put back on the heap for next time.
        while unused:
            heapq.heappush(heap, unused.pop())
    return results
#Given a set of questions and a set of answerers, it returns for each user a list of the users whose interests cover 
# her set of interests, as well as the number of such users. 
def grow_cover_old(questions,answerers,total_cover,total_count,df,dfC):
    number_cover=[]
    cover=[]
    while(questions):
        
        number_in_common, common_questions, user_in_common,answerers=common_elements(questions, answerers,df,dfC)
        if(number_in_common==0):
            print(questions)
            total_cover.append(cover)
            total_count.append(-1)
            return total_cover, total_count  
            #questions=[]
        else:
            cover.append(user_in_common)
            number_cover.append(number_in_common)
            for element in common_questions:
                questions.remove(element)
            
    total_cover.append(cover)
    total_count.append(len(cover))
    return total_cover, total_count
def grow_cover(questions,answerers,total_cover,total_count,df,dfC):
    in_common=[]
    all_in_common=[]
    len_cover=0
    for answerer in answerers:
            
    #print(answerer)
        new_answers=df[np.logical_and(df.UserId==answerer, df.TypeId==2)]
            #new_answersId=answers.Id
        new_questions=set(new_answers.ParentId)
        shared_questions=new_questions.intersection(set(questions))
        in_common.append(list(shared_questions))
        all_in_common=all_in_common+list(shared_questions)
    #print(set(all_in_common), questions)
    #number_in_common, common_questions, user_in_common,answerers=common_elements(questions, answerers,df,dfC)
    if len(set(questions))==len(set(all_in_common)):
        cover=greedy_set_cover(in_common, questions)
        len_cover=len(cover)
    else:
        cover=[]
        len_cover=-1
    total_cover.append(cover)
    total_count.append(len_cover)
    return total_cover, total_count
#It finds the cover for all users.
def find_cover(df,dfC,dfV):
    total_cover=[]
    total_count=[]
    i=0
    for user in set(df.UserId):
        if user!=-2:
            print(i)
            i=i+1
            #questions=df[np.logical_and(df.UserId==user,df.TypeId==1)].Id
            votes, questions=find_questions_no_votes(user,df,dfC)
            if len(questions)>5:
                answerers=find_answerers(user,votes,df,dfC)
                print(len(answerers))
                total_cover,total_count=grow_cover(questions,answerers,total_cover,total_count,df,dfC)
        
    return total_cover,total_count


def get_distributions(df,dfC,dfV):
    number_comments=[]
    number_votes=[]
    difference=[]
    division=[]
    for user in set(df.UserId):#set(dfV.UserId).union(set(dfC.UserId)):
        if user!=-2:
            comments, questions_comments=find_questions_all(user,df,dfC,dfV)
            votes, questions_votes=find_questions_no_votes(user,df,dfC)
            if len(questions_comments)>10:
                number_comments.append(len(questions_comments))
                number_votes.append(len(questions_votes))
                difference.append(len(questions_votes)-len(questions_comments))
                if len(questions_votes)>0:
                    division.append(len(questions_comments)*1.0/(1.0*len(questions_votes)))
    return number_comments, number_votes, difference, division

#Returns all answerers for a given question in a given set.
def all_answerers(question,test_set):
    return test_set.loc[np.logical_and(test_set.TypeId==2, test_set.ParentId==question)].UserId
#Returns all accepted answerers for a given question in a given set.
def accepted_answerers(question,training_set,dfC,dfV):
    return training_set.loc[np.logical_and(training_set.TypeId==2, training_set.ParentId==question)].UserId[0]
#Given a training and a test set it returns the proportion of questions in the test set for which the answerers 
#(or accepted answerer) lie in the set of interest of the asker in the training set
def find_counts(question,test_set,training_set,df,dfC,dfV,options_questions=None,options_answerers=None):
        count=0
        count_random=0
        count_accepted=0
        count_accepted_random=0
        number_answerers_question=0
        number_answerers=0
    #print(question)
        #question=int(question)
        #Returns the question answerers
        answerers_question=all_answerers(question.Id,test_set)
        number_answerers_question=len(answerers_question)
        if number_answerers_question==0:
            return None
        #Returns the accepted answerer
        accepted_answer=list(test_set.loc[test_set.Id==question.Id].AcceptedAnswer)
        if not np.isnan(accepted_answer[0]):
            accepted_answerer=list(test_set.loc[test_set.Id==int(accepted_answer[0])].UserId)
        #Asker
        user=int(test_set.loc[test_set.Id==question.Id].UserId)
        #print(user)
    
        if user!=-2:
            #print(i)
            #questions=df[np.logical_and(df.UserId==user,df.TypeId==1)].Id
            #Returns the questions in which the user has participated
            if options_questions=='All':
                posts, questions=find_questions_all(user,training_set,dfC,dfV)
            #Questions in which the user has commented or answered
            elif options_questions=='No votes':
                posts, questions=find_questions_no_votes(user,training_set,dfC)
            #Questions in which the user has answered
            elif options_questions=='Answers':
                posts, questions=find_questions_answers(user,training_set)
            #Questions that the user has asked
            else:
                posts=list(training_set.loc[np.logical_and(training_set.TypeId==1, training_set.UserId==user)].Id)
            #print(votes)
            #if len(questions)>10:
            #Returns the other users participating in those questions
            if options_answerers=='All':
                answerers=find_answerers(user,posts,training_set,dfC)
            else:
                answerers=find_answerers_no_comments(user,posts,training_set)
            answerers=set(answerers)
            if user in answerers:
                answerers.remove(user)
            number_answerers=len(set(answerers))
            #Returns a random sample of users with the same size as the users in the set of interests
            random_answerers=set(random.sample(set(training_set.UserId),number_answerers))
            if user in random_answerers:
                random_answerers.remove(user)
            #print(answerers)
            #print(len(set(answerers).intersection(set(answerers_question))))
            if len(answerers.intersection(set(answerers_question)))>0:
                count+=1
            if len(random_answerers.intersection(set(answerers_question)))>0:
                count_random+=1
            if not np.isnan(accepted_answer):
                if accepted_answerer:
                    if int(accepted_answerer[0]) in answerers:
                        count_accepted+=1
                    if int(accepted_answerer[0]) in random_answerers:
                        count_accepted_random+=1
            return [count,count_random,count_accepted,count_accepted_random,number_answerers_question,number_answerers]
    
def percentage(training_set,test_set,df,dfC,dfV,options_questions=None,options_answerers=None,size=0.9):

    #print(len(training_set))
    #print(len(test_set))
    #print(n)
    count=0
    count_random=0
    count_accepted=0
    count_accepted_random=0
    counts=test_set[test_set.TypeId==1].apply(find_counts,axis=1,args=(test_set,training_set,df,dfC,dfV,
                                                                       options_questions, options_answerers))
    return counts
        
                
    #return(count*1./len(test_set[test_set.TypeId==1]),count_random*1./len(test_set[test_set.TypeId==1]),
    #       count_accepted*1./len(test_set[np.logical_and(test_set.TypeId==1,test_set.AcceptedAnswer>0)]),
    #    count_accepted_random*1./len(test_set[np.logical_and(test_set.TypeId==1,test_set.AcceptedAnswer>0)]))
        
