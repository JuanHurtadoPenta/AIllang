from openai import OpenAI
import os,json
from openai import  BadRequestError
from openai import OpenAI
import psycopg2
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import create_sql_query_chain
from operator import itemgetter
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
def  ExtaerNombreKPI(human_query):
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
            nombre="No se pudo obtener nombre empresa"

    return nombre
human_query="valor de gastos de logistica de la empresa almacenes juan eljuri para mayo 2024",
print(ExtaerNombreKPI(human_query))

