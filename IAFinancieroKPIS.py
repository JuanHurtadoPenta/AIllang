import os,json
from openai import  BadRequestError
from openai import OpenAI
import psycopg2
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import create_sql_query_chain
from operator import itemgetter
from DinamicEmpresa import ObtenerEmpresa,ObtenerEmpresa1#no mover el orden de la importacion
from TablasDinamicas import GetTablasSellecionadasKPIS
from DinamicEjemplosChroma1 import GetEjemploPromptKPIS
from langchain_openai import ChatOpenAI
import re
from datetime import datetime
from PosgressJega import add_question,add_response,add_sql_query,add_response_id

from dotenv import load_dotenv
# Ignorar todos los DeprecationWarning
# Cargar las variables de entorno desde el archivo .env
load_dotenv()
dir_VSEjemplos="/app/VectorStore/EjemplosKPIS"
#dir_VSEjemplos="VectorStore/EjemplosKPIS"
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
            host="10.124.0.5",#"192.168.193.5",#"10.124.0.5",#
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
def procesar_tabla_Columna_correctaKPI(pregunta, tabla):
    # Separar las líneas de la tabla
    filas = tabla.strip().split("\n")
    
    # Extraer los encabezados y las filas de datos
    encabezados = filas[0].split("|")
    encabezados = [encabezado.strip() for encabezado in encabezados]  # Limpiar espacios
    
    # Determinar la columna a eliminar
    if "acumulado" in pregunta.lower() or "acumulada" in pregunta.lower():
        columna_a_eliminar = "valor"
    else:
        columna_a_eliminar = "valor Acumulado"
    
    # Verificar que la columna a eliminar exista
    try:
        posicion_columna = encabezados.index(columna_a_eliminar)
    except ValueError:
        raise ValueError(f"La columna '{columna_a_eliminar}' no se encontró en los encabezados de la tabla.")
    
    # Reconstruir la tabla eliminando la columna en esa posición
    nueva_tabla = []
    for fila in filas:
        valores = fila.split("|")
        valores = [valor.strip() for valor in valores]  # Limpiar espacios
        # Eliminar la columna correspondiente
        nueva_fila = [valores[i] for i in range(len(valores)) if i != posicion_columna]
        nueva_tabla.append(" | ".join(nueva_fila))
    
    # Unir las filas modificadas para formar la tabla actualizada
    return "\n".join(nueva_tabla)
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
    
