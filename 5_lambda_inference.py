import requests

def externalized_model(request) -> list:
  vm_ip =  '34.176.52.229' #By default the internal ip used by mlflow is 127.0.0.1, but to externalize the model the external  ip of the vm must be written here
  # Remember to change ip every time we turn on the vm again!
  
  headers = {}
  
  #This is to be able to check the lambda fn inside the vm
  request = request.get_json()

  response = requests.post(f'http://{vm_ip}:5001/invocations', headers=headers, json=request)
  return str(response.json())

# In requirements.txt add requests

# Testing function:
#{"dataframe_split": {"columns":["casos", "casospermil", "hombres80", "mujeres80", "pobla80", "pobla65", "poblamid", "pobladata", "pobladens", 
#"mujeres", "urbano", "expectvida", "neontlmort", "dismort", "lesion", "enfnotrans", "enftrans", "pbi", "tuberculosis", "diabetes", "medicos", 
#"camas", "immunsaramp", "tempmarzo", "hiptenh", "hiptenm", "hipten", "bcg", "tiempo", "l10casospermil"], 
#"data": [[10200, 382.5, 0.25, 0.45, 0.32, 3.21, 62.34, 0.42, 0.61, 52.67, 23.45, 
#60.52, 38.2, 19.7, 15.5, 45.1, 35.8, 1.23, 192, 10.3, 0.45, 0.32, 68, 8.1, 21.2, 22.2, 19.3, 1, 53, 0.6]]}}
