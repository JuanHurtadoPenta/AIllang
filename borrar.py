from openai import OpenAI
import os,json
from openai import  BadRequestError
from openai import OpenAI
import psycopg2
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import create_sql_query_chain
from operator import itemgetter
from DinamicEmpresa import ObtenerEmpresa,vectorestore#no mover el orden de la importacion
from TablasDinamicas import GetTablasSellecionadas
from DinamicEjemplosChroma1 import GetEjemploPrompt
from langchain_openai import ChatOpenAI
import re
from PosgressJega import add_question,add_response,add_sql_query,add_response_id
os.environ["OPENAI_API_KEY"] = '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'

from dotenv import load_dotenv
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

def ExtaerNombre(human_query):
    human_query=human_query.lower()
    nombre_empresas_ai=ExtraerNombreIA(human_query)
    nombre_empresas=ObtenerEmpresa1(nombre_empresas_ai)
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
def borrar():
    consultas = [
          " dame el   valor de activo de mayo 2024 de  bajaj",
    " quiero el consolidado de ventas brutas de la empresa indumot para febrero 2023",
    "Cual es el ERI de  royal motors para marzo 2024",
    "Quiero el valor EBITDA de  toscana para enero 2024 ",
    "Cual es el valor de Activo Corriente  de Aje Licores en el mes de febrero 2024",
    "Dame el valor de ventas brutas para   KTM de junio 2024",
    "Cual es  balance general de  inmot para febrero 2023.",
    "dame la diferencia de ventas netas del mes de enero de los años 2023 y 2024 de innmot",
    "dame la diferencia de ventas netas del mes de enero de los años 2023 y 2024 de kawasaki",
    "dame la diferencia de ventas netas del mes de enero de los años 2023 y 2024 de  la taberna"
    ]

    # Ejecutar la función para cada consulta
    for consulta in consultas:
        print(ExtaerNombre(consulta))
        #Empresas=ObtenerEmpresa(consulta)
        #print ("lista de empresas:"+Empresas)
        #print(ExtaerNombre(consulta,Empresas))
        print("--------------------------------------------")  # Aquí puedes modificar para ejecutar la consulta en tu base de datos en lugar de solo imprimirla.
def ObtenerEmpresa1(query):
    # Carga la información en el vector store
    #vector_store = CargarInfoVS()
    vector_store=vectorestore()
    # Realiza una búsqueda de similitu
    #print(query)
    results = vector_store.similarity_search_with_score(query, k=1)  # Cambia 'k' según el número de resultados que quieras obtener
    
    #print(results)# Inicializa una variable para almacenar todos los resultados concatenados
    resultados = []
    total=[]
    # Itera a través de todos los resultados y agrega cada uno a la lista
    for documento in results:
        res,b=documento
        resultado = f"* Nombre comercial: {res.page_content}, Nombre Completo: {res.metadata['id']}"
        resultados.append(resultado)
        total.append(b)
    print(total)
    #print(resultados)
    coind=False
    for a in total:
        #print(a)
        if float(a)<=0.25:
            coind=True
    
    if coind==True:
    # Une todos los resultados en una sola cadena con salto de línea
        resultado_final = "\n".join(resultados)
        #print(resultado_final)
        return resultado_final
    else: return None


borrar()

