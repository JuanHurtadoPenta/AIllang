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

    name: str = Field(description="Give the name of the unique releevant table in SQL database.that could aswer the client query")

def get_tables(tables: List[Table]) -> List[str]:
    tables  = [table.name for table in tables]
    return tables
# table_names = "\n".join(db.get_usable_table_names())
def GetTablasSellecionadas():
    table_details = get_table_details()

    table_details_prompt = f"""
    Return only one table name that is most relevant to the user's query based on the descriptions of the tables provided. If the query is not relevant to financial data or indicators, do not return any table.
    {table_details}
   Instructions:
   **Return only one name of the table tan could be the more relevan to responde the human query**"""

    select_table = {"input": itemgetter("question")} | create_extraction_chain_pydantic(Table, llm, system_message=table_details_prompt) | get_tables
    #select_table.invoke({"question": "give me details of customer and their order count"})
    return select_table
def GetTablasSellecionadasKPIS():
    table_details = """Table Name:eeff_valor_indicador_v
Table Description: almacena los valores de diversos indicadores financieros utilizados para evaluar el desempeño económico y operativo de la empresa, tales como Ciclo de Efectivo ($/día), Apalancamiento Patrimonio, Capital Neto de Trabajo, % Utilidad Operacional, Rotación de Inventarios, % Gastos de Logística, Liquidez Corriente, % Utilidad Neta, Rotación Cuentas por Pagar, % Gastos Administrativos, Prueba Ácida, % Costo de Venta, % Margen Bruto, % Gastos de Ventas, ROA (Return on Assets), Periodo Medio de Cobro (días), ROE (Return on Equity - DuPont), % Gastos No Operacionales, % EBITDA, % Gastos de Publicidad, Días de Inventario (días), Capital Invertido, % Gastos Operacionales, Deuda/EBITDA, Razón de Endeudamiento, Cobertura de Intereses, Período Medio de Pago (días) y % Venta Neta, proporcionando datos clave para el análisis financiero y la toma de decisiones estratégicas."""

    table_details_prompt = f"""
    Return only one table name that is most relevant to the user's query based on the descriptions of the tables provided. If the query is not relevant to financial data or indicators, do not return any table.
    {table_details}
   Instructions:
   **Return only one name of the table tan could be the more relevan to responde the human query**"""

    select_table = {"input": itemgetter("question")} | create_extraction_chain_pydantic(Table, llm, system_message=table_details_prompt) | get_tables
    #select_table.invoke({"question": "give me details of customer and their order count"})
    return select_table