def NL2SQLKPI(input,id_usuario,canal,id_padre):
    id_question=add_question(canal, id_usuario,input,id_padre)
    select_table=GetTablasSellecionadasKPIS()
    few_shot_prompt=GetEjemploPromptKPIS(input)
    print("los ejemplos son:"+str(few_shot_prompt))
    db=ObtenerDB()#
    print( "obtuvo db")
    OriginalInput=input
    input=ExtaerNombre(input)
    
    #print(few_shot_prompt)
    promptGenerarSQL=f"""
Eres un experto en SQL Queries para bases de datos PostgreSQL. Tu objetivo es crear una consulta SQL que permita extraer la información necesaria para responder a la pregunta  del usuario utilizando los ejemplos dados como referencia . Para esto quiero que **sigas mis instrucciones paso a paso Y PUNTO POR PUNTO ANALIZANDO BIEN CADA UNO DE ELLOS. **
Instrucciones:

1. **Analiza los ejemplos dados:** Compara la petición del usuario con los ejemplos proporcionados y busca similitudes en la estructura o los filtros aplicados.
   - Los ejemplos proporcionados son tu **guía principal** para construir la consulta.
   - Utiliza los *mismos filtros* de los ejemplos siempre que la solicitud del usuario sea similar.
   -**Obten todas las **columnas de salida**Parte del SELECT** en los ejemplos  y UTILIZALAS EN TU CONSULTA. **No OMITAS NINGUNA COLUMNA**, incluso si parecen irrelevantes para la nueva consulta.***NO UTILIZAR NINGUNA COLUMNA QUE NO ESTE EN LOS EJEMPLOS ***.
2.  **Filtros,Columnas y condiciones obligatorias:**
   - **Debes incluir siempre** `sal_tipo=1` en **todas** tus consultas SQL.
   - Si la consulta **menciona explícitamente** 'presupuesto', usa el valor `2` para `sal_tipo`.
   -***Nunca te inventes valores o respuestas que no esten dentro de la inofrmacion o que puedas calcular.**
   ** si se realiza algun calculo explicalo detalladamente.
   -*si la consulta es sobre EVITDA entoces agregar  la columna **sal_nombre_indicador al select.**

4. **Tratamiento de marcas diacríticas (acentos):**
   - Si en la consulta del usuario hay palabras con marcas diacríticas (como acentos o tildes ),No elimines dichas marcas al procesar la solicitud.
5. **Uso del esquema de la tabla:**
   - El esquema de la tabla solo debe usarse para determinar filtros y condiciones adicionales **si es necesario**, pero siempre se debe priorizar la estructura de los ejemplos proporcionados.

6. **Construcción de la consulta:**
   - Escribe una consulta SQL en PostgreSQL que recupere la información solicitada utilizando **solo** los nombres de columnas proporcionados en los ejemplos y ***tomando en cuenta todos los pasos anteriores.***
   - No añadas ni asumas ninguna condición, nombres de columnas o valores que no hayan sido mencionados explícitamente por el usuario.
   -**No te Inventes nombres de  COLUMNAS en el select o los filtros,usa solo las dadas en los ejemplos**
   -**Siempre selecionar las columnas ** sal_porcentaje_val** , **sal_porcentaje_acu** en tu consulta.**
   para la busqueda del indicador(columna sal_nombre_indicador) has una busqueda insesible a mayuscualas y minusculas siempre usa  ILIKE '%...%';

7. **Salida de la consulta:**
   - La salida de la IA debe ser **solo el texto de la consulta SQL dentro de las marcas ```sql** sin ningún tipo de formato adicional, comentarios, bloques de código o caracteres especiales . 
   - **Es fundamental que la respuesta final sea exclusivamente la consulta SQL, optimizada y lista para ejecutarse en PostgreSQL, sin ninguna información adicional.**
8.***RESPUESTA FINAL: la salida de la consulta.***
Aquí está la información relevante de la tabla:

    """
    if  os.path.exists(dir_VSEjemplos):
        print(" entro al prompt  de app\VectorStore\Ejemplos")
        promptGSQL = ChatPromptTemplate.from_messages(
            [
                #("system","You are a Posgres expert. Given an input question, create a syntactically correct Posgress query to run.you must first analyze the examples that will be provided in subsequent messages. Your responses should primarily be based on these examples. Identify the patterns, selected columns, and structures used in those examples and apply them to the new queries. Unless otherwise specificed.Write a SQL Postgres query that retrieves the requested information using **only** the provided column names. Do not add or assume any other conditions, column names, or values that are not explicitly mentioned by the user.\n\nYou **MUST include** sal_tipo=1 in ALL of your SQL Postgres queries. However, if the query explicitly mentions 'presupuesto', use the value 2 for sal_tipo.\n\nIf the query **explicitly mentions** 'ERI' or 'estado de resultados integrales', include the sal_tipo_estado column with the value 'ERI' in capital letters.\n\nIf the **query explicitly mentions** 'ESF', 'estado de situación financiera'  or 'balance general', include the sal_tipo_estado column with the value 'ESF' in capital letters.\n\nIf a company name is provided, perform a case-insensitive search using the ILIKE operator to match substrings. Ensure that **no additional filters** such as 'efectivo' or 'equivalente' are added unless explicitly requested by the user.\n\nAdditionally, if any words in the input question  contain diacritical marks (like accents), remove those marks.\n\nHere is the relevant table info: {table_info}\n\nGenerate an SQL query that selects only the relevant columns from the data, excluding those that should not be considered according to the following list: do not include (sal_codigo, saldo_nivel, sal_genero, sal_nombre_eeff, sal_negrita, sal_codigo_emp, sal_id, sal_indicador, sal_seg_codigo, sal_id_nivel1, sal_id_nivel2, sal_id_nivel3, sal_codigo_eeff, sal_calculo, sal_nombre_se, sal_codigo_cuenta, ref_fecha_actualizacion, sal_cen_id, sal_alm_id).\n\nBefore generating any SQL query, carefully analyze the provided examples and their corresponding SQL queries. **Your primary task is to replicate the patterns, column selections, and structures observed in these examples**. Only if the examples do not fully address the query, you may refer to the schema of the table to supplement the information, but **all selected columns must align with those used in the examples**. The schema should only be used to determine filters and additional conditions if necessary.\n\nRemember, the examples provided in other messages are your primary guide for constructing your responses.\n\n**Output the SQL query only** as plain text, without any additional characters, comments, or formatting. Do not use code blocks, backticks, or any other markup." ),
                ("system",promptGenerarSQL+"{table_info}"+"\n"+"{top_k}"+"ejemplos:"),
                few_shot_prompt,
                ("human", "{input}"),
            ]
        )
    else:
        print(" NOOOO entro al prompt  de app\VectorStore\Ejemplos")
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
    print(QuerySQL)
    try:
        if id_question is not None:
            add_sql_query(id_question, QuerySQL, 1)
    except Exception as e:
        print(f"No se pudo agregar la consulta SQL a la base de datos: {e}")
    #QuerySQL=reemplazar_fechas(QuerySQL)
    QuerySQL_new=filtrar_fecha(QuerySQL)
    if QuerySQL_new == "La fecha que quieres consultar no tenemos en valores reales porque es mayor o igual a la fecha de hoy. Si quieres en presupuesto, vuelve a hacer tu consulta incluyendo que buscas el presupuesto.":
        QueryResponse=QuerySQL_new
    else:
        resultado=ejecutar_consulta(QuerySQL_new)
        print(input)
        print(QuerySQL_new)
        print(resultado)
        if not resultado:
            QuerySQL= chain.invoke({"question": ExtaerNombreKPI(QuerySQL_new)})
            QuerySQL=QuerySQL['query']
            #print(QuerySQL)
            QuerySQL=extract_sql( QuerySQL)
            QuerySQL=extract_json(QuerySQL)
            print(QuerySQL)
            try:
                if id_question is not None:
                    add_sql_query(id_question, QuerySQL, 1)
            except Exception as e:
                print(f"No se pudo agregar la consulta SQL a la base de datos: {e}")
            #QuerySQL=reemplazar_fechas(QuerySQL)
            QuerySQL_new=filtrar_fecha(QuerySQL)
            resultado=ejecutar_consulta(QuerySQL_new)
        if not resultado:
            QueryResponse="notifica al usuario que se lo busco como 'KPI' pero que no se obtuvo resultados,dile que Para poder darte una respuesta adecuada sobre este 'KPI', por favor proporciona más detalles o verifica la información que me estas solicitando consultando."
        else:
            tabla=tabla_string(QuerySQL,resultado)
            tabla=procesar_tabla_Columna_correctaKPI(input, tabla)
            #tabla=devolver_Analisis(input,tabla)
            print(tabla)
            filtros=extraer_filtros(QuerySQL)
            QueryResponse=" Para extraer la inoformacion se usaron los siguientes filtros: " +filtros+"\n obteniendo como resultado:\n"+tabla#devolver_Analisis(OriginalInput,tabla)

    id_pregunta=None
    try:
         if id_question is not None:
            id_pregunta=add_response_id( QueryResponse, id_question, 1)
    except Exception as e:
        print(f"No se pudo agregar la la respuesta a la base de datos: {e}")
    return QueryResponse,id_pregunta
