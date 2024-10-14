import os,json
import openai 
from openai import  BadRequestError
from openai import OpenAI
import psycopg2
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import create_sql_query_chain
from operator import itemgetter
import TablasDinamicas,DinamicEjemplosChroma
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
import warnings
from langchain_chroma import Chroma
from dotenv import load_dotenv
# Ignorar todos los DeprecationWarning
# Cargar las variables de entorno desde el archivo .env
load_dotenv()
# Configuración de la API de OpenAI y LangChain
#openai.api_key = os.getenv("OPENAI_API_KEY")
#warnings.filterwarnings("ignore", category=DeprecationWarning)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
# infomracion encuentras aqui  https://www.youtube.com/watch?v=fss6CrmQU2Y&t=2510s
#os.environ["OPENAI_API_KEY"] = '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'
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]="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"
os.environ["LANGCHAIN_ENDPOINT"]="https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"]="NL2SQL"

def ObtenerDB():
    username = "dev_jhurtado" 
    password = "Pka12msE1b2qO%401"# "Pka12msE1b2qO@1" 
    host = "192.168.193.5" 
    port = "5432"
    mydatabase = "dbcorp_desarrollo"
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
            host="192.168.193.5",
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

def devolver_Analisis(result,human_query):
    print(human_query)
    print(result)
    #*Do not mention the SQL query  in your response
    promptRespuestaFinal = f"""
    
You are an advanced data analyst and financial expert with deep knowledge of SQL. Your goal is to analyze the SQL query, understand the result it generates, and explain it clearly to the user.
    Given the following SQL result from PostgreSQL, analyze it as a Data Scientist and respond to the client's query.
    *Your response must be in Spanish.
    *If the SQL result includes the field 'ERI', provide the values from sal_acumulado_nac, which are the accumulated values. If the client explicitly requests monthly values, omit this condition.
    *The explanation should be clear and easy to understand so that a person with any level of knowledge can grasp it.
    *Continue the client's text smoothly, ensuring that your response feels like a natural extension of what the client has written.
    *Answer directly to the client's question, focusing on what is being asked without unnecessary details.
    *Respond directly to the user's question based on the SQL result Itemized if its nesesary and only use the provide data", ensuring that your answer is easy to understand. Your explanation should reflect both your financial expertise and the data retrieved, providing useful insights or conclusions.
    * Make sure your explanation is conversational ,easy to follow  And NEVER forgot to give the negative signs in the your response, even for someone who may not have a strong background in SQL or finance. Avoid using overly technical jargon.
    **Your response must NATURALLY CONTINUE the client's message, maintaining a smooth conversational flow.
    *Do not rephrase the client’s query; instead, continue the conversation as if you were writing the next sentence.
    *Directly address the client's question with relevant insights from the SQL result.
    *Format your response naturally and conversationally. For example, instead of returning raw data like 'saldo_acumulado_indian_motos':7109505.49, provide a complete sentence such as: El saldo acumulado de Indian Motos es de 7109505.49.
    *YOu MUST Return the answer as a JSON  using the key "query_response" as the following example:
    "query_response": " YOUR ANSWER."
    <humanquery>
    {human_query}
    </humanquery>
    <result of SQLQuery>
    {result}
    </result of SQLQuery>
    """
    prompt = f"""
    
You are an advanced data analyst and financial expert with deep knowledge of SQL. Your goal is to analyze the SQL query, understand the result it generates, and explain it clearly to the user.
    Given the following SQL result from PostgreSQL, analyze it as a Data Scientist and respond to the client's query.
    *Your response must be in Spanish.
    *If the SQL result includes the field 'ERI', provide the values from sal_acumulado_nac, which are the accumulated values. If the client explicitly requests monthly values, omit this condition.
    *The explanation should be clear and easy to understand so that a person with any level of knowledge can grasp it.
    *Continue the client's text smoothly, ensuring that your response feels like a natural extension of what the client has written.
    *Answer directly to the client's question, focusing on what is being asked without unnecessary details.
    *Respond directly to the user's question based on the SQL result Itemized if its nesesary and only use the provide data", ensuring that your answer is easy to understand. Your explanation should reflect both your financial expertise and the data retrieved, providing useful insights or conclusions.
    * Make sure your explanation is conversational ,easy to follow  And NEVER forgot to give the negative signs in the your response, even for someone who may not have a strong background in SQL or finance. Avoid using overly technical jargon.
    **Your response must NATURALLY CONTINUE the client's message, maintaining a smooth conversational flow.
    *Do not rephrase the client’s query; instead, continue the conversation as if you were writing the next sentence.
    *Directly address the client's question with relevant insights from the SQL result.
    *Format your response naturally and conversationally. For example, instead of returning raw data like 'saldo_acumulado_indian_motos':7109505.49, provide a complete sentence such as: El saldo acumulado de Indian Motos es de 7109505.49.
    *YOu MUST Return the answer as a JSON  using the key "query_response" as the following example:
    "query_response": " YOUR ANSWER."
    <query>
    {human_query}
    </query>
    <result of SQLQuery>
    """
    messages=[
                {"role": "system", "content": "Eres un experto en analitica de datos y ecomerces.Tu objetivo principal es tomar los datos obtenidos de una consulta de tu base de datos y analaizarlo para responder la consulta el cliente ."},
                {"role": "user", "content": promptRespuestaFinal}
            ]
    #messages=VariosMensajes(result,messages)
    try:
        client = OpenAI(
            # This is the default and can be omitted
            api_key='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'
            #api_key=os.environ.get("OPENAI_API_KEY"),
        )
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=3000,
            n=1,
            stop=None,
            temperature=0.0,
        )
        respuesta=chat_completion
        descripcion = respuesta.choices[0].message.content
        #print(descripcion)
        response_json = json.loads(descripcion)
        Queryresponse= response_json["query_response"]
        print(Queryresponse)
    except  BadRequestError as e:
        if "maximum context length" in str(e):
            Queryresponse="La información que desea consultar es muy extensa como para mostrártela por este medio. Por favor, delimite mejor su consulta."
        else:
            raise  # Puedes seguir manejando otros errores aquí si es necesario

    return Queryresponse
        
