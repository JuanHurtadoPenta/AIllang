import os,json
from openai import  BadRequestError
from openai import OpenAI
import psycopg2
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import create_sql_query_chain
from operator import itemgetter
from DinamicEmpresa import ObtenerEmpresa#no mover el orden de la importacion
from TablasDinamicas import GetTablasSellecionadas
from DinamicEjemplosChroma1 import GetEjemploPrompt
from langchain_openai import ChatOpenAI
import re
from PosgressJega import add_question,add_response,add_sql_query,add_response_id

from dotenv import load_dotenv
# Ignorar todos los DeprecationWarning
# Cargar las variables de entorno desde el archivo .env
load_dotenv()
dir_VSEjemplos="/app/VectorStore/Ejemplos"
#dir_VSEjemplos="VectorStore/Ejemplos"
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

# infomracion encuentras aqui  https://www.youtube.com/watch?v=fss6CrmQU2Y&t=2510s
os.environ["OPENAI_API_KEY"] = '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'
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]="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"
os.environ["LANGCHAIN_ENDPOINT"]="https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"]="NL2SQL"
#######################################################3
### modelo estructurando mejor la data de infomracion sql
#############################################

def ObtenerDB():
    username = "dev_jhurtado" 
    password = "Pka12msE1b2qO%401"# "Pka12msE1b2qO@1" 
    host = "10.124.0.5"#"192.168.193.5" #"10.124.0.5"#
    port = "5432"
    mydatabase = "dbcorp"
    pg_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{mydatabase}"
    from langchain_community.utilities.sql_database import SQLDatabase
    # db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",sample_rows_in_table_info=1,include_tables=['customers','orders'],custom_table_info={'customers':"customer"})
    db = SQLDatabase.from_uri(pg_uri, view_support = True)
    return db
def EjecutarSQL(db):
    from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
    execute_query = QuerySQLDataBaseTool(db=db)
    return execute_query
def ejecutar_consulta(sql_query):
    try:
        # Conectarse a la base de datos PostgreSQL
        connection = psycopg2.connect(
            host="10.124.0.5",#"192.168.193.5",#"10.124.0.5",
            port="5432",
            dbname="dbcorp",
            user='dev_jhurtado',
            password="Pka12msE1b2qO@1"#'Pka12msE1b2qO%401'
        )
        # Crear un cursor para ejecutar la consulta
        cursor = connection.cursor()
        # Ejecutar la consulta SQL
        cursor.execute(sql_query)
        # Obtener el resultado de la consulta
        result = cursor.fetchall()
        # Cerrar la conexión
        cursor.close()
        connection.close()
        return result
    except Exception as error:
        print(f"Error al ejecutar la consulta: {error}")
        return None

