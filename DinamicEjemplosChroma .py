from langchain_openai import OpenAIEmbeddings

#Libreria para usar los ejemplos dinamicos con CHROMA
#https://python.langchain.com/docs/integrations/vectorstores/chroma/

#pip install -qU "langchain-chroma>=0.1.2"
###########################################################################################
#     ESTE DESARROLLO TIENE A  CHROMA COMO VECTORE STORE, PERO CREA LOS EMBENDIGS CADA QUE SE EJECUTA
#     BORRANOD EL ANTERIOR DB. 
##########################################################################################

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
    vectorstore =Chroma()# Chroma(collection_name="SQLFinanciero",embedding_function= embeddings,persist_directory="VectorStore\Ejemplos")
    #vectorstore.delete_collection()
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        Examples,
        OpenAIEmbeddings(),
        vectorstore,
        k=6,
        input_keys=["input"],
        collection_name="SQLFinanciero",
        persist_directory="VectorStore\Ejemplos"
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
    return few_shot_prompt

def GetEjemploPrompt():
    Examples=leerAEjemplos(r"/app/DocumentosRequeridos/Examples.txt",2)#/app/DocumentosRequeridos/Examples.txt",2)
    return EjemplosDinamicos(Examples)