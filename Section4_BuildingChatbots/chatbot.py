from pprint import pprint

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import streamlit as st

load_dotenv("../.env")

llm = ChatOllama(
    base_url="http://localhost:11434",
    model="qwen2.5:latest",
    temperature=0.5,
    max_tokens=250,
)


def get_session_history(session_id) -> SQLChatMessageHistory:
    return SQLChatMessageHistory(
        session_id=session_id, connection_string="sqlite:///chat_history.db"
    )


session_id = "Karthik"
st.title("How can I help you today?")
st.write("Enter your query below")
session_id = st.text_input("Enter you name", session_id)

if st.button("New Chat"):
    st.session_state.chat_history = []
    get_session_history(session_id).clear()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


template = ChatPromptTemplate.from_messages(
    [
        ("human", "{prompt}"),
        ("placeholder", "{history}"),
    ]
)
chain = template | llm | StrOutputParser()


def invoke_history(chain, session_id, prompt):
    history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="prompt",
        history_messages_key="history",
    )
    for response in history.stream(
        {"prompt": prompt}, 
        config={"configurable": {"session_id": session_id}}):
        
        yield response


prompt = st.chat_input("Enter your query")
if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message('assistant'):
        response = st.write_stream(invoke_history(chain, session_id, prompt))
    st.session_state.chat_history.append({"role": "assistant", "content": response})
