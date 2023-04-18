import requests
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import text

# Initial config
vm_ip =  "34.176.179.120"# By default the internal ip used by mlflow is 127.0.0.1, but to externalize the model the external  ip of the vm must be written here
vm_port = "5001"

db_pass = "trinibd"
db_ip = "34.176.228.62"
db_name = "postgres"
db_user = "postgres"
db_port = "5432"


def parse_request(request):
    # The request MUST have this format
    # {'dataframe_split': {event_id: '5e82b70d-b550-4bee-9d5d-16a2e73029f9', 'data':[[10,10,10,10]]}}
    #request = request.get_json()

    event_id = request.pop('event_id') if 'event_id' in request else 'no_event_id'

    features = request["data"]
    assert len(features) == 30, 'The request must have the correct ammount of columns (At least)'

    return event_id, features


def save_predictions(event_id, prediction):
    # For remote dbs
    # engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_ip}:{db_port}/{db_name}')

    # For localhost there is no port
    # engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_ip}/{db_name}')


    conn_string = f"host='{db_ip}' dbname='{db_name}' user='{db_user}' password='{db_pass}'"
    conn =  psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute(f"""insert into public.inference(id, value) values('{event_id}',{prediction})""")
    conn.commit() # <- We MUST commit to reflect the inserted data
    cursor.close()
    conn.close()

def externalized_model(features) -> str:
    headers = {}

    json_request = {'dataframe_split': {'data':[features]}}

    response = requests.post(f'http://{vm_ip}:{vm_port}/invocations', headers=headers, json=json_request)
    response = response.json()["predictions"]

    return response[0]


def check_business_logic(features):
    """
    Here We should put some business logic
    We're going to put the min/max of the covid dataset features
    """
    casos, casospermil, hombres80, mujeres80, pobla80, pobla65, poblamid, pobladata, pobladens, mujeres, urbano, expectvida, neontlmort, dismort, lesion, enfnotrans, enftrans, pbi, tuberculosis, diabetes, medicos, camas, immunsaramp, tempmarzo, hiptenh, hiptenm, hipten, bcg, tiempo, l10casospermil = features
    
    casos_condition =  (2 <= casos) and (casos <= 1699933)
    casospermil_condition =  (0.948707 <= casospermil) and (casospermil <= 	17596.219834)
    
    hombres80_condition =    (0.087368 <= hombres80) and (hombres80 <= 	6.166254)
    mujeres80_condition =    (0.163864 <= mujeres80) and (mujeres80 <= 	10.556442)
     
    pobla80_condition =      (0.130777 <= pobla80) and (pobla80 <= 	8.361348) 
    pobla65_condition =      (1.085001 <= pobla65) and (pobla65 <= 	27.576370) 
    poblamid_condition =     (47.420668 <= poblamid) and (poblamid <=  85.089165)
    pobladata_condition =    (0.001102 <= pobladata) and (pobladata <=  13.927300)
    pobladens_condition =    (0.020406 <= pobladens) and (pobladens <=  79.529984)
      
    mujeres_condition =      (24.495287	<= mujeres) and (mujeres <= 54.535343)
    urbano_condition =       (13.032000	<= urbano) and (urbano <= 100.000000) 
    
    expectvida_condition =   (49.837000		<= expectvida) and (expectvida <= 81.700000	)
    neontlmort_condition =   (0.900000		<= neontlmort) and (neontlmort <= 42.000000	)  
    
    dismort_condition =      (7.800000			<= dismort) and (dismort <= 30.600000		)
    lesion_condition =       (2.600000		<= lesion) and (lesion <= 28.400000	)
    enfnotrans_condition =   (26.000000			<= enfnotrans) and (enfnotrans <= 95.200000		)
    enftrans_condition =     (1.300000			<= enftrans) and (enftrans <= 65.300000	)
    pbi_condition =          (0.756838			<= pbi) and (pbi <= 123.213936)
    tuberculosis_condition = ( 1.000000			<= tuberculosis) and (tuberculosis <= 611.000000)
    diabetes_condition =     (1.000000			<= diabetes) and (diabetes <= 22.000000			)
    
    medicos_condition =      (0.017675		<= medicos) and (medicos <= 5.710111		)
    camas_condition =        (0.200000		<= camas) and (camas <= 13.796000	)
   
    immunsaramp_condition =  (30	<= immunsaramp) and (immunsaramp <= 99	)
    tempmarzocondition =     (-18.720000		<= tempmarzo) and (tempmarzo <= 30.630000	)
    
    hiptenh_condition =      (9.000000	<= hiptenh) and (hiptenh <= 54.600000)
    hiptenm_condition =      (12.400000	<= hiptenm) and (hiptenm <= 50.600000)
    hipten_condition =       (10.700000			<= hipten) and (hipten <= 50.600000)
    
    bcg_condition =            (0	= bcg) and (bcg = 1)
    tiempo_condition =         (0		<= tiempo) and (tiempo <= 136)
    l10casospermil_condition = (0.2897465890359868			<= l10casospermil) and (l10casospermil <= 4.245444059518778	)
    
    return not(
    casos_condition and casospermil_condition and hombres80_condition and mujeres80_condition and pobla80_condition and 
    pobla65_condition and poblamid_condition and pobladata_condition and pobladens_condition and mujeres_condition and urbano_condition and expectvida_condition and neontlmort_condition and dismort_condition and
    lesion_condition and enfnotrans_condition and enftrans_condition and pbi_condition and tuberculosis_condition and diabetes_condition and medicos_condition and camas_condition and
    immunsaramp_condition and tempmarzocondition and hiptenh_condition and hiptenm_condition and hipten_condition and bcg_condition and tiempo_condition and l10casospermil_condition
    )
    


def get_business_prediction(features):
    "Here we could have some function of the feature"

    return -1


def trigger_events(request):
    # This pipeline supposes that we are using it to do just one inference at the time
    # If we want to do more inferences, we need to modify the functions to be able to handle them

    #This is to work inside the lambda fn
    request = request.get_json()
    event_id, features = parse_request(request)

    if check_business_logic(features):
        prediction = get_business_prediction(features)

    else:
        prediction = externalized_model(features)

    save_predictions(event_id, prediction)

    return str(prediction)

print(trigger_events(
  # no cumple business condition
   {"event_id": "17cfe7d5-3cdb-4e62-861d-0371b79f16f2", "data": [-100, 382.5, 0.5, 0.45, 0.32, 3.21, 62.34, 0.42, 0.61, 
             52.67, 23.45, 60.52, 38.2, 19.7, 15.5, 45.1, 35.8, 1.23, 
             192, 10.3, 0.45, 0.32, 68, 91.1, 22.2, 22.2, 19.3, 
             1, 53, 0.6]}
))

print(trigger_events(
  # no cumple business condition
   {"event_id": "17cfe7d5-3cdb-4e62-861d-0371b79f16f2", "data": [10, 382.5, 0.5, 0.45, 0.32, 3.21, 62.34, 0.42, 0.61, 
             52.67, 23.45, 60.52, 38.2, 19.7, 15.5, 45.1, 35.8, 1.23, 
             192, 10.3, 0.45, 0.32, 68, 91.1, 22.2, 22.2, 19.3, 
             1, 53, 0.6]}
))


#print(trigger_events(
#    {"event_id": "event_id_1", "dataframe_split": {"data":[[10,10,10,10]]}}
#    ))

#print(trigger_events(
#    { "dataframe_split": {"data":[[0,0,0,0]]}}
#    ))

#print(trigger_events(
#    { "dataframe_split": {"data":[[19,10,10,10]]}}
#    ))
