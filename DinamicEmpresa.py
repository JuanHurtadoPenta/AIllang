from langchain_openai import OpenAIEmbeddings
import json
from langchain_chroma import Chroma
#https://www.studywithgpt.com/es/tutorial/anbbtw
# Inicializa las embeddings
embeddings = OpenAIEmbeddings()
dir ="/app/VectorStore/Empresas"
#dir ="VectorStore/Empresas"
ruta_archivo = r"/app/DocumentosRequeridos/empresas.txt"#/app/DocumentosRequeridos/empresas.txt"  # Asegúrate de que el archivo esté en formato JSON
#ruta_archivo = r"DocumentosRequeridos/empresas.txt"
# Función para leer empresas desde un archivo JSON
def leerEmpresas():
    with open(ruta_archivo, 'r', encoding='utf-8') as file:
        examples = json.load(file)  # Carga el JSON correctamente
    return examples

def CargarInfoVS():
    text = leerEmpresas()
    # Inicializa la colección Chroma
    vectorstore = Chroma(
        collection_name="Empresas",
        embedding_function=embeddings,
        persist_directory=dir,
    )
    
    # Asegúrate de que cada elemento en text sea un dict con "nombre_completo" y "nombre_comercial"
    texts = [item["nombre_comercial"] for item in text]  # Extrae solo los nombres completos
    metadata = [{"id": item["nombre_completo"]} for item in text]  # Extrae la metadata

    # Agrega textos a la colección
    vectorstore.add_texts(texts=texts, metadatas=metadata)
    
    return vectorstore

def vectorestore():
    vector_store = Chroma(
        collection_name="Empresas",
        embedding_function=embeddings,
        persist_directory=dir,  # Donde guardar los datos localmente, elimínalo si no es necesario
    )
    return vector_store
def ObtenerEmpresa(query):
    # Carga la información en el vector store
    #vector_store = CargarInfoVS()
    vector_store=vectorestore()
    # Realiza una búsqueda de similitu
    #print(query)
    results = vector_store.similarity_search(query, k=3)  # Cambia 'k' según el número de resultados que quieras obtener
    # Inicializa una variable para almacenar todos los resultados concatenados
    resultados = []
    # Itera a través de todos los resultados y agrega cada uno a la lista
    for res in results:
        resultado = f"* Nombre comercial: {res.page_content}, Nombre Completo: {res.metadata['id']}"
        resultados.append(resultado)
    
    # Une todos los resultados en una sola cadena con salto de línea
    resultado_final = "\n".join(resultados)
    #print(resultado_final)
    return resultado_final
#######################33
#para volver a cargar la base se debe borrar la carpeta empresa y ejecutar
 #vector_store = CargarInfoVS()
#print(ObtenerEmpresa("Cual es el ERI de  royal motors para marzo 2024"))