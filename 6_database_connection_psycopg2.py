import psycopg2

user= 'postgres'
password= 'trinibd'
ip='34.176.228.62'
port='5432'
db_name='postgres'

conn_string = f"host='{ip}' dbname='{db_name}' user='{user}' password='{password}'"
with psycopg2.connect(conn_string) as conn:
  cursor = conn.cursor()
  cursor.execute("""insert into public.inference("value") values(-1)""")
  conn.commit() # <- We MUST commit to reflect the inserted data
  cursor.close()
