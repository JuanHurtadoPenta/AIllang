import os,json
from openai import  BadRequestError
from openai import OpenAI
import psycopg2
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import create_sql_query_chain
from operator import itemgetter
from DinamicEmpresa import ObtenerEmpresa,ObtenerEmpresa1#no mover el orden de la importacion
from TablasDinamicas import GetTablasSellecionadas
from DinamicEjemplosChroma1 import GetEjemploPrompt
from langchain_openai import ChatOpenAI
import re
from datetime import datetime
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
    host = "192.168.193.5" #"10.124.0.5"#
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
            host="192.168.193.5",#"10.124.0.5",
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

4. **Comparatives for 'Consolidado'**: If I mention *'consolidado'* in my question, perform a comparison between the values of both dates.dont forget to use the values choused in the first point.
5. **Focus on 'balance general'**: When the query mentions *'balance general'*, concentrate specifically on the rows where the **`'nombre'`** is **`'ACTIVO'`**, **`'PASIVO'`**, or **`'PATRIMONIO'`**. Ensure you accurately utilize the values obtained in the first point. Your response should exclusively include the values for these categories without any additional commentary.
6. **Focus for 'ERI'**: If I mention 'ERI', focus on the values of `'Saldo Acumulado'` for `'VENTAS NETAS'`, `'VENTAS BRUTAS'`, `'UTILIDAD BRUTA'`, `'GASTOS OPERACIONALES'`, and `'UTILIDAD NETA'`.
7.**Perform the Calculation:**
   - If you need to calculate any value, make sure to follow the appropriate *procedure*.
   - Explain the *calculation process* clearly, including and mention  the specific *values* you used.
   - Indicate the *formula* or *method* you applied to arrive at the final result.
8.**Narrative respond**:
    -Ensure the response is always in **narrative text** format, even when reporting multiple values. 

