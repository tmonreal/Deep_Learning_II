curl http://34.176.179.120:5001/invocations -H 'Content-Type: application/json' -d '{"dataframe_split": {"data": [[10200, 382.5, 0.25, 0.45, 0.32, 3.21, 62.34, 0.42, 0.61, 52.67, 23.45, 60.52, 38.2, 19.7, 15.5, 45.1, 35.8, 1.23, 192, 10.3, 0.45, 0.32, 68, 8.1, 21.2, 22.2, 19.3, 1, 53  ]]}}'

# ['casos', 'casospermil', 'hombres80', 'mujeres80', 'pobla80', 'pobla65',
#       'poblamid', 'pobladata', 'pobladens', 'mujeres', 'urbano', 'expectvida',
#       'neontlmort', 'dismort', 'lesion', 'enfnotrans', 'enftrans', 'pbi',
#       'tuberculosis', 'diabetes', 'medicos', 'camas', 'immunsaramp',
#       'tempmarzo', 'hiptenh', 'hiptenm', 'hipten', 'bcg', 'tiempo',
#       'l10casospermil']