def devolver_Analisis(human_query,tabla):
    print(tabla)
    print(human_query)
    #*Do not mention the SQL query  in your response
    prompt2=f"""
Assume the role of an expert financial data analyst with deep knowledge of SQL. Your goal is to **respond clearly and effectively** using the data obtained from an SQL query. The response must always be in JSON format, within the key "query_response".

<<BEGIN CONTEXT>>
giving the following data table:
{tabla}

<<END CONTEXT>>

My query is as follow: {human_query}

Before providing me with a response, carefully consider the following **OBSERVATIONS**:

 ***Analysis all the  column on the table and the values in there***

1.**Analyze the rows of the *`Tipo Estado`* column in the table and select the values based on the following conditions:**
    - ***If the value of *`Tipo Estado`* is 'ERI'***:
        - **Do not** take into account the *`Saldo Mensual`* column.
        - Exclusively extract the values from the *`Saldo Acumulado`* column.
        - Respond based on those values and explicitly state that the amount corresponds to *'saldo acumulado (acumulado nacional)'*.
    - ***If the value of *`Tipo Estado`* is 'ESF'***:
       - **Do not** take into account the *`Saldo Acumulado`* column.
       - Exclusively extract the values from the *`Saldo Mensual`* column.
       - Respond based on those values and explicitly state that the amount corresponds to *'saldo mensual (mensual nacional)'*.\n\nReturn the results in *JSON* format, ensuring that the selected column and the type of balance are clearly indicated, and exclude any value from the column that does not correspond to the state type."


   - Ensure the response clearly mentions whether the amount is based on *"saldo acumulado"* or *"saldo mensual"*, depending on the column from which the value was obtained.

2. **Maintain the signs of the values**: Ensure that the *numeric values retain their original signs in your respond*.

3. **Selection of the almacen**: If I do not mention a specific *almacen* in my query, use the data where `' Almacén Nombre'` is `'SIN ALMACEN'`.

4. **Comparatives for 'consolidado'**: If I mention 'consolidado', perform a comparison between the values of both dates.dont forget to use the values choused in the first point.
5. **Focus on 'balance general'**: When the query mentions *'balance general'*, concentrate specifically on the rows where the **`'nombre'`** is **`'ACTIVO'`**, **`'PASIVO'`**, or **`'PATRIMONIO'`**. Ensure you accurately utilize the values obtained in the first point. Your response should exclusively include the values for these categories without any additional commentary.
6. **Focus for 'ERI'**: If I mention 'ERI', focus on the values of `'Saldo Acumulado'` for `'VENTAS NETAS'`, `'VENTAS BRUTAS'`, `'UTILIDAD BRUTA'`, `'GASTOS OPERACIONALES'`, and `'UTILIDAD NETA'`.
7.**Perform the Calculation:**
   - If you need to calculate any value, make sure to follow the appropriate *procedure*.
   - Explain the *calculation process* clearly, including and mention  the specific *values* you used.
   - Indicate the *formula* or *method* you applied to arrive at the final result.

"""
    prompt3="""Your response MUST tu be in SPANISH and it should summarize the key findings in a conversational manner.Ensures that your respond be in a one string. For example:  
    ```json
    {
        "query_response": "TU RESPUESTA....."
    }
    """


    
    messages=[
                {"role": "system", "content": "Eres un experto en analitica de datos y ecomerces.Tu objetivo principal es tomar los datos obtenidos de una consulta de tu base de datos y analaizarlo para responder la consulta el cliente ."},
                {"role": "user", "content": prompt2+prompt3}#promptRespuestaFinal}#prompt2}
            ]
    #print(messages)
    #messages=VariosMensajes(result,messages)
    try:
        client = OpenAI(
            # This is the default and can be omitted
            #api_key='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'
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=3000,
            n=1,
            stop=None,
            temperature=0.4,
        )
        respuesta=chat_completion
        descripcion = respuesta.choices[0].message.content
        #print(descripcion)
        descripcion=extract_json(descripcion)
        #print(descripcion)
        response_json = json.loads(descripcion)
       # print("las condiciones son:"+str(response_json["Condiciones"]))
        Queryresponse= response_json["query_response"]
        #informe= response_json["informe"]
        respuestaT=Queryresponse#+"\n"+informe
        #print(Queryresponse)
    except  BadRequestError as e:
        if "maximum context length" in str(e):
            #Queryresponse=devolver_AnalisisLargo(result,human_query,SQL_query)
            respuestaT="La información que desea consultar es muy extensa como para mostrártela por este medio. Por favor, delimite mejor su consulta."
        else:
            raise  # Puedes seguir manejando otros errores aquí si es necesario

    return respuestaT

# Función para verificar y extraer la consulta SQL del texto
def extract_sql(text):
    # Verificar si la marca de código ```sql está presente en el texto
    if '```sql' in text:
        # Usar expresiones regulares para encontrar texto entre ```sql
        match = re.search(r'```sql\n(.*?)\n```', text, re.DOTALL)
        if match:
            return match.group(1).strip()  # Devolver el contenido sin espacios adicionales
    return text  # Devuelve None si no hay coincidencia o si no hay marca de código
def extract_json(text):
    # Buscar y eliminar todo lo que está antes de "SQLQuery:", incluyendo la propia frase
    indice = text.find("SQLQuery:")
    
    if indice != -1:
        # Cortar el texto para eliminar lo anterior a "SQLQuery:"
        text = text[indice + len("SQLQuery:"):]
    
    # Verificar si existe la marca ```json en el texto
    if '```json' in text:
        # Usar expresiones regulares para encontrar texto entre ```json y ```
        match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
        if match:
            return match.group(1).strip()  # Devolver el contenido sin espacios adicionales
    
    # Si no se encuentra JSON, retornar el texto limpio después de SQLQuery
    return text
    
