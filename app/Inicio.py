import streamlit as st
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from threading import Thread

st.set_page_config(layout='wide', page_title='Inicio - Basdonax AI RAG', page_icon='⌨️')

from common.langchain_module import response as langchain_response
from common.streamlit_style import hide_streamlit_style

hide_streamlit_style()

# FastAPI setup
app = FastAPI()

class RequestBody(BaseModel):
    query: str

@app.post("/query")
async def query_langchain(request_body: RequestBody):
    query = request_body.query
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        response = langchain_response(query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Streamlit app code
def run_streamlit():
    st.title("Basdonax AI RAG")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if user_input := st.chat_input("Escribí tu mensaje 😎"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(user_input)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Process user input and generate response
        if st.session_state.messages and user_input.strip() != "":
            response = langchain_response(user_input)
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

# Run Streamlit in a separate thread
def start_streamlit():
    run_streamlit()

if __name__ == "__main__":
    # Start Streamlit in a new thread
    streamlit_thread = Thread(target=start_streamlit)
    streamlit_thread.start()

    # Run FastAPI
    uvicorn.run(app, host="0.0.0.0", port=8000)