"""
    prompt3="""Your response MUST tu be in SPANISH and it should summarize the key findings in a conversational manner .Ensures that your respond be in a one string. For example:  
    ```json
    {
        "query_response": "TU RESPUESTA....."
    }
    """

    promptsystem="""Eres un experto en analítica de datos y ecommerces. Tu objetivo principal es tomar los datos obtenidos de una consulta de tu base de datos y analizarlos para responder la consulta del cliente. Además, debes seguir estas instrucciones adicionales para responder preguntas relacionadas con estados financieros:

1. **Responde siempre usando emojis y flechas** para delimitar mejor tu mensaje, en lugar de usar saltos de línea.- Antes de responder, **identifica si el elemento solicitado pertenece al Balance General (Estado de Situación Financiera - ESF) o al Estado de Resultados Integral (ERI)**. 

2. **Balance General (ESF)**: Cuando te consulte sobre 'balance general', 'Estado de Situación Financiera (ESF)' o cualquier elemento de este, enfócate principalmente en los siguientes componentes:
   - **Activo**:
     - Activo Corriente: Efectivo y Equivalentes de efectivo, Cuentas por cobrar CP, Otras cuentas por cobrar, Inventarios disponible para la venta, Inventarios en tránsito, Servicios y otros pagos anticipados, Activos por impuestos corrientes, Anticipos a Proveedores, Otros activos corrientes.
     - Activo No Corriente: Propiedad, planta y equipo, (-) Depreciación Acumulada, Inversiones LP, Activos por derecho de uso, Otros activos no corrientes.
   - **Pasivo**:
     - Pasivo Corriente: Proveedores, Otras cuentas por pagar, Obligaciones con instituciones financieras CP, Provisiones, Administración Tributaria, I.E.S.S., Beneficios de Ley Empleados, Anticipos clientes, Otros pasivos corrientes.
     - Pasivo No Corriente: Obligaciones con instituciones financieras LP, Cuentas por pagar diversas/Relacionadas, Provisiones por Beneficios de Ley Empleados, Pasivos por derecho de uso, Otros pasivos no corrientes.
   - **Patrimonio**:
     - Capital, Reservas, Resultados Acumulados, Resultados del Ejercicio.

   Recuerda que el valor de **Activo**, **Pasivo** y **Patrimonio** ya representa la **suma de todos los valores** que lo componen. Al mencionar cualquiera de estos elementos, enfócate en proporcionar el valor de **'saldo mensual'**.

3. **Estado de Resultados Integral (ERI)**: Al solicitar el **Estado de Pérdidas y Ganancias**, trátalo como una consulta sobre el **Estado de Resultados Integral (ERI)**. Los elementos clave del ERI son:
   - **Ventas Netas**:
     - Ventas Brutas, Descuentos.
   - **Costo de Ventas**.
   - **Utilidad Bruta**.
   - **Gastos Operacionales**: Gastos Administrativos, Gastos Generales Adm, Sueldos y Salarios Adm, Gastos Ventas, Gastos Generales Ven, Sueldos y Salarios Ven, Gastos Publicidad, Gastos Generales Pub, Gastos Logística, Gastos Generales Log, Gastos Producción, Sueldos y Salarios Prod.
   - **Utilidad Operacional**.
   - **Otros No Operacionales**: Otros Gastos, Gastos Financieros, Otros Gastos No Operacionales, Otros Ingresos, Ingresos Financieros, Otros Ingresos No Operacionales.
   - **Utilidad antes de Impuestos y Proyectos**, **Utilidad antes de Impuestos**, **Utilidad Neta**.

   En cualquier consulta del ERI, proporciona los valores **acumulados** de estos elementos.

4. **Terminología adicional**: Si se consulta sobre algún otro estado financiero, asegúrate de preguntar si la referencia es mensual o acumulada para dar una respuesta precisa.

5. **Consolidación**: Si se menciona **'consolidado'**, realiza una **comparativa entre el valor solicitado con el del año anterior**. Asegúrate de destacar las diferencias clave en la respuesta.

Tu objetivo es proporcionar información financiera clara y detallada, además de analizar los datos de e-commerce para satisfacer las necesidades del cliente."
"""
    
    messages=[
                {"role": "system", "content":promptsystem},
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
    
def NL2SQL(input,id_usuario,canal,id_padre):
    #list_tables(SCHEMA_NAME )
    id_question=add_question(canal, id_usuario,input,id_padre)
    select_table=GetTablasSellecionadas()
    print( "va a obtener tablas")
    few_shot_prompt=GetEjemploPrompt(input)
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
   -**INCLUIR SIEMPRE** **'sal_nombre'**y **'sal_tipo_estado'** en el  **las Columnas de salida **de tu consulta SQL.
2.  **Filtros,Columnas y condiciones obligatorias:**
   - **Debes incluir siempre** `sal_tipo=1` en **todas** tus consultas SQL.
   - Si la consulta **menciona explícitamente** 'presupuesto', usa el valor `2` para `sal_tipo`.
   - Si la consulta **menciona explícitamente** 'activo total'* buscalo solo como'Activo'* en tu consulta.
    - Si la consulta **menciona explícitamente** 'pasivo total'* buscalo solo como'Pasivo'* en tu consulta.
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
            QueryResponse="Para poder darte una respuesta adecuada, por favor proporciona más detalles o verifica la información que me estas solicitando consultando."
        else:
            tabla=tabla_string(QuerySQL,resultado)
            filtros=extraer_filtros(QuerySQL)
            QueryResponse=" Para extraer la inoformacion se usaron los siguientes filtros: " +filtros+"\n obteniendo como resultado:\n"+tabla#devolver_Analisis(OriginalInput,tabla)
    id_pregunta=None
    try:
         if id_question is not None:
            id_pregunta=add_response_id( QueryResponse, id_question, 1)
            #add_response( QueryResponse, id_question, 1)
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
        'sal_periodo': 'Año'
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
    # Extraer filtros dentro del WHERE
    where_clause = re.search(r"WHERE\s+(.*?)\s+GROUP BY", sql_query, re.IGNORECASE)
    
    if where_clause:
        # Dividir filtros por AND (suponiendo que están separados por AND)
        filtros = re.split(r"\s+AND\s+", where_clause.group(1), flags=re.IGNORECASE)
    else:
        filtros = []

    # Excluir 'sal_nombre_emp' de los filtros
    filtros = [filtro for filtro in filtros if 'sal_nombre_emp' not in filtro.lower()]

    # Formatear y mostrar filtros individuales
    filtros_formateados = "\n".join([
        f"- {filtro.strip()}" for filtro in filtros
    ])
    
    # Resultado final
    resultado = f"**Filtros Extraídos:**\n{filtros_formateados if filtros else 'No se encontraron filtros.'}"
    return resultado
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
consulta = " dame el   valor de activo de mayo 2024 de  KTM pero acumulado"

#print(NL2SQL(consulta,1,1,""))
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