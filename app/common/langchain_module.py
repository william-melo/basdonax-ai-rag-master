from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from common.chroma_db_settings import Chroma
from common.assistant_prompt import assistant_prompt
import os
import argparse

model = os.environ.get("MODEL")
# For embeddings model, the example uses a sentence-transformers model
# https://www.sbert.net/docs/pretrained_models.html 
# "The all-mpnet-base-v2 model provides the best quality, while all-MiniLM-L6-v2 is 5 times faster and still offers good quality."
embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME", "all-MiniLM-L6-v2")
target_source_chunks = int(os.environ.get('TARGET_SOURCE_CHUNKS',5))

from common.constants import CHROMA_SETTINGS



def response(query: str) -> str:
    # No se usa `argparse`, configura directamente los valores necesarios
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

    db = Chroma(client=CHROMA_SETTINGS, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": target_source_chunks})

    # Usa directamente los valores necesarios en lugar de argumentos de línea de comandos
    callbacks = [StreamingStdOutCallbackHandler()]  # Siempre activa el callback

    llm = Ollama(model=model, callbacks=callbacks, temperature=0, base_url='http://ollama:11434')
    prompt = assistant_prompt()

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain.invoke(query)
