import os
import sys
from pathlib import Path

import streamlit as st
from langchain.agents import AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from tools.base import ToolResult
from tools.loop import (
    PROVIDER_TO_DEFAULT_MODEL_NAME,
    APIProvider,
    sampling_loop,
)

# Set the page configuration
st.set_page_config(
    page_title="AI Assistant",
    page_icon=":robot:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Set the title and description
st.title("AI Assistant")
st.write(
    "This is an AI assistant that can help you with a variety of tasks. "
    "Simply type your request in the input box below and the assistant will respond."
)

# Create the chat input
chat_input = st.text_area("Your message", height=200)

# Create the chat button
if st.button("Send"):
    # Create the chat model and memory
    chat_model = ChatOpenAI(temperature=0.7)
    memory = ConversationBufferMemory(return_messages=True)

    # Create the agent
    agent = AgentExecutor.from_agent_and_tools(
        agent=sampling_loop(
            APIProvider.OPENAI,
            PROVIDER_TO_DEFAULT_MODEL_NAME[APIProvider.OPENAI],
            chat_input,
            memory,
        ),
        tools=[],
        verbose=True,
        memory=memory,
    )

    # Run the agent and get the result
    result = agent.run(chat_input)

    # Display the result
    st.write(result)