def NL2SQL(input,id_usuario,canal):
    #list_tables(SCHEMA_NAME )
    id_question=add_question(canal, id_usuario,input)
    Empresas=ObtenerEmpresa(input)
    print("las empresas son"+str(Empresas))
    select_table=GetTablasSellecionadas()
    print( "va a obtener tablas")
    few_shot_prompt=GetEjemploPrompt(input)
    print("los ejemplos son:"+str(few_shot_prompt))
    db=ObtenerDB()#
    print( "obtuvo db")
    OriginalInput=input
    input=ExtaerNombre(input,Empresas)
    
    #print(few_shot_prompt)
    promptGenerarSQL=f"""
Eres un experto en SQL Queries para bases de datos PostgreSQL. Tu objetivo es crear una consulta SQL que permita extraer la información necesaria para responder a la pregunta  del usuario utilizando los ejemplos dados como referencia . Para esto quiero que **sigas mis instrucciones paso a paso Y PUNTO POR PUNTO ANALIZANDO BIEN CADA UNO DE ELLOS. **
Instrucciones:

1. **Analiza los ejemplos dados:** Compara la petición del usuario con los ejemplos proporcionados y busca similitudes en la estructura o los filtros aplicados.
   - Los ejemplos proporcionados son tu **guía principal** para construir la consulta.
   - Utiliza los *mismos filtros* de los ejemplos siempre que la solicitud del usuario sea similar.
   -**Obten todas las **columnas de salida**Parte del SELECT** en los ejemplos  y UTILIZALAS EN TU CONSULTA. **No OMITAS NINGUNA COLUMNA**, incluso si parecen irrelevantes para la nueva consulta.***NO UTILIZAR NINGUNA COLUMNA QUE NO ESTE EN LOS EJEMPLOS ***.
   -**INCLUIR SIEMPRE** **'sal_nombre'**y **'sal_tipo_estado'** en el  **las Columnas de salida **de tu consulta SQL.
2.  **Filtros,Columnas y condiciones obligatorias:**
   - **Debes incluir siempre** `sal_tipo=1` en **todas** tus consultas SQL.
   - Si la consulta **menciona explícitamente** 'presupuesto', usa el valor `2` para `sal_tipo`.
   - Si la consulta **menciona explícitamente** 'ERI' o 'estado de resultados integrales', incluye la columna `sal_tipo_estado` con el valor `'ERI'` en mayúsculas y incluye la columna sal_tipo_emp en el SELECT.
   - Si la consulta **menciona explícitamente** 'ESF', 'estado de situación financiera' o 'balance general', incluye la columna `sal_tipo_estado` con el valor `'ESF'` en mayúsculas y incluye la columna sal_tipo_emp en el SELECT.
   - ** LA Consulta  DEL CLIENTE MENCIONA la palabra **CONSOLIDADO**: Si la consulta incluye la palabra **consolidado**, realiza una **única consulta** que obtenga los ***datos para la fecha solicitada y para un año antes*** mediante ** sal_periodo IN ('año Actual', 'Año anterior')**, filtrando ambos periodos en la misma consulta.
   -**Nunca te inventes valores o respuestas que no esten dentro de la inofrmacion o que puedas calcular.
   ** si se realiza algun calculo explicalo detalladamente.
   
4. **Tratamiento de marcas diacríticas (acentos):**
   - Si en la consulta del usuario hay palabras con marcas diacríticas (como acentos), elimina dichas marcas al procesar la solicitud.
5. **Uso del esquema de la tabla:**
   - El esquema de la tabla solo debe usarse para determinar filtros y condiciones adicionales **si es necesario**, pero siempre se debe priorizar la estructura de los ejemplos proporcionados.

6. **Construcción de la consulta:**
   - Escribe una consulta SQL en PostgreSQL que recupere la información solicitada utilizando **solo** los nombres de columnas proporcionados en los ejemplos y ***tomando en cuenta todos los pasos anteriores.***
   - No añadas ni asumas ninguna condición, nombres de columnas o valores que no hayan sido mencionados explícitamente por el usuario.
   -**No te Inventes COLUMNAS**
   -**Siempre selecionar las columnas ** sal_valor_nac** , **sal_acumulado_nac** ,**Sal_tipo_estado**en tu consulta.**

7. **Salida de la consulta:**
   - La salida de la IA debe ser **solo el texto de la consulta SQL dentro de las marcas ```sql** sin ningún tipo de formato adicional, comentarios, bloques de código o caracteres especiales . 
   - **Es fundamental que la respuesta final sea exclusivamente la consulta SQL, optimizada y lista para ejecutarse en PostgreSQL, sin ninguna información adicional.**
8.***RESPUESTA FINAL: la salida de la consulta.***
Aquí está la información relevante de la tabla:

    """
    if  os.path.exists(dir_VSEjemplos):
        #print(" entro al prompt  de app\VectorStore\Ejemplos")
        promptGSQL = ChatPromptTemplate.from_messages(
            [
                #("system","You are a Posgres expert. Given an input question, create a syntactically correct Posgress query to run.you must first analyze the examples that will be provided in subsequent messages. Your responses should primarily be based on these examples. Identify the patterns, selected columns, and structures used in those examples and apply them to the new queries. Unless otherwise specificed.Write a SQL Postgres query that retrieves the requested information using **only** the provided column names. Do not add or assume any other conditions, column names, or values that are not explicitly mentioned by the user.\n\nYou **MUST include** sal_tipo=1 in ALL of your SQL Postgres queries. However, if the query explicitly mentions 'presupuesto', use the value 2 for sal_tipo.\n\nIf the query **explicitly mentions** 'ERI' or 'estado de resultados integrales', include the sal_tipo_estado column with the value 'ERI' in capital letters.\n\nIf the **query explicitly mentions** 'ESF', 'estado de situación financiera'  or 'balance general', include the sal_tipo_estado column with the value 'ESF' in capital letters.\n\nIf a company name is provided, perform a case-insensitive search using the ILIKE operator to match substrings. Ensure that **no additional filters** such as 'efectivo' or 'equivalente' are added unless explicitly requested by the user.\n\nAdditionally, if any words in the input question  contain diacritical marks (like accents), remove those marks.\n\nHere is the relevant table info: {table_info}\n\nGenerate an SQL query that selects only the relevant columns from the data, excluding those that should not be considered according to the following list: do not include (sal_codigo, saldo_nivel, sal_genero, sal_nombre_eeff, sal_negrita, sal_codigo_emp, sal_id, sal_indicador, sal_seg_codigo, sal_id_nivel1, sal_id_nivel2, sal_id_nivel3, sal_codigo_eeff, sal_calculo, sal_nombre_se, sal_codigo_cuenta, ref_fecha_actualizacion, sal_cen_id, sal_alm_id).\n\nBefore generating any SQL query, carefully analyze the provided examples and their corresponding SQL queries. **Your primary task is to replicate the patterns, column selections, and structures observed in these examples**. Only if the examples do not fully address the query, you may refer to the schema of the table to supplement the information, but **all selected columns must align with those used in the examples**. The schema should only be used to determine filters and additional conditions if necessary.\n\nRemember, the examples provided in other messages are your primary guide for constructing your responses.\n\n**Output the SQL query only** as plain text, without any additional characters, comments, or formatting. Do not use code blocks, backticks, or any other markup." ),
                ("system",promptGenerarSQL+"{table_info}"+"\n"+"{top_k}"+"ejemplos:"),
                few_shot_prompt,
                ("human", "{input}"),
            ]
        )
    else:
        promptGSQL = ChatPromptTemplate.from_messages(
            [
                #("system","You are a Posgres expert. Given an input question, create a syntactically correct Posgress query to run.you must first analyze the examples that will be provided in subsequent messages. Your responses should primarily be based on these examples. Identify the patterns, selected columns, and structures used in those examples and apply them to the new queries. Unless otherwise specificed.Write a SQL Postgres query that retrieves the requested information using **only** the provided column names. Do not add or assume any other conditions, column names, or values that are not explicitly mentioned by the user.\n\nYou **MUST include** sal_tipo=1 in ALL of your SQL Postgres queries. However, if the query explicitly mentions 'presupuesto', use the value 2 for sal_tipo.\n\nIf the query **explicitly mentions** 'ERI' or 'estado de resultados integrales', include the sal_tipo_estado column with the value 'ERI' in capital letters.\n\nIf the **query explicitly mentions** 'ESF', 'estado de situación financiera'  or 'balance general', include the sal_tipo_estado column with the value 'ESF' in capital letters.\n\nIf a company name is provided, perform a case-insensitive search using the ILIKE operator to match substrings. Ensure that **no additional filters** such as 'efectivo' or 'equivalente' are added unless explicitly requested by the user.\n\nAdditionally, if any words in the input question  contain diacritical marks (like accents), remove those marks.\n\nHere is the relevant table info: {table_info}\n\nGenerate an SQL query that selects only the relevant columns from the data, excluding those that should not be considered according to the following list: do not include (sal_codigo, saldo_nivel, sal_genero, sal_nombre_eeff, sal_negrita, sal_codigo_emp, sal_id, sal_indicador, sal_seg_codigo, sal_id_nivel1, sal_id_nivel2, sal_id_nivel3, sal_codigo_eeff, sal_calculo, sal_nombre_se, sal_codigo_cuenta, ref_fecha_actualizacion, sal_cen_id, sal_alm_id).\n\nBefore generating any SQL query, carefully analyze the provided examples and their corresponding SQL queries. **Your primary task is to replicate the patterns, column selections, and structures observed in these examples**. Only if the examples do not fully address the query, you may refer to the schema of the table to supplement the information, but **all selected columns must align with those used in the examples**. The schema should only be used to determine filters and additional conditions if necessary.\n\nRemember, the examples provided in other messages are your primary guide for constructing your responses.\n\n**Output the SQL query only** as plain text, without any additional characters, comments, or formatting. Do not use code blocks, backticks, or any other markup." ),
                ("system",promptGenerarSQL+"{table_info}"),
                few_shot_prompt,
                ("human", "{input}"),
            ]
        )
    generate_query = create_sql_query_chain(llm, db,promptGSQL)
    #RunnablePassthrough.assign(table_names_to_use=select_table) |
    chain = (
    RunnablePassthrough.assign(table_names_to_use=select_table) |
    RunnablePassthrough.assign(query=generate_query)
    )
    QuerySQL= chain.invoke({"question": input})
    QuerySQL=QuerySQL['query']
    #print(QuerySQL)
    QuerySQL=extract_sql( QuerySQL)
    QuerySQL=extract_json(QuerySQL)
    #print(QuerySQL)
    try:
        if id_question is not None:
            add_sql_query(id_question, QuerySQL, 1)
    except Exception as e:
        print(f"No se pudo agregar la consulta SQL a la base de datos: {e}")
    resultado=ejecutar_consulta(QuerySQL)
    print(input)
    print(QuerySQL)
    print(resultado)
    if not resultado:
        QueryResponse="Para poder darte una respuesta adecuada, por favor proporciona más detalles o verifica la información que estás consultando."
    else:
        tabla=tabla_string(QuerySQL,resultado)
        QueryResponse= devolver_Analisis(OriginalInput,tabla)
    id_pregunta=None
    try:
         if id_question is not None:
            id_pregunta=add_response_id( QueryResponse, id_question, 1)
            #add_response( QueryResponse, id_question, 1)
    except Exception as e:
        print(f"No se pudo agregar la la respuesta a la base de datos: {e}")
    return QueryResponse,id_pregunta

