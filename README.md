# Designing Machine Learning Systems

Este repositorio contiene el trabajo final de la asignatura de Machine Learning II de la Carrera de Especialización en Inteligencia Artificial (CEIA) de la Universidad de Buenos Aires.

## 1. Introducción
El objetivo de este proyecto es realizar un entrenamiento y despliegue de modelos de aprendizaje automático en la nube. En particular, los modelos buscan clasificar la tasa bruta de mortalidad durante el año 2020 en el cual comenzó la pandemia de COVID-19. En este trabajo, se trata a la mortalidad como una variable objetivo binaria, teniendo como posibles valores: tasa de mortalidad baja (0) o alta (1). 

El [dataset analizado](https://github.com/tmonreal/Machine_Learning_II/blob/main/datacovid.csv) es el que se presenta en el paper: Hradsky, O., & Komarek, A. (2021). Demographic and public health characteristics explain large part of variability in COVID-19 mortality across countries. European journal of public health, 31(1), 12–16.

## 2. Desarrollo
En primer lugar, se realizó un análisis exploratorio del conjunto de datos para examinar la información, observar las características principales y realizar visualizaciones. Finalmente, las features que se definieron para ingresar a los modelos son 30, a saber: 

1. Casos: número de casos de covid hasta el 28/05/2020
2. Casos.permil: casos por millón
3. L10Casos.permil: log10(1+casos.permil)
4. Hombres80: % de hombres mayores de 80 años
5. Mujeres80: % de mujeres mayores de 80 años
6. Pobla80: media del % de hombres > 80 y mujeres > 80 años
7. Pobla65: % población > 65 años
8. PoblaMid: % población entre 15 y 64 años
9. PoblaData: número de personas por cada 100 millones
10. PoblaDens: cientos de personas por km2
11. Mujeres: % población femenina del total
12. Urbano: % población urbana del total
13. ExpectVida: años de esperanza de vida al nacer
14. NeontlMort: tasa mortalidad por cada 1000 nacidos vivos
15. DisMort: % mortalidad entre 30 y 70 años
16. Lesion:% causas de muerte por lesión
17. EnfNoTrans: % causas de muertes por enfermedades no transmisibles
18. EnfTrans: % causas de muertes por enfermedades transmisibles, condiciones
prenatales y nutrición
19. PBI: PBI en miles de dólares
20. Tuberculosis: incidencia por cada 1000 personas
21. Diabetes: % población de 20 a 79 años
22. Médicos: número de médicos por cada 1000 personas
23. Camas: número de camas por cada 1000 personas
24. ImmunSaramp: % inmunización sarampión niños entre 12 a 23 meses
25. TempMarzo: temperatura media en marzo 2020
26. HipTen.H: prevalencia hipertensión hombres-2010
27. HipTen.M: prevalencia hipertensión mujeres-2010
28. HipTen: valor medio entre HipTen.H y HipTen.M
29. BCG: estrategia de inmunización 0 (selectiva-grupos de riesgo) o 1 (toda)
30. Tiempo: número de días desde el primer caso

### Herramientas implementadas
Para lograr el objetivo en cuestión, se empleó el servicio de Google Cloud para crear y ejecutar una máquina virtual (VM) que utilice Ubuntu. Además, gracias a Cloud SQL se creó una base de datos PostgreSQL que contenga toda la información requerida para entrenar a los modelos.

Por otro lado, se empleó [MLflow](https://mlflow.org/). Este tiene un componente de tracking que permite registrar parámetros, versiones de código, métricas y archivos de salida al ejecutar el código. Además, tiene un componente de registry que permite comparar diferentes modelos y elegir cual queremos poner en producción.

Asimismo, se utilizó [Apache Airflow](https://airflow.apache.org/), una plataforma que permite monitorear flujos de trabajo. El mismo se empleó cómo scheduler.

### Pipelines de training, competition y deploy
Se creó un pipeline que ejecuta los siguientes tres pasos, uno por uno:

#### 1. Training
En primer lugar, se implementaron 5 modelos supervisados de clasificación utilizando la librería sklearn. Estos son:
1) Regresión Logistica CV
2) Random Forest
3) Gradient Boosting
4) AdaBoost
5) SVM

Estos modelos se loguean a la base de datos remota mencionada anteriormente. Para ello, fue necesario blanquear la IP con el firewall y levantar un servidor de MLflow.

#### 2. Competition
A continuación, se prosigue por seleccionar al mejor modelo de los entrenados previamente para registrarlo. En este caso el modelo seleccionado fue AdaBoostClassifier.

![image](https://github.com/tmonreal/Machine_Learning_II/assets/84754265/4a1fb9bc-f56c-498f-af38-d2df176ec540)

#### 3. Deploy
Finalmente, se selecciona el modelo que se encuentra en ese momento en producción y se lo sirve.

### Inferencias
Una vez que el modelo se encuentra deployado, se pueden hacer inferencias. Para que estas puedan ser externalizadas, se emplea una Cloud Function o función lambda cómo capa intermedia. La estructura de la función se puede ver a continuación:

![Screenshot from 2024-05-06 16-13-47](https://github.com/tmonreal/Machine_Learning_II/assets/84754265/9ac180ea-4e92-4da0-a1ca-feb73345706f)

La función “check_business_logic” se encarga de verificar ciertas heurísticas de negocio. Para este trabajo, se tomaron los máximos y mínimos del dataset cómo rangos aceptables. Si alguno de los features no cumple con las condiciones, se retorna una predicción de -1. 

Una vez deployada la función lambda, es posible testear dentro de Google Cloud. A continuación, se observa una imagen ilustrativa del testeo.

![image](https://github.com/tmonreal/Machine_Learning_II/assets/84754265/a51e44fb-1640-4d79-b471-2886c17730d7)

Además, es posible llamar a la función desde cualquier dispositivo que pueda hacer curl mediante una petición HTTPS. Por ejemplo, a continuación se observa el llamado desde la terminal de Windows.

![image](https://github.com/tmonreal/Machine_Learning_II/assets/84754265/fe895918-c523-49c7-9ad9-f56b214aebca)

#### Tablas de inferencias, ground truth y raw data

Se crearon tres tablas de manera automática utilizando alembic. Las migrations son queries de SQL que corren de forma automática, de este modo evitamos correrlas de forma manual. Las tablas creadas son:

1. Tabla de inferencias obtenidas.
2. Tabla de valores de ground truth.
3. Tabla de valores de los features usados para predecir.
   
Estas tres se unen mediante un parámetro (id) de tipo Uuid.

### Scheduling
Cómo último paso, se empleó Apache Airflow para correr el proceso cada 1 día de forma automática. El scheduler de Airflow se encarga de supervisar el DAG creado, y activa las diferentes instancias una vez que se completaron las dependencias. A continuación se puede observar el DAG que contiene en primer lugar el script de Python para entrenar los modelos, y en segundo lugar el script para seleccionar el que tiene mejor IBA.

![image](https://github.com/tmonreal/Machine_Learning_II/assets/84754265/3d76fb1d-5ab1-433d-a563-3851af09465f)

## 3. Conclusión
Se puede concluir que se logró entrenar y desplegar 5 modelos de aprendizaje automático en la nube empleando las técnicas aprendidas durante el curso. Debido a que nuestro trabajo de modelado tenía fines más bien educativos, es dificil de pensarlo cómo un producto que vaya a estar en producción. Sin embargo, nos ha servido para aprender las técnicas y poder aplicarlas en un futuro a otros modelos. 
