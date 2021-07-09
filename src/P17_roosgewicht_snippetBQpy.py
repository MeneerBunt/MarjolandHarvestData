# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 09:14:58 2021

@author: 602956
"""

import pandas as pd
import pickle


# dit is het model zoals we het hebben getraind in een andere code, het resultaat is opgeslagen in een pickle.
clf = pickle.load( open('D:\P_17 - roosgewicht\data\clf_roosgewicht_marjoland.pckl', 'rb') )


# dis is de json, die nu in BQ wordt geladen. Deze wordt ook ingeladen in dit proces om 
# een voorspelling te doen van het gewicht van de roos. In BQ
file_path = "D:\P_17 - roosgewicht\data\harvest.jsonl"
json = pd.read_json(path_or_buf=file_path, lines=True)


# de functie: 
def PredictRoseweight(table, model):
    
    # tabel inlezen en pivot, zodat het in de svr past  
    df = table[['id','classification_nr', 'classification_products_pieces','avg', 'parameter_id']]
    df = df[df.parameter_id.isin(['4', '140', '141', '114', '113'])]
    df.classification_products_pieces = pd.to_numeric( df.classification_products_pieces )
    
    # 
    df = pd.pivot_table(df, values='avg', index=['id', 'classification_nr', 
                                                 'classification_products_pieces'],
                        columns=['parameter_id'])
    
    df = df.reset_index(drop=False)
    df = df.rename_axis(None, axis=1)
    
    # doe de voorspelling, louter op parameters 113, 114, 140, 141
    df_predict = df
    y = model.predict(df[[113, 114, 140, 141]])
    
    df_predict['gr'] = y 
    df_predict.gr = df_predict.gr.round()
    
    #pivot agian
    out = df_predict[['id', "classification_nr", "gr", "classification_products_pieces"]].melt(
        id_vars=['id', "classification_nr", "classification_products_pieces"], 
        var_name="parameter_id", 
        value_name="avg")

    out['sum'] = out.avg * out.classification_products_pieces
    
    out.loc[(out.parameter_id == 'gr'),'parameter_id']=99
    out[ 'min'], out[ 'max'] = out[ 'avg'], out[ 'avg']
    out[ 'stddev'] = 0
    
    return( out )


out = PredictRoseweight(json, clf)