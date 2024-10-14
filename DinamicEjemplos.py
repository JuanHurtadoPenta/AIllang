from langchain_openai import OpenAIEmbeddings
from weaviate.exceptions import WeaviateGRPCUnavailableError
import os

#Libreria para usar los ejemplos dinamicos con Weviavite

#os.environ["OPENAI_API_KEY"] = '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'
#pip install -Uqq langchain-weaviate
cluster_url = "https://1nvc7iupslqjt4i6rmuvoa.c0.us-west3.gcp.weaviate.cloud"#"https://grpc-1nvc7iupslqjt4i6rmuvoa.c0.us-west3.gcp.weaviate.cloud"
api_key = "69KnsVEvfx5Ni5mnjblGKForfcTLigbV5yg2"
# Establece las variables de entorno dentro del script
os.environ["WEAVIATE_URL"] = cluster_url
os.environ["WEAVIATE_API_KEY"] = api_key 
embeddings = OpenAIEmbeddings()

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


def EjemplosDinamicos(Examples):
    from langchain_core.example_selectors import SemanticSimilarityExampleSelector
    from langchain_openai import OpenAIEmbeddings
    from langchain_core.prompts import ChatPromptTemplate,FewShotChatMessagePromptTemplate
    from langchain_community.vectorstores import Weaviate
    import weaviate
    from weaviate.auth import AuthApiKey
    from langchain_community.vectorstores import Weaviate
    # Crear el cliente de Weaviate utilizando la versión 4
    try:
        auth = AuthApiKey(api_key)
        client = weaviate.connect_to_weaviate_cloud(
        cluster_url=cluster_url,  # Replace with your Weaviate Cloud URL
        auth_credentials=auth  # Replace with your Weaviate Cloud key
        )
        #borra una coleccion con el nombre existente 
        client.collections.delete("SQL1") 
        client.close()
    except WeaviateGRPCUnavailableError as e:
        print("No se pudo borrar la coleccion existente")
    #este metodo crea siempre una coleccion
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        Examples,
        OpenAIEmbeddings(),
        Weaviate,
        k=6,
        input_keys=["input"],
        index_name="SQL1"
        )

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
    return few_shot_prompt

def GetEjemploPrompt():
    Examples=leerAEjemplos(r"/DocumentosRequeridos\Examples.txt",2)
    return EjemplosDinamicos(Examples)