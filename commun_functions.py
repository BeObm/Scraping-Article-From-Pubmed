# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 21:14:54 2020

@author: 24942718
"""
from numba import jit
import numpy as np
import json2 
import re
from Bio import Entrez
from datetime import datetime
batch_size =50000
id_start=0 
import pandas as pd
import os
clear = lambda: os.system('cls')
import time
check_list=['None','PublicationTypeList','jtitle','ArticleTitle','Author 1','Author 1 introduction','Author 1 mailbox',
                'Author 2','Author 2 introduction','Author 2 mailbox',
                'Author n','Author n introduction','Author n mailbox',
                'PubDate','Pagination','issn','volume','issue','Abstract']    # list pour eviter d enregistrer les titres de colonne d une nouvelle feuille comme infos 


def remove_tags(text):
  cleaned_text = re.compile('<.*?>')
  cleantext = re.sub(cleaned_text, '', text)
  return cleantext

dblist = Entrez.read(Entrez.einfo())
dblist= dblist['DbList']


def search(query,db,retstart,retmax):
    
    Entrez.email = 'fairman@live.fr'
    handle = Entrez.esearch(db=db,
                            retstart=retstart,
                            sort='relevance',
                            retmax=retmax,
                            retmode='xml',
                            term=query)
    results = Entrez.read(handle, validate=False)

    return results



def fetch(id_list,db):
    ids = ','.join(id_list)
    Entrez.email = 'fairman@live.fr'
    handle = Entrez.efetch(db=db,
                           retmode='xml',
                           id=ids)
# ['pubmed', 'protein', 'nuccore', 'nucleotide', 'nucgss', 'nucest', 'structure', 'genome',
#'annotinfo', 'assembly', 'bioproject', 'biosample', 'blastdbinfo', 'books',
#'cdd', 'clinvar', 'clone', 'gap', 'gapplus', 'grasp', 'dbvar', 'epigenomics',
#'gene', 'gds', 'geoprofiles', 'homologene', 'medgen', 'mesh', 'ncbisearch',
#'nlmcatalog', 'omim', 'orgtrack', 'pmc', 'popset', 'probe', 'proteinclusters',
#'pcassay', 'biosystems', 'pccompound', 'pcsubstance', 'pubmedhealth', 'seqannot',
#'snp', 'sra', 'taxonomy', 'unigene', 'gencoll', 'gtr']

    results = Entrez.read(handle,validate=False)
#    handle.close()
    return results


def f_date():
    # datetime object containing current date and time
     now = datetime.now()
     # dd/mm/YY H:M:S
     #dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
     dt_string = now.strftime("%d%m_%H%M")
#     print("date and time =", dt_string)
     return dt_string




def scrap_data(jsonList,output_file):
         """cette fonction permet de recuperer les infos du site web de pubmed
    puis d en extraire les informations voulues par lots d articles"""
         rec = 1  # to count the number of complete articles scrapped
         err = 0  # to count the number of incomplete articles
        
         id_list = list(json2.load_file(jsonList))                                                             
         print("Total articles to check:", len(id_list))
         record = set_record()
         review=pd.DataFrame.from_dict(record)
#                   review=clean_record(review)
         review.to_csv(output_file, mode='a',index=False,header=True)

         for batch_i in range(0, len(id_list), batch_size):
             
                         
           maxx=batch_i + batch_size
           batch = id_list[batch_i:maxx]
           tot=id_list[maxx:len(id_list)]
                    
    #           try:
           time.sleep(0.2)
           papers = fetch(batch,'pubmed')
#           print("\n fetching suceess for bach",batch)
#           with open("id_list.txt",'a') as id_list:
#                 id_list.write(str(batch[len(batch)-1])+'\n')
#           except:
#                print("\n fetching fail for bach",batch)
#                pass
           
           for i, paper in enumerate(papers['PubmedArticle']):
                keep=True
                record = set_record()
                if rec % 400000 ==0:
                    d=f_date()   
                    output_file ="new/file"+str(1)+"_"+d+".csv"
                    rec=0
                     
                p=paper['MedlineCitation']['Article']

                #@@@@  DOI + URL

                try:
                  doi1=p['ELocationID']
                  doi= doi1[0]
                  # print('doi: ', doi)
                  if doi.startswith("http") or doi.startswith("HTTP"):

                            url=doi
                            # url='http://pubs.acs.org/doi/'+doi
                  else:
                            url='http://dx.doi.org/'+doi
                   
                            doi= doi                          
                  record['DOI'].append(doi)
                  record['URL'].append(url)
                except: #
                  doi='None'
                  url="None"
                  keep=False
                  
                  # print("doi error")

                 #@@  Authors
                
                auth={}
                auths=[]

                try:
                      for elt in p['AuthorList']:
                           affiliation =elt['AffiliationInfo'][0]
                           affiliation= affiliation['Affiliation']
                           authname= elt['LastName']+' '+elt["ForeName"]
                           
                           auths.append((authname,affiliation))

                      mail_exist,authlist=get_authors(auths)

                      auth1,aff1='None','None'
                      auth2,aff2='None','None'
                      authn,affn='None','None'
                      email1,email2,emailn='None','None','None'                                          
                      if mail_exist==True:
                          if len(authlist)>=1:
                            auth1=authlist[0][0]
                            aff1=authlist[0][1]
                            email1=authlist[0][2]
                            
                            if len(authlist)>=2:
                              auth2=authlist[1][0]
                              aff2=authlist[1][1]
                              email2=authlist[1][2]
                               
                              if len(authlist)>=3:
                                     authn=authlist[2][0]
                                     affn=authlist[2][1]
                                     emailn=authlist[2][2]                         
                   
                            record['Author 1'].append(auth1)
                            record['Author 1 introduction'].append(aff1)
                            record['Author 1 mailbox'].append(email1)
        
                         
                            record['Author 2'].append(auth2)
                            record['Author 2 introduction'].append(aff2)
                            record['Author 2 mailbox'].append(email2)
                               
                             
                            record['Author n'].append(authn)
                            record['Author n introduction'].append(affn)
                            record['Author n mailbox'].append(emailn) 
                      else:
                          keep=False
                          
                except: #
                       keep=False
                       
                   
                
                ######  @@   ISSN
                try:
                  issn=p['Journal']['ISSN']
#                  print('issn: ', issn)
                except: #
                  issn='None'
                  # print("issn error")
                record['issn'].append(issn)

     ##@@@   VOlume Journal
                try:
                      volume=p['Journal']['JournalIssue']['Volume']
#                      print("volume: ", volume)
                except: #
                      volume='None'
                      # print("volume error")
                record['volume'].append(volume)

     #@@@@@  ISUUE
                try:
                      issue=p['Journal']['JournalIssue']['Issue']
#                      print('issue: ',issue)
                except: #
                      issue='None'
                      # print("issue error")
                record['issue'].append(issue)


     ## @@  DATE OD PUBLICATION
                try:
                      date=p['Journal']['JournalIssue']['PubDate']
                      PubDate='/'.join(date.values())
#                      print('PubDate: ',PubDate)
                except: #
                     PubDate='None'
                     keep=False
                     # print("datepub error")
                record['PubDate'].append(PubDate)

     #@@  Journal Title
                try:
                      jtitle=p['Journal']['Title']
                      jtitle=remove_tags(jtitle)
#                      print('J Title：', jtitle)
                except: #
                      jtitle='None'
                      keep=False
                      # print("jtitle error")
                record['jtitle'].append(jtitle)


     #@@  Article Title
                try:
                      ArticleTitle =p['ArticleTitle']
                      ArticleTitle=remove_tags(ArticleTitle)
#                      print('ArticleTitle ：', ArticleTitle)
                except: #
                     ArticleTitle  ='None'
                     keep=False
                     # print("article title error")
                record['ArticleTitle'].append(ArticleTitle)


     #@@  Pagination
                try:
                      pages =p['Pagination']['MedlinePgn']
#                      print('Pagination ：', pages)
                except: #
                      pages  ='None'
                      # print("pages error")
                record['Pagination'].append(pages)


     #@@  PublicationTypeList
                try:
                      PTL =p['PublicationTypeList']
                      PTL= '; '.join(PTL)
#                      print("PTL: ",PTL)

                except: #
                      PTL  ='None'
                      # print("PTL error")
                record['PublicationTypeList'].append(PTL)



     #@@  Abstract
                try:
                      abstract =p['Abstract']['AbstractText']
                      abstract='\n'.join(abstract)
                      abstract= remove_tags(abstract)
#                      print(abstract,'\n')

                except: #
                      abstract  ='None'
                      keep=False
                      # print('abstract error')
                record['Abstract'].append(abstract)


    
                if keep==False:                  
                    err+=1
                if keep==True:
                    clear()
                    rec+=1  
                   
                    review=pd.DataFrame.from_dict(record)
#                   review=clean_record(review)
                    review.to_csv(output_file, mode='a',index=False,header=False)
                print("Report: {} articles sauvegardés et {} articles écartés".format(rec,err))
#         p=pd.read_csv(output_file)
#         p.to_excel("okkk.xlsx",index=None,header=True)
           json2.dump_file(jsonList, tot)          
                       
         return output_file



def get_authors(auths):
    authlist=[]
    authors=[]
    for auth in auths:  # boucle pour recherhcer et retirer le mail de l  affiliation
            affiliation =auth[1]
                        
            email1 = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", auth[1])
            if email1 != "" :
                email= email=' '.join(email1)
                # affiliation=auth[1].replace(email,' ')
            else:
                 email1 = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", auth[1])
                 if email1 != "" :
                    email=' '.join(email1)  
                    # affiliation=auth[1].replace(email, ' ')
                 else:
                     email1 = re.findall(r"[a-z0-9\.\-+_]+at[a-z0-9\.\-+_]+dot[a-z]+", auth[1])
                     if email1 != "" :
                         email=' '.join(email1)
                         # affiliation=auth[1].replace(email,' ')
                     else:
                         email1 = re.findall(r"[a-z0-9\.\-+_]+at[a-z0-9\.\-+_]+dot[a-z]+", auth[1]) 
                         if email1 != "" :
                             email=' '.join(email1)
                             # affiliation=auth[1].replace(email,' ')
                         else:
                            email='None'
            
            authlist.append((auth[0],affiliation,email))
                                                                            
    
    if authlist[0][2] != 'None':    # voir si le mail du premier auteur est disponible
        mail_exist=True
    else:
        if authlist[1][2] !="None":    # voir si le mail du second auteur est disponible
            mail_exist =True
        else:
            mail_exist=False
    
    if mail_exist == False:
        for auth in authlist[2:]:      # boucle pour verifier si au moins un autre auteur a un mail
            if auth[2]=='None':
                 mail_exist=False
            else:
                mail_exist=True
                authors.append(authlist[0])
                authors.append(authlist[1])
                authors.append(auth)
    else:
        
       authors.append(authlist[0])
       authors.append(authlist[1])
       authors.append(authlist[-1])
         
    for elt in authors:
      if '@' in elt[2]:
        mail_exist=True
        break
      else:
        mail_exist=False   
            
    return mail_exist,authors









def clean_record(record,old_doi):
     """ cette fonction permet de netooyer les article obtenu en eliminant les doublons
    et en supprimant ceux qui ne respectent pas les criteres de selection"""

     print(len(record),'records before cleaning')
     record.drop_duplicates(subset=['DOI'],inplace=True)
     print(len(record), 'records after droping duplicates')
     for index, row in record.iterrows() :
           keep=True
           # lists=[ row['DOI'],row['Author 1 mailbox'],row['Author 1'],
           #        row['Abstract'],row['Author 1 introduction'],row['jtitle']]
          
           if row['DOI'] in old_doi or row['DOI'] in check_list:
              keep=False
           else:    
              
              
                if row['Abstract'] in check_list:
                                     keep=False
                else:
                 
                    if row['jtitle'] in check_list:
                         keep=False
                                                                                              
           if keep==False:
               try:
                   record= record.drop(index)
               except:
                    pass

     return record


def get_them(txt_file):
     """ cette fonction permet d obtenir la liste des terms de recherche a utiliser  """
     them=[]
     with open(txt_file,'r') as doc:
          text=doc.readlines()
          for elt in text:
              if elt!='':
                  a=elt.split('&')
                  for b in a:
                      them.append(b)
#          text=text.lower()
#          text=text.split()
#          text=set(text)
#          thems=[tem for tem in text if len(tem)>=8]
     return them


def set_record():
    """ Cette fonction permet de reinitialiser le dictionnaire devant contenir
     les records"""   
    record = defauldist(list)
    return record








def  get_frame(file_path):
     """ cette fonction permet de lire un fichier xlsx ou csv
     puis de convertir son contenu en pandaDataFrame"""
     data =[]
     i=1
     files=os.listdir(file_path)
     for file in files:
           print(i,': The file',file,'in process...')
           i+=1
           if file[-3:]=='lsx':
               d00= pd.read_excel(file_path+file,sheet_name =None)
               for el,val in d00.items():
                  data.append(val)
           if file[-3:]=='csv':
               d1= pd.read_csv(file_path+file)
               data.append(d1)
     frame = pd.concat(data, ignore_index=True)
     print("the folder's files have",len(frame),"records")

     return frame
