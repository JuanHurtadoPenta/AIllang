from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from IALang6 import NL2SQL
from PosgressJega import get_user_id_by_channel

app = FastAPI()

# Definir el modelo de datos que esperamos en la solicitud
class QueryRequest(BaseModel):
    query: str
    canal: str
    user_id:str
    id_padre:int

@app.post("/nl2sql")
async def nl2sql_endpoint(request: QueryRequest):
    natural_language_query = request.query
    canal=int(request.canal)
    user_id=int(request.user_id)
    id_padre=int(request.id_padre)
    print(user_id)
    try:
            sql_query,id_pregunta = NL2SQL(natural_language_query,user_id,canal,id_padre)
            print("respondio :"+sql_query)
            return {"sql_query": sql_query,"id_pregunta":id_pregunta}
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8383)