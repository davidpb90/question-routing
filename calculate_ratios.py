from initialize import init_db
from DoublingAlgorithms import ratios
import pickle

df, dfC,dfV=init_db()
results_All_All=ratios(df[df.TypeId==1], df,dfC,dfV,'All','All')
results_No_All=ratios(df[df.TypeId==1], df,dfC,dfV,'No votes','All')
results_Answers_All=ratios(df[df.TypeId==1], df,dfC,dfV,'Answers','All')
results_Questions_All=ratios(df[df.TypeId==1], df,dfC,dfV,'Other','All')
results_All_Acc=ratios(df[df.TypeId==1], df,dfC,dfV,'All','Acc')
results_No_Acc=ratios(df[df.TypeId==1], df,dfC,dfV,'No votes','Acc')
results_Answers_Acc=ratios(df[df.TypeId==1], df,dfC,dfV,'Answers','Acc')
results_Questions_Acc=ratios(df[df.TypeId==1], df,dfC,dfV,'Other','Acc')
pickle.dump([results_All_All, results_No_All, results_Answers_All,results_Questions_All,results_All_Acc,results_No_Acc,results_Answers_Acc,results_Questions_Acc], open( "results_travel.p", "wb" ) )
