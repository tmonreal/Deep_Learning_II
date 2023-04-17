#!/usr/bin/env python
# coding: utf-8

# In[0]: Import libraries


import mlflow
from mlflow.client import MlflowClient

import os
import sklearn
import numpy  as np

import pandas as pd
import psycopg2

# sklearn
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PowerTransformer, RobustScaler
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV, SGDClassifier
from sklearn.neighbors import LocalOutlierFactor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,roc_auc_score, classification_report, confusion_matrix, precision_recall_curve, auc, balanced_accuracy_score, f1_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.feature_selection import SelectKBest, f_classif

from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingGridSearchCV
from sklearn.datasets import make_classification

# imblearn
from imblearn.metrics import classification_report_imbalanced
from imblearn.metrics import geometric_mean_score as gmean
from imblearn.metrics import make_index_balanced_accuracy as iba
from sklearn.metrics import make_scorer

gmean = iba(alpha=0.1, squared=True)(gmean)
gmean_scorer = make_scorer(gmean)

# In[1]: Initial setup

#This will be used in the next class
# os.chdir('/home/ml2/aprendizaje_maquina_II/Clase 5') 

client = mlflow.client.MlflowClient()
## This db could be an external postgres database
# mlflow.set_tracking_uri('sqlite:///mlruns.db')
# conectarse a la base de datos de postgres con mlflow postgresql+psycopg2://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]
user= 'postgres'
password= 'trinibd'
netloc='34.176.228.62'
port='5432'
dbname='postgres'

conn_string = f'postgresql://{user}:{password}@{netloc}:{port}/{dbname}'

mlflow.set_tracking_uri(conn_string)

## This will fail in databricks because the experiment_id is a random hash

new_experiment_id = 0 #Why not put this in an else? Just because I can
list_mlflow_experiments =  mlflow.search_experiments()
if len(list_mlflow_experiments):
    list_experiment_id = list(map(lambda list_mlflow_experiments: int(list_mlflow_experiments.experiment_id), list_mlflow_experiments ))
    last_experiment_id =  max(list_experiment_id)
    new_experiment_id  = last_experiment_id + 1
    
    mlflow.create_experiment(str(new_experiment_id))

# In[2]: Carga de datos

# Carga de base de datos a pandas
# desde csv
# df_covid = pd.read_csv('datosCovid.csv')
# desde postgres
conn = psycopg2.connect(conn_string)
sql = 'select * from public."datoscovid";'
df_covid = pd.read_sql_query(sql, conn)

# conn.close()

# Mortalidad baja
df_covid.loc[df_covid['l10muertes.permil'] <= 1, 'mortalidad'] = 0

# Mortalidad alta
df_covid.loc[df_covid['l10muertes.permil'] > 1, 'mortalidad'] = 1

# Se calcula el logarimo base 10 de los casos por millon habitantes, asi evitamos posibles outliers 
df_covid['l10casos.permil'] = np.log10( 1 + df_covid['casos.permil'])

# This should be a query from a database
# Eliminamos la variable target de X como asi tambien aquellas que tienen valores de muerte 
X = df_covid.drop(['mortalidad','l10muertes.permil','muertes.permil','muertes','cntrname','geoid','bcgf'], axis = 1)
y = df_covid['mortalidad']

# # Usando el autolog muchas metricas se guardan solas...

# In[3]:


mlflow.sklearn.autolog(max_tuning_runs = None)

X_train, X_test, y_train, y_test = train_test_split(X,y, stratify = y)


# In[4]: Definimos una funcion para entrenar los modelos y guardar los resultados en mlflow


def log_model(model,
              developer = None,
              experiment_id = None,
              grid = False,
              **kwargs):
    
    
    assert developer     is not None, 'You must define a developer first'
    assert experiment_id is not None, 'You must define a experiment_id first'
    
    
    with mlflow.start_run(experiment_id = experiment_id):

        mlflow.set_tag('developer',developer)
        
        #The default is to train just one model
        # model = model(**kwargs)
        if grid:
            model = HalvingGridSearchCV(model,
                                        param_grid = kwargs,
                                        scoring= gmean_scorer,
                                        n_jobs= -1)
        else:
            model = model(**kwargs)
        
        
        model.fit(X_train, y_train)
        # test_acc = (model.predict(X_test) == y_test).mean()
        test_inbalanced = classification_report_imbalanced(y_test, model.predict(X_test), output_dict=True)

        # mlflow.log_metric('test_acc',test_acc)
        mlflow.log_metric('avg_f1',test_inbalanced['avg_f1'])
        mlflow.log_metric('avg_iba',test_inbalanced['avg_iba'])
        
        # obtengo el nombre del modelo
        model_name = model.__class__.__name__
        print(model_name)
        # guardo el modelo
        mlflow.sklearn.log_model(model,model_name)

# In[5]: Entrene los modelos y guarde los resultados en mlflow


#normal logging
log_model(LogisticRegressionCV      ,'trini', experiment_id = new_experiment_id, **{'class_weight':'balanced'})
log_model(RandomForestClassifier    ,'trini', experiment_id = new_experiment_id, **{'class_weight':'balanced'})
log_model(GradientBoostingClassifier,'trini', experiment_id = new_experiment_id, **{'learning_rate':0.1})
log_model(AdaBoostClassifier,'trini', experiment_id = new_experiment_id, **{'learning_rate':0.1,'n_estimators':50})
log_model(LinearSVC,'trini', experiment_id = new_experiment_id, **{'random_state':0,'tol':1e-05})

# param_grid_LRCV = {
#     'LogisticRegressionCV__solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
#     'LogisticRegressionCV__class_weight': [None, 'balanced']
#     }
# log_model(LogisticRegressionCV ,'diego', experiment_id = new_experiment_id, grid = True, **param_grid_LRCV)

# Colocar entrenamiento de grid search
#grid logging
# log_model(SVC    ,
#           'trini', 
#           experiment_id = new_experiment_id, 
#           grid = True,
#           **{'kernel':('linear', 'rbf'), 'C':[1, 10]}
# )

# In[6]: Muestre los resultados de los modelos en mlflow
list_mlflow_experiments =  mlflow.search_experiments()
list_experiment_id = list(map(lambda list_mlflow_experiments: int(list_mlflow_experiments.experiment_id), list_mlflow_experiments ))
last_experiment_id =  max(list_experiment_id)

runs = mlflow.search_runs(experiment_ids = [last_experiment_id])
runs
# %%
for i in range(len(runs)):
    print(runs['run_id'][i])
    print(runs['metrics.avg_f1'][i])
    print(runs['metrics.avg_iba'][i])
    print('')

# %%