def ExtaerNombre(human_query,nombre_empresas):
    #*Do not mention the SQL query  in your response
    promptNombres=f"""

Dada la siguiente pregunta: "{human_query}", extrae el nombre de la empresa y compáralo con los nombres comerciales de la siguiente lista: {nombre_empresas}. 
Asegúrate de que la comparación sea correcta, siguiendo estos pasos:
1. Si encuentras una **coincidencia exacta** sin importar mayusculas o minusculas, responde con la pregunta original, pero reemplaza el nombre comercial con el nombre completo de la empresa correspondiente.
2. Si no hay coincidencia exacta, devuelve la pregunta original sin cambios.
Devuelve tu respuesta en formato JSON con la clave "nombre".
"""

    #print(promptNombres)

    
    messages=[
                {"role": "system", "content": "Eres experto en analizar preguntas y extraer infomracion de ellas ."},
                {"role": "user", "content": promptNombres}#promptRespuestaFinal}#prompt2}
            ]
    #print(messages)
    #messages=VariosMensajes(result,messages)
    try:
        client = OpenAI(
            # This is the default and can be omitted
            #api_key='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'
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=400,
            n=1,
            stop=None,
            temperature=0.1,
        )
        respuesta1=chat_completion
        descripcion1 = respuesta1.choices[0].message.content
        #print(descripcion)
        descripcion1=extract_json(descripcion1)
        #print(descripcion)
        response_json1 = json.loads(descripcion1)
       # print("las condiciones son:"+str(response_json["Condiciones"]))
        Queryresponse= response_json1["nombre"]
        #informe= response_json["informe"]
        nombre=Queryresponse#+"\n"+informe
        #print(Queryresponse)
    except  BadRequestError as e:
        if "maximum context length" in str(e):
            #Queryresponse=devolver_AnalisisLargo(result,human_query,SQL_query)
            nombre="No se pudo obtener nombre empresa"
        else:
            raise  # Puedes seguir manejando otros errores aquí si es necesario

    return nombre

