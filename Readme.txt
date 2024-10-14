Este es un desarrollo usando Open IA an Langchain para hacer un modelo nl2sql Avanzado donde , se puede utilizar una base de ejemplos dinamica mediante 
el uso de vectore store ,guardando enbendings. Asi como la seleccion dinamica de tablas y squemas.
 toda la inofmracion pertinenete se encunetra en :https://blog.futuresmart.ai/mastering-natural-language-to-sql-with-langchain-nl2sql#heading-implementing-rephrasing-with-langchain y https://www.youtube.com/watch?v=fss6CrmQU2Y



 weaviate-client>=3.26.7;<4.0.0


 v2:dividir el sql en fracciones de parrafo par amandar como mensajes diferente para eso :
 1)use prompt en vez de prompt1
 2)descomenta la linea #messages=VariosMensajes(result,messages)
