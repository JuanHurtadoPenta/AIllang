from langchain_openai import OpenAIEmbeddings

#Libreria para usar los ejemplos dinamicos con CHROMA
#https://python.langchain.com/docs/integrations/vectorstores/chroma/

#pip install -qU "langchain-chroma>=0.1.2"
###########################################################################################
#     ESTE DESARROLLO TIENE A  CHROMA COMO VECTORE STORE, PERO CREA LOS EMBENDIGS CADA QUE SE EJECUTA
#     pero con otro metodo directo de similarity
##########################################################################################

embeddings = OpenAIEmbeddings()
dir="/app/VectorStore/Ejemplos"
#dir="VectorStore/Ejemplos"
ruta_ejemplos=r"/app/DocumentosRequeridos/Examples.txt"
#ruta_ejemplos=r"DocumentosRequeridos/Examples.txt"
def leerAEjemplos(ruta_archivo,Value=1):
    import json
    textos=[]
    if Value==1:
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            examples = json.load(file)
        for item in examples:
            a=f""" "input":"{item['input']}"
                "query": "{item['query']}"
                """
            textos.append(a)
        return textos
    else:
        with open(ruta_archivo, 'r', encoding='utf-8') as file:
            examples = json.load(file)
        return examples


def EjemplosDinamicos(query):
    from langchain_core.example_selectors import SemanticSimilarityExampleSelector
    from langchain_openai import OpenAIEmbeddings
    from langchain_core.prompts import ChatPromptTemplate,FewShotChatMessagePromptTemplate
    from langchain_chroma import Chroma
    import shutil # Importing shutil module for high-level file operations
    import os


    #vectorstore = Chroma()
    #vectorstore.delete_collection()
    #print("borro coleciones")
    # Clear out the existing database directory if it exists
    #if os.path.exists("VectorStore\Ejemplos"):
       # shutil.rmtree("VectorStore\Ejemplos")
    
    #vectorstore =Chroma()# Chroma(collection_name="SQLFinanciero",embedding_function= embeddings,persist_directory="VectorStore\Ejemplos")
    #vectorstore = Chroma(collection_name="SQLFinanciero",embedding_function= embeddings,persist_directory="VectorStore\Ejemplos")
    #vectorstore.reset_collection()
    if  os.path.exists(dir):
        #print("entro a la  carpeta de ejemplos")
        vector_store = Chroma(
        collection_name="SQLFinanciero",
        embedding_function=embeddings,
        persist_directory=dir,  # Donde guardar los datos localmente, elimínalo si no es necesario
        )
        results = vector_store.similarity_search(query, k=6)  # Cambia 'k' según el número de resultados que quieras obtener
        # Inicializa una variable para almacenar todos los resultados concatenados
        resultados = []
        # Itera a través de todos los resultados y agrega cada uno a la lista
        for res in results:
            resultado= f"""("system","{res.metadata['input']}\nSQLQuery:\n {res.metadata['query']}\n")"""
            resultados.append(resultado)
        #print(resultados)
        #print("los ejemplos son"+str(resultados))
        example_prompt1=ChatPromptTemplate.from_messages(resultados)
        return  example_prompt1
    else:
        # Chroma(collection_name="SQLFinanciero",embedding_function= embeddings,persist_directory="VectorStore\Ejemplos")
    #vectorstore.delete_collection()
        print("no existe")
        Examples=leerAEjemplos(ruta_ejemplos,2)#/app/DocumentosRequeridos/Examples.txt",2)
        vectorstore =Chroma()#
        example_selector = SemanticSimilarityExampleSelector.from_examples(
            Examples,
            OpenAIEmbeddings(),
            vectorstore,
            k=6,
            input_keys=["input"],
            collection_name="SQLFinanciero",
            persist_directory=dir
            )
        #vectorstore.persist()

        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}\nSQLQuery:"),
                ("ai", "{query}"),
            ]
        
        )

        example_prompt1 = ChatPromptTemplate.from_messages(
            [
                ("system","{input} \nSQLQuery:\n{query}\n"),
            ]
        
        )
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt1,
            example_selector=example_selector,
            input_variables=["input","top_k"],
        )
        #print("va a rretornar")
        #print(few_shot_prompt)
        return few_shot_prompt

def GetEjemploPrompt(query):
    return EjemplosDinamicos(query)

##########################
# para crear una nueva base de ejmplos, borra la carpeta ejemplos y ejecuta los siguitnetes comandos
#human_query="dame el   valor de activo de mayo 2024 de la empresa KTM"
#Empresas=GetEjemploPrompt(human_query)