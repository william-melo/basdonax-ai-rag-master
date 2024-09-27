import streamlit as st

st.set_page_config(layout='wide', page_title='Archivos - Basdonax AI RAG', page_icon='📁')

import chromadb, os
from langchain_community.embeddings import HuggingFaceEmbeddings
from chromadb.config import Settings
from common.chroma_db_settings import get_unique_sources_df
from common.ingest_file import ingest_file, delete_file_from_vectordb, ingest_files, delete_files_from_vectordb
from common.streamlit_style import hide_streamlit_style

hide_streamlit_style()

# Define the Chroma settings
CHROMA_SETTINGS = chromadb.HttpClient(host="host.docker.internal", port = 8000, settings=Settings(allow_reset=True, anonymized_telemetry=False))
collection = CHROMA_SETTINGS.get_or_create_collection(name='vectordb')
embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

st.title('Archivos')

# Carpeta donde se guardarán los archivos en el contenedor del ingestor
container_source_directory = 'documents'

# Función para guardar el archivo cargado en la carpeta
def save_uploaded_file(uploaded_file):
    # Verificar si la carpeta existe en el contenedor, si no, crearla
    if not os.path.exists(container_source_directory):
        os.makedirs(container_source_directory)

    with open(os.path.join(container_source_directory, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return os.path.join(container_source_directory, uploaded_file.name)

# Widget para cargar archivos
uploaded_files = st.file_uploader("Cargar archivo", type=['csv', 'doc', 'docx', 'enex', 'eml', 'epub', 'html', 'md', 'odt', 'pdf', 'ppt', 'pptx', 'txt'], accept_multiple_files=True)

# Botón para ejecutar el script de ingestión
if st.button("Agregar archivos a la base de conocimiento") and uploaded_files:
    progress_bar = st.progress(0)
    for i, uploaded_file in enumerate(uploaded_files):
        file_name = uploaded_file.name
        ingest_files(uploaded_files)
        progress_bar.progress((i + 1) / len(uploaded_files))
    st.success(f"Se agregaron {len(uploaded_files)} archivos a la base de conocimiento.")
elif not uploaded_files:
    st.write("Por favor carga al menos un archivo antes de agregar a la base de conocimiento.")

st.subheader('Archivos en la base de conocimiento:')

files = get_unique_sources_df(CHROMA_SETTINGS)
files['Eliminar'] = False
files_df = st.data_editor(files, use_container_width=True)

selected_files = files_df.loc[files_df['Eliminar'] == True]
num_selected = len(selected_files)

if num_selected > 0:
    st.divider()
    st.subheader('Eliminar archivos')
    
    if num_selected == 1:
        st.write(f"Archivo seleccionado para eliminar:")
    else:
        st.write(f"Archivos seleccionados para eliminar: {num_selected}")
    
    st.dataframe(selected_files, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
                
    with col2:
        button_text = 'Eliminar archivo' if num_selected == 1 else 'Eliminar archivos seleccionados'
        if st.button(button_text):
            try:
                delete_files_from_vectordb(selected_files['Archivo'].tolist())
                success_message = 'Archivo eliminado con éxito' if num_selected == 1 else f'{num_selected} archivos eliminados con éxito'
                st.success(success_message)
                st.rerun()
            except Exception as e:
                error_message = 'Ocurrió un error al eliminar el archivo' if num_selected == 1 else 'Ocurrió un error al eliminar los archivos'
                st.error(f'{error_message}: {e}')
else:
    st.info('Selecciona los archivos que deseas eliminar marcando la casilla en la columna "Eliminar".')
                


