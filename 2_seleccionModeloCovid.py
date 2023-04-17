#!/usr/bin/env python
# coding: utf-8

# In[1]: Initial setup


import mlflow
from mlflow.client import MlflowClient

import os


client = mlflow.client.MlflowClient()
## This db could be an external postgres database
# mlflow.set_tracking_uri('sqlite:///mlruns.db')
# conectarse a la base de datos de postgres con mlflow postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]
user= 'postgres'
password= ')5]U`.kAhKNqt3K~'
netloc='34.176.228.62'
port='5432'
dbname='postgres'

conn_string = f'postgresql+psycopg2://{user}:{password}@{netloc}:{port}/{dbname}'

mlflow.set_tracking_uri(conn_string)

# In[2]: Muestre los resultados de los modelos en mlflow

list_mlflow_experiments =  mlflow.search_experiments()
list_experiment_id = list(map(lambda list_mlflow_experiments: int(list_mlflow_experiments.experiment_id), list_mlflow_experiments ))
last_experiment_id =  max(list_experiment_id)


runs = mlflow.search_runs(experiment_ids = [last_experiment_id])

best_model_run_id = runs.sort_values(by = ['metrics.avg_iba'], ascending = False).iloc[0]['run_id']
print(best_model_run_id)

new_model = mlflow.register_model(f'runs:/{best_model_run_id}/model','ml2_uba')


client = mlflow.client.MlflowClient()
client.transition_model_version_stage('ml2_uba',
                                      new_model.version,
                                      "production",
                                      archive_existing_versions = True)


# %%