from pprint import pprint

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import streamlit as st

load_dotenv('../.env')

llm = ChatOllama(
   base_url="http://localhost:11434",
   model="qwen2.5:latest",
   temperature=0.5,
   max_tokens=250
)

st.title("How can I help you today?")
st.write("Enter your query below")


def get_session_history(session_id) -> SQLChatMessageHistory:
    return SQLChatMessageHistory(
        session_id=session_id, connection_string="sqlite:///chat_history.db"
    )


template = ChatPromptTemplate.from_messages(
    [
        ("human", "{prompt}"),
        ("placeholder", "{history}"),
    ]
)
chain = template | llm | StrOutputParser()

store = {}

history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="prompt",
    history_messages_key="history",
)

session_id = "Karthik"
get_session_history(session_id).clear()

prompt = st.chat_input("Enter your query")
