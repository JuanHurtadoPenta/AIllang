from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from IALang6 import NL2SQL
from IAFinancieroKPIS import NL2SQLKPI
from PosgressJega import get_user_id_by_channel

app = FastAPI()

# Definir el modelo de datos que esperamos en la solicitud
class QueryRequest(BaseModel):
    query: str
    canal: str
    user_id: str
    id_padre: int

@app.post("/nl2sql")
async def nl2sql_endpoint(request: QueryRequest):
    try:
        sql_query, id_pregunta = NL2SQL(request.query, int(request.user_id), int(request.canal), request.id_padre)
        print("Respondió: " + sql_query)
        return {"sql_query": sql_query, "id_pregunta": id_pregunta}
    except Exception as e:
        print("Error en nl2sql_endpoint: " + str(e))
        raise HTTPException(status_code=500, detail="Error al procesar la consulta: " + str(e))

@app.post("/nl2sqlKPI")
async def nl2sqlKPI_endpoint(request: QueryRequest):
    try:
        sql_query, id_pregunta = NL2SQLKPI(request.query, int(request.user_id), int(request.canal), request.id_padre)
        print("Respondió: " + sql_query)
        return {"sql_query": sql_query, "id_pregunta": id_pregunta}
    except Exception as e:
        print("Error en nl2sqlKPI_endpoint: " + str(e))
        raise HTTPException(status_code=500, detail="Error al procesar la consulta KPI: " + str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8383)