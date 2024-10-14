import os
import psycopg2
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import create_sql_query_chain
from operator import itemgetter
import TablasDinamicas,DinamicEjemplos
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

os.environ["OPENAI_API_KEY"] = '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'
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]="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"
##########################################################################################################################################################
#
# este desarrollo esta enfocado al uso exclusivo de tablas, actualmente no puede usar en una misma cadena el ejecutar sql query en vistas
#
#########################################################################################################################################################
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
    print(db)
    return db
def EjecutarSQL(db):
    from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
    execute_query = QuerySQLDataBaseTool(db=db)
    return execute_query
def NL2SQL(input):
    select_table=TablasDinamicas.GetTablasSellecionadas()
    db=ObtenerDB()
    few_shot_prompt=DinamicEjemplos.GetEjemploPrompt()
    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a Posgres expert. Given an input question, create a syntactically correct Posgress query to run. Unless otherwise specificed.Write a SQL Postgres query that retrieves the requested information using **only** the provided column names. Do not add or assume any other conditions, column names, or values that are not explicitly mentioned by the user.\n\n You **MUST include** `sal_tipo=1` in ALL of your SQL Postgres queries. However, if the query explicitly mentions 'presupuesto', use the value `2` for `sal_tipo`.\n\n If the query **explicitly mentions** 'ERI' or 'estado de resultados integrales', include the `sal_tipo_estado` column with the value 'ERI' in capital letters.\n\n If the **query explicitly mentions** 'ESF', 'estado de situación financiera'  or 'balance general', include the `sal_tipo_estado` column with the value 'ESF' in capital letters.\n\n If a company name is provided, perform a case-insensitive search using the `ILIKE` operator to match substrings. Ensure that **no additional filters** such as 'efectivo' or 'equivalente' are added unless explicitly requested by the user.\n\nHere is the relevant table info: {table_info}\n\nBelow are a number of examples of questions and their corresponding SQL queries."),
            few_shot_prompt,
            ("human", "{input}"),
        ]
    )
    generate_query = create_sql_query_chain(llm, db,final_prompt)
    answer_prompt = PromptTemplate.from_template(
     """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
    )
    rephrase_answer = answer_prompt | llm | StrOutputParser()

    execute_query = QuerySQLDataBaseTool(db=db)

    chain = (
    RunnablePassthrough.assign(table_names_to_use=select_table) |
    RunnablePassthrough.assign(query=generate_query).assign(
        result=itemgetter("query") | execute_query
    )
    | rephrase_answer
    )
    return chain.invoke({"question": input})



#print(NL2SQL("cual es el valor del Eri de la empresa inmot de enero 2024"))
db=ObtenerDB()     
#print(connection)    
execute_query = QuerySQLDataBaseTool(db=db)
print(execute_query.invoke("SELECT COUNT(*) FROM eeff_saldos_v;"))