def NL2SQL(input):
    select_table=TablasDinamicas.GetTablasSellecionadas()
    db=ObtenerDB()#
    few_shot_prompt=DinamicEjemplosChroma.GetEjemploPrompt()
    #print(few_shot_prompt)
    promptGSQL = ChatPromptTemplate.from_messages(
        [
            #("system","You are a Posgres expert. Given an input question, create a syntactically correct Posgress query to run.you must first analyze the examples that will be provided in subsequent messages. Your responses should primarily be based on these examples. Identify the patterns, selected columns, and structures used in those examples and apply them to the new queries. Unless otherwise specificed.Write a SQL Postgres query that retrieves the requested information using **only** the provided column names. Do not add or assume any other conditions, column names, or values that are not explicitly mentioned by the user.\n\nYou **MUST include** sal_tipo=1 in ALL of your SQL Postgres queries. However, if the query explicitly mentions 'presupuesto', use the value 2 for sal_tipo.\n\nIf the query **explicitly mentions** 'ERI' or 'estado de resultados integrales', include the sal_tipo_estado column with the value 'ERI' in capital letters.\n\nIf the **query explicitly mentions** 'ESF', 'estado de situación financiera'  or 'balance general', include the sal_tipo_estado column with the value 'ESF' in capital letters.\n\nIf a company name is provided, perform a case-insensitive search using the ILIKE operator to match substrings. Ensure that **no additional filters** such as 'efectivo' or 'equivalente' are added unless explicitly requested by the user.\n\nAdditionally, if any words in the input question  contain diacritical marks (like accents), remove those marks.\n\nHere is the relevant table info: {table_info}\n\nGenerate an SQL query that selects only the relevant columns from the data, excluding those that should not be considered according to the following list: do not include (sal_codigo, saldo_nivel, sal_genero, sal_nombre_eeff, sal_negrita, sal_codigo_emp, sal_id, sal_indicador, sal_seg_codigo, sal_id_nivel1, sal_id_nivel2, sal_id_nivel3, sal_codigo_eeff, sal_calculo, sal_nombre_se, sal_codigo_cuenta, ref_fecha_actualizacion, sal_cen_id, sal_alm_id).\n\nBefore generating any SQL query, carefully analyze the provided examples and their corresponding SQL queries. **Your primary task is to replicate the patterns, column selections, and structures observed in these examples**. Only if the examples do not fully address the query, you may refer to the schema of the table to supplement the information, but **all selected columns must align with those used in the examples**. The schema should only be used to determine filters and additional conditions if necessary.\n\nRemember, the examples provided in other messages are your primary guide for constructing your responses.\n\n**Output the SQL query only** as plain text, without any additional characters, comments, or formatting. Do not use code blocks, backticks, or any other markup." ),
            ("system","Eres un experto en SQL Queries para bases de datos PostgreSQL. Tu objetivo es crear una consulta SQL que satisfaga la solicitud del usuario utilizando los ejemplos dados como referencia.\n\nSigue los siguientes pasos:\n\n1. **Analiza los ejemplos dados:** Compara la petición del usuario con los ejemplos proporcionados y busca similitudes en la estructura o los filtros aplicados.\n- Los ejemplos proporcionados son tu **guía principal** para construir la consulta.\n- Utiliza **exactamente las mismas columnas** y filtros de los ejemplos siempre que la solicitud del usuario sea similar.\n\n2. **Construcción de la consulta:**\n- Escribe una consulta SQL en PostgreSQL que recupere la información solicitada utilizando **solo** los nombres de columnas proporcionados en los ejemplos.\n- No añadas ni asumas ninguna condición, nombres de columnas o valores que no hayan sido mencionados explícitamente por el usuario.\n\n3. **Filtros y condiciones obligatorias:**\n- **Debes incluir siempre** `sal_tipo=1` en **todas** tus consultas SQL.\n- Si la consulta **menciona explícitamente** 'presupuesto', usa el valor `2` para `sal_tipo`.\n- Si la consulta **menciona explícitamente** 'ERI' o 'estado de resultados integrales', incluye la columna `sal_tipo_estado` con el valor `'ERI'` en mayúsculas.\n- Si la consulta **menciona explícitamente** 'ESF', 'estado de situación financiera' o 'balance general', incluye la columna `sal_tipo_estado` con el valor `'ESF'` en mayúsculas.\n\n4. **Búsqueda de nombres de empresas:**\n- Si se proporciona el nombre de una empresa, realiza una búsqueda insensible a mayúsculas/minúsculas utilizando el operador `ILIKE` para hacer coincidir subcadenas.\n- Asegúrate de que **no se añadan filtros adicionales**, como 'efectivo' o 'equivalente', a menos que el usuario los solicite explícitamente.\n\n5. **Tratamiento de marcas diacríticas (acentos):**\n- Si en la consulta del usuario hay palabras con marcas diacríticas (como acentos), elimina dichas marcas al procesar la solicitud.\n\n6. **Uso del esquema de la tabla:**\n- El esquema de la tabla solo debe usarse para determinar filtros y condiciones adicionales **si es necesario**, pero siempre se debe priorizar la estructura de los ejemplos proporcionados.\n\n7. **Salida de la consulta:**\n- La salida de la IA debe ser **solo el texto de la consulta SQL** sin ningún tipo de formato adicional, comentarios, bloques de código o caracteres especiales como backticks.\n\nEl resultado final debe ser una consulta SQL optimizada y lista para ejecutarse en PostgreSQL, respetando todas las reglas y condiciones mencionadas.\n\n Aquí está la información relevante de la tabla: {table_info}."),
            few_shot_prompt,
            ("human", "{input}"),
        ]
    )
    generate_query = create_sql_query_chain(llm, db,promptGSQL)
    
    chain = (
    RunnablePassthrough.assign(table_names_to_use=select_table) |
    RunnablePassthrough.assign(query=generate_query)
    )
    QuerySQL= chain.invoke({"question": input})
    QuerySQL=QuerySQL['query']
    #print(QuerySQL)
    resultado=ejecutar_consulta(QuerySQL)
    if (resultado==""):
        QueryResponse="Para poder darte una respuesta adecuada, por favor proporciona más detalles o verifica la información que estás consultando."
    else:
       QueryResponse= devolver_Analisis(resultado,input)
    return QueryResponse
