# -*- coding: utf-8 -*-
# from numba import jit
from commun_functions import *

d=f_date()   
file="new/file"+str(1)+"_"+d+".csv"  # output file to receive the scrapping result

import json2

jsonList='id_list.json'

def get_json_list(them,debut=0):
    """
        Parameters
    ----------
    them : list of keyword for search
    Returns
    -------
    pkl_list : pkl file containing the id_list to be used for fetching
    """
    jsonList=r'id_list.json'
    # jsonList2=r'id_list.json'
    #  last id recupere....=20800000
    batch=10000  # nombre d'article dans chaque esearch
    max_papers=29800000# nombre maximun d articles attendus
    resutllist=[]
    for elt in them[0:1]: # on fait le querring en utilisant just le premier element
        for batch_i in range(debut,max_papers, batch):
            print("retrieving article {} to {}".format(batch_i,batch_i+batch))            
            try:
                result=search(elt,'pubmed',retstart=batch_i,retmax=batch)
                resutllist += result['IdList']  
            except:
                # sauvegarder le resultat pour une future utilisation
                json2.dump_file(jsonList, resutllist)
                print("The retrieving have been stopped after {} UIDS retrieved".format(len(resutllist)))
        print('SEARCH REPORT: The search found {} articles'.format(len(resutllist)))
       # sauvegarder le resultat pour une future utilisation
        json2.dump_file(jsonList, resutllist)
         
    return jsonList


if __name__ == '__main__':
    
    record=set_record()
    i=0
    # get_json_list(get_them('THEM.txt'))    # obtenir le fichier json
    scrap_data(jsonList=jsonList,output_file=file)

#    review=pd.DataFrame.from_dict(record)
#    review=clean_record(review)
#    d=f_date()
#    review.to_excel("ok/file5_"+d+".xlsx")