from datetime import datetime, timedelta
import re

def reemplazar_fechas(sql_text):
    # Obtener la fecha actual
    hoy = datetime.now()
    # Crear diccionario con los reemplazos
    reemplazos = {
        "año actual": hoy.year,
        "año anterior": hoy.year - 1,
        "año siguiente": hoy.year + 1,
        "mes actual": hoy.strftime("%Y-%m"),
        "mes anterior": (hoy.replace(day=1) - timedelta(days=1)).strftime("%Y-%m"),
        "mes siguiente": (hoy.replace(day=28) + timedelta(days=4)).replace(day=1).strftime("%Y-%m")
    }

    # Reemplazar cada término en el texto SQL
    for termino, valor in reemplazos.items():
        # Usamos re.escape para evitar conflictos con caracteres especiales en las palabras clave
        sql_text = re.sub(re.escape(termino), str(valor), sql_text, flags=re.IGNORECASE)

    return sql_text
def  ExtaerNombre(human_query):
    human_query=human_query.lower()
    nombre_empresas_ai=ExtraerNombreIA(human_query)
    nombre_empresas=ObtenerEmpresa1(nombre_empresas_ai)
    print("las empresas son"+str(nombre_empresas))
    if nombre_empresas is None:
        return human_query
    nombre_empresas=nombre_empresas.lower()
    print(nombre_empresas)
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
        print(descripcion1)
        response_json1 = json.loads(descripcion1)
       # print("las condiciones son:"+str(response_json["Condiciones"]))
        Queryresponse= response_json1["nombre"]
        print("ultima respuesta"+str(Queryresponse))
        #informe= response_json["informe"]
        if Queryresponse==None:
            print("aqui")
            return human_query
        elif Queryresponse=="None":
            print("aqui2")
            return human_query
        else:
            nombre=Queryresponse#+"\n"+informe
        #print(Queryresponse)
    except  BadRequestError as e:
            #Queryresponse=devolver_AnalisisLargo(result,human_query,SQL_query)
            nombre="No se pudo obtener nombre empresa"

    return nombre