def VariosMensajes(texto,messages):
    # Contar el número de palabras
    # Variables para acumular palabras y bloques de párrafos
    bloque_actual = []
    parrafos_divididos = []
    contador_palabras = 0

    # Recorrer cada elemento de la lista 'texto'
    for parrafo in texto:
        # Si el parrafo es una tupla, unimos todos sus elementos en un solo string
        if isinstance(parrafo, tuple):
               parrafo = '(' + ', '.join([str(p) for p in parrafo]) + ')'
        
        palabras = parrafo.split()
        palabras_en_parrafo = len(palabras)
        
        # Si añadir el nuevo párrafo supera las 750 palabras, guardar el bloque actual y comenzar uno nuevo
        if contador_palabras + palabras_en_parrafo > 750:
            parrafos_divididos.append(' '.join(bloque_actual))
            bloque_actual = []
            contador_palabras = 0

        # Agregar el párrafo actual al bloque
        bloque_actual.extend(palabras)
        contador_palabras += palabras_en_parrafo

    # Añadir el último bloque si hay palabras en él
    if bloque_actual:
        parrafos_divididos.append(' '.join(bloque_actual))
        
    # Añadir el mensaje al último párrafo
    if parrafos_divididos:
        parrafos_divididos[-1] += " </result of SQLQuery>"

    for parrafo in parrafos_divididos:
        messages.append({"role": "user", "content": parrafo})

    print(messages)
    return messages

#db=ObtenerDB()     
#print(connection)    
#execute_query = QuerySQLDataBaseTool(db=db)
#print(execute_query.invoke("SELECT COUNT(*) FROM eeff_saldos_v;"))
#input="Consultar las Devoluciones del año 2023 de la empresa indumot."
# Lista de consultas
# Aquí puedes modificar para ejecutar la consulta en tu base de datos en lugar de solo imprimirla.