def tabla_string(SQL_query,result):

        # Mapa de nombres de columnas a sus nuevos nombres
    header_mapping = {
        'sal_nombre': 'Nombre',
        'sal_tipo_estado': 'Tipo Estado',
        'sal_valor_nac': 'Saldo Mensual',
        'sal_valor_ext': 'Saldo Mensual Moneda Extranjera',
        'sal_acumulado_nac': 'Saldo Acumulado',
        'sal_acumulado_ext': 'Saldo Acumulado Moneda Extranjera',
        'sal_sector': 'Sector',
        'sal_alm_nombre': 'Almacén Nombre',
        'sal_mes': 'Mes',
        'sal_periodo': 'Año'
    }

    # Extraer encabezados de la consulta SQL
    match = re.search(r'SELECT\s+(.*?)\s+FROM', SQL_query, re.IGNORECASE)
    if match:
        original_headers = [header.strip() for header in match.group(1).split(',')]
        headers = [header_mapping.get(header, header) for header in original_headers]  # Reemplazar según el mapa
    else:
        headers = []

    # Generar el string de la tabla
    table_str = ' | '.join(headers) + '\n'  # Encabezados
    table_str += '-' * (len(headers) * 10) + '\n'  # Línea divisoria

    # Añadir filas de datos con separación
    for row in result:
        table_str += ' | '.join(f"{str(item):<10}" for item in row) + '\n'  # Formato alineado a la izquierda
        table_str += '-' * (len(headers) * 10) + '\n'  # Línea divisoria entre filas

    return table_str
