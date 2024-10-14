from operator import itemgetter
from langchain.chains.openai_tools import create_extraction_chain_pydantic
from pydantic import BaseModel,Field
from typing import List
import pandas as pd
from langchain_openai import ChatOpenAI
import os
#os.environ["OPENAI_API_KEY"] = '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'
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
ruta=r"/app/DocumentosRequeridos/database_table_descriptions.csv"
#ruta=r"DocumentosRequeridos/database_table_descriptions.csv"
def get_table_details():
    # Read the CSV file into a DataFrame
    table_description = pd.read_csv(ruta, sep=';')#"/app/DocumentosRequeridos/database_table_descriptions.csv", sep=';')
    
    print("leyo el archivo de tablas")
    #print(table_description)
    # Iterate over the DataFrame rows to create Document objects
    table_details = ""
    for index, row in table_description.iterrows():
        table_details = table_details + "Table Name:" + str(row['Table']) + "\n" + "Table Description:" +  str(row['Description']) + "\n\n"

    return table_details


class Table(BaseModel):
    """Table in SQL database."""

    name: str = Field(description="Name of table in SQL database.")

def get_tables(tables: List[Table]) -> List[str]:
    tables  = [table.name for table in tables]
    return tables
# table_names = "\n".join(db.get_usable_table_names())
def GetTablasSellecionadas():
    table_details = get_table_details()

    table_details_prompt = f"""Return the names of ALL the SQL tables that MIGHT be relevant to the user question. \
    The tables are:

    {table_details}

    Remember to include ALL POTENTIALLY RELEVANT tables, even if you're not sure that they're needed."""

    select_table = {"input": itemgetter("question")} | create_extraction_chain_pydantic(Table, llm, system_message=table_details_prompt) | get_tables
    #select_table.invoke({"question": "give me details of customer and their order count"})
    return select_table