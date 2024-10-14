from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from IALang4 import NL2SQL
from PosgressJega import get_user_id_by_channel

app = FastAPI()

# Definir el modelo de datos que esperamos en la solicitud
class QueryRequest(BaseModel):
    query: str
    canal: str
    value:str

@app.post("/nl2sql")
async def nl2sql_endpoint(request: QueryRequest):
    natural_language_query = request.query
    canal=int(request.canal)
    value=request.value
    try:
        user_id = get_user_id_by_channel(canal, value)  # Llamar a la función para obtener el ID del usuario
        if user_id is not None:
            # Llamar a la función NL2SQL desde el archivo lang3.py
            sql_query = NL2SQL(natural_language_query,user_id,canal)
            return {"sql_query": sql_query}
        else: 
            return {"sql_query": "Usuario no registrado o  no tiene acesso a jega."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)