def borrar():
    consultas = [
    " dame el   valor de activo de mayo 2024 de  KTM",
    " quiero el consolidado de ventas brutas de la empresa honda para febrero 2023",
    "Cual es el ERI de  royal motors para marzo 2024",
    "Quiero el valor EBITDA de  toscana para enero 2024 ",
    "Cual es el valor de Activo Corriente  de Aje Licores en el mes de febrero 2024",
    "Dame el valor de ventas brutas para   KTM de junio 2024",
    "Cual es  balance general de  inmot para febrero 2023.",
    "dame la diferencia de ventas netas del mes de enero de los años 2023 y 2024 de innmot"
    ]

    # Ejecutar la función para cada consulta
    for consulta in consultas:
        print("input:"+consulta)
        print(NL2SQL(consulta,1,1))
        #Empresas=ObtenerEmpresa(consulta)
        #print ("lista de empresas:"+Empresas)
        #print(ExtaerNombre(consulta,Empresas))
        print("--------------------------------------------")  # Aquí puedes modificar para ejecutar la consulta en tu base de datos en lugar de solo imprimirla.


#borrar()
#db=ObtenerDB()     
#print(connection)    
#execute_query = QuerySQLDataBaseTool(db=db)
#print(execute_query.invoke("SELECT COUNT(*) FROM eeff_saldos_v;"))
#input="Consultar las Devoluciones del año 2023 de la empresa honda."
#print(GetEjemploPrompt(input))
# Lista de consultas
# Aquí puedes modificar para ejecutar la consulta en tu base de datos en lugar de solo imprimirla.
#print(NL2SQL(" cual es el valor del  activo corriente de mayo 2024 de la empresa inmot",1,1))

#dame la diferencia de ventas netas del mes de enero de los años 2023 y 2024 de la empresa inmot
#print(ExtaerNombre(human_query,Empresas))