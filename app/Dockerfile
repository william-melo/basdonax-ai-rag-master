# Usa una imagen base de Python
FROM python:3.11

# Establecer el directorio de trabajo
WORKDIR /app

# Copia todo el contenido del directorio actual al directorio de trabajo
COPY . .

# Actualiza pip e instala las dependencias
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Instalar nltk y descargar los recursos necesarios
RUN python -m nltk.downloader punkt

# Exponer los puertos para Streamlit y FastAPI
EXPOSE 8080
EXPOSE 8000

# Comando para ejecutar tanto Streamlit como FastAPI
CMD ["sh", "-c", "uvicorn Inicio:app --host 0.0.0.0 --port 5100 & streamlit run Inicio.py --server.port 8080"]