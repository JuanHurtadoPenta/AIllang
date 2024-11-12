# Usa una imagen base de Python
FROM python:3.11


# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de tu aplicación al contenedor
COPY . /app

COPY ./VectorStore/Ejemplos/.  /app/VectorStore/Ejemplos/
COPY ./VectorStore/Empresas/. /app/VectorStore/Empresas/

# Instalar las dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Exponer el puerto que usará la aplicación (8000 por defecto en FastAPI)
EXPOSE 8383

# Comando para ejecutar la aplicación usando Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8383"]