def ExtraerNombreIA(human_query):
    nombre=None
    print(human_query)
    #*Do not mention the SQL query  in your response
    prompt2=f"""
    dada la siguiente frase:
    {human_query}
    cual es el nombre de la empresa( debe ser una palabra completa ):
    ***Siempre**respondeme en formato json con la clave "Nombre" y si no logras indentificar el nombre ,dentro de clave pon none***
    ejemplo de respuesta:"""
    prompt3=""""
    ```json
    {
    "Nombre": "inmot"
    }
    ```json
    {
    "Nombre": "none"
    }"""
    
    messages=[
                {"role": "system", "content": " Eres experto extrayendo infomracion de frases ."},
                {"role": "user", "content": prompt2 +prompt3}#promptRespuestaFinal}#prompt2}
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
            temperature=0.2,
        )
        respuesta=chat_completion
        descripcion = respuesta.choices[0].message.content
        print(descripcion)
        descripcion=extract_json(descripcion)
        print(descripcion)
        response_json = json.loads(descripcion)
       # print("las condiciones son:"+str(response_json["Condiciones"]))
        Queryresponse= response_json["Nombre"]
        #informe= response_json["informe"]
        nombre=Queryresponse#+"\n"+informe
    except  BadRequestError as e:
            nombre=None # Puedes seguir manejando otros errores aquí si es necesario
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
        'sal_sector': 'Cluster',
        'sal_alm_nombre': 'Almacén Nombre',
        'sal_mes': 'Mes',
        'sal_periodo': 'Año',
        'sal_porcentaje_val AS porcentaje':'valor',
        'sal_porcentaje_acu AS porcentaje_acumulado':'valor Acumulado',
        'sal_porcentaje_val ':'valor',
        'sal_porcentaje_acu ':'valor Acumulado',
    }

    # Extraer encabezados de la consulta SQL
    match = re.search(r'SELECT\s+(.*?)\s+FROM', SQL_query, re.IGNORECASE)
    if match:
        # Procesa cada encabezado eliminando funciones como SUM(...) y conservando solo el nombre
        original_headers = [
            re.sub(r'SUM\([^\)]+\)\s+AS\s+', '', header.strip()) for header in match.group(1).split(',')
        ]
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


