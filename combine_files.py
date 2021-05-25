 # -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 21:51:47 2020

@author: 24942718
"""
import pandas as pd
from commun_functions import clean_record
from commun_functions import f_date
from commun_functions import *


new_files="new/"

old_files='old/'

def combine_check(old_files_path,new_files_path,batch_size=25000):

        old_frame=get_frame(old_files_path)
        old_doi=[]
        for index, row in old_frame.iterrows() :
            old_doi.append(row['DOI'])


        new_frame=get_frame(new_files_path)
        frame=clean_record(new_frame,old_doi)
        print('After cleaning,  the combined dataframe has',len(new_frame),'records to put in',(len(new_frame)//batch_size)+1, 'sheets' )
#        frame=new_frame.sub(old_frame,axis='index')
        # write it out
        print('\n Combined file edition in progress,please wait...' )
        k=0
        dat=f_date()
        for j in range((len(frame)//200000)+1):
            writer = pd.ExcelWriter('new/combined_list_'+str(j+1)+'_'+dat+'.xlsx')

            for i in range(8):
                     batch_i=k*batch_size
                     k+=1
                     d2 = frame.iloc[batch_i:batch_i + batch_size,:]
                     d2.to_excel(writer,'sheet_'+str(i+1), header=True)
            writer.save()
        return frame




combine_check(old_files,new_files)