def filtrar_fecha(consulta_base):
    # Obtener el año y mes actuales
    fecha_actual = datetime.now()
    anio_actual = fecha_actual.year
    mes_actual = fecha_actual.month

    # Extraer el valor de sal_tipo de la consulta
    sal_tipo_match = re.search(r'sal_tipo\s*=\s*(\d+)', consulta_base)
    # Extraer el año de la consulta
    anio_match = re.search(r'sal_periodo\s*=\s*(\d+)', consulta_base)
    # Verificar si sal_mes está presente
    mes_match = re.search(r'sal_mes\s*=\s*(\d+)', consulta_base)

    # Verificar si se encontró sal_tipo y si es igual a 1
    if sal_tipo_match and sal_tipo_match.group(1) == '1':
        print("coincide sal tipo1")
        # Obtener el año de la consulta
        if anio_match:
            anio_consulta = int(anio_match.group(1))
            # Comprobar si sal_mes está presente
            if mes_match:
                print("coincide sal mes")
                mes_consulta = int(mes_match.group(1))
                # Comprobar si la fecha es mayor o igual a la actual
                if (anio_consulta > anio_actual or 
                    (anio_consulta == anio_actual and mes_consulta >= mes_actual)):
                    mensaje = "La fecha que quieres consultar no tenemos en valores reales porque es mayor o igual a la fecha de hoy. Si quieres en presupuesto, vuelve a hacer tu consulta incluyendo que buscas el presupuesto."
                    return mensaje
                else:
                    # Extraer la parte antes y después de WHERE
                    before_where, after_where = consulta_base.split("WHERE", 1)

                    # Construir la nueva condición considerando el año y el mes
                    nueva_condicion = f"(sal_periodo < {anio_actual} OR (sal_periodo = {anio_actual} AND sal_mes < {mes_actual})) AND "
                    
                    # Combinar las partes para crear la nueva consulta
                    consulta_base = f"{before_where}WHERE {nueva_condicion}{after_where}"

            else:
                print("no tiene mes de filtro")
                # Si sal_mes no está presente, agregar la condición para meses anteriores
                before_where, after_where = consulta_base.split("WHERE", 1)
                nueva_condicion = f"(sal_periodo < {anio_actual} OR (sal_periodo = {anio_actual} AND sal_mes < {mes_actual})) AND "
                consulta_base = f"{before_where}WHERE {nueva_condicion}{after_where}"
        else:
                print("no tiene año de filtro")
                # Si sal_mes no está presente, agregar la condición para meses anteriores
                before_where, after_where = consulta_base.split("WHERE", 1)
                nueva_condicion = f"(sal_periodo < {anio_actual} OR (sal_periodo = {anio_actual} AND sal_mes < {mes_actual})) AND "
                consulta_base = f"{before_where}WHERE {nueva_condicion}{after_where}"

    return consulta_base

def extraer_filtros(sql_query):
    # Expresión regular para capturar todo lo que está después de WHERE hasta el final de la consulta
    where_clause = re.search(r"WHERE\s+(.*)", sql_query, re.IGNORECASE)

    if where_clause:
        # Dividir filtros por AND
        filtros = re.split(r"\s+AND\s+", where_clause.group(1), flags=re.IGNORECASE)
        print(filtros)  # Imprimir filtros antes de excluir 'sal_nombre_emp'

        # Excluir 'sal_nombre_emp' de los filtros
        filtros = [filtro for filtro in filtros if 'sal_nombre_emp' not in filtro.lower()]

        # Formatear y mostrar filtros individuales
        filtros_formateados = "\n".join([f"- {filtro.strip()}" for filtro in filtros])
    else:
        filtros_formateados = "No se encontraron filtros."

    # Resultado final
    return f"**Filtros Extraídos:**\n{filtros_formateados}"

def  ExtaerNombreKPI(human_query):
    print("")
    human_query=human_query.lower()
    promptNombres = f"""
   Eres un asistente experto en detección y corrección de nombres de indicadores financieros.

**Objetivo**:  
Los usuarios hacen consultas sobre KPI o indicadores financieros, pero no saben cómo están guardados exactamente estos nombres en nuestra lista oficial. Tu tarea es:  
1. Identificar si la consulta del usuario hace referencia a algún KPI de la lista oficial.  
2. Si encuentras un KPI coincidente, **reescribe toda la pregunta del usuario**, reemplazando el nombre del KPI mencionado por el **nombre exacto** de la lista oficial.  
3. Si no encuentras ningún KPI coincidente, devuelve la pregunta original sin cambios.  

**Pregunta del usuario**:  
"{human_query}"  

**Lista oficial de indicadores o KPI**:  
1. Ciclo de efectivo ($ día)  
2. Apalancamiento Patrimonio  
3. Capital Neto de Trabajo  
4. % Utilidad Operacional  
5. Rotación Inventarios  
6. % Gastos de Logística  
7. Liquidez Corriente  
8. % Utilidad Neta  
9. Rotación cuentas por pagar  
10. % Gastos Administrativos  
11. Prueba Ácida  
12. % Costo de Venta  
13. % Margen Bruto  
14. % Gastos de Ventas  
15. ROA  
16. Ciclo de efectivo (días)  
17. Período medio de cobro  
18. ROE (Duppont)  
19. % Gastos No Operacionales  
20. % EBITDA  
21. % Gastos de Publicidad  
22. Días de Inventario (días)  
23. Capital Invertido  
24. % Gastos Operacionales  
25. Deuda/Ebitda  
26. Razón Endeudamiento  
27. Cobertura Intereses  
28. Período medio de pago (días)  
29. % Venta Neta  
30. Rotación Cartera  



**Reglas estrictas para tu respuesta**:  
1. Tu respuesta siempre debe devolver la **pregunta completa** en formato JSON, dentro de una clave llamada `nombre`.  
2. No respondas con solo el nombre del KPI.  
3. Si corregiste el nombre del KPI, asegúrate de integrarlo correctamente en el contexto de la pregunta original.  
4. Si no hay coincidencia, devuelve la pregunta original sin cambios.  

**Formato esperado de salida**:  
Tu respuesta debe estar en formato JSON con una sola clave `nombre`, que contenga la pregunta completa como un string unico  

**Ejemplo de entrada y salida**:  


    Ejemplo:
    Entrada:
    Pregunta: "¿Cuál es el período medio de cobros de los meses del año 2023 de la empresa KTM?"

    Salida esperada:
    """

    promptNombres2=""" 
    ```json
    {
        "nombre": "¿Cuál es el Período medio de cobro de los meses del año 2023 de la empresa KTM?"
    }

    Salida Incorrecta:
    ```json
    {
        "nombre": " Período medio de cobro (días)"
    }
    """

    #print(promptNombres)

    
    messages=[
                {"role": "system", "content": "Eres experto en analizar preguntas ycorreguir infomracion ."},
                {"role": "user", "content": promptNombres+promptNombres2}#promptRespuestaFinal}#prompt2}
            ]
    try:
        client = OpenAI(
            # This is the default and can be omitted
            #api_key='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'
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.2,
        )
        respuesta1=chat_completion
        descripcion1 = respuesta1.choices[0].message.content
        #print(descripcion)
        descripcion1=extract_json(descripcion1)
        print(descripcion1)
        response_json1 = json.loads(descripcion1)
       # print("las condiciones son:"+str(response_json["Condiciones"]))
        Queryresponse= response_json1["nombre"]
        Queryresponse = Queryresponse.replace("('", "").replace("',)", "")

        print("ultima respuesta"+str(Queryresponse))
        #informe= response_json["informe"]
        if Queryresponse==None:
            print("aqui")
            return human_query
        elif Queryresponse=="None":
            print("aqui2")
            return human_query
        else:
            nombre=Queryresponse#+"\n"+informe
        #print(Queryresponse)
    except  BadRequestError as e:
            print(e)
            #Queryresponse=devolver_AnalisisLargo(result,human_query,SQL_query)
            nombre=human_query

    return nombre

def borrar():
    consultas = [
    " dame el   valor de activo total de mayo 2024 de  KTM",
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
        print(NL2SQL(consulta,1,1,""))
        #Empresas=ObtenerEmpresa(consulta)
        #print ("lista de empresas:"+Empresas)
        #print(ExtaerNombre(consulta,Empresas))
        print("--------------------------------------------")  # Aquí puedes modificar para ejecutar la consulta en tu base de datos en lugar de solo imprimirla.
#consulta = "cual es el margen bruto de la empresa en ese mes "

#print(NL2SQLKPI(consulta,1,1,""))
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