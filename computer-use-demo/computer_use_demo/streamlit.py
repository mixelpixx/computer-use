import os
import sys
import time
import openai
import streamlit as st
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from streamlit.delta_generator import DeltaGenerator

from computer_use_demo.loop import (
    PROVIDER_TO_DEFAULT_MODEL_NAME,
    APIProvider,
    sampling_loop,
    get_provider_and_model,
)
from computer_use_demo.utils import (
    get_image_from_url,
    get_image_from_file,
    get_image_from_base64,
    get_image_from_pil,
    get_image_from_numpy,
    get_image_from_tensor,
    get_image_from_bytes,
    get_image_from_url_or_file,
)

@dataclass
class ChatMessage:
    role: str
    content: str
    error: Optional[str] = None

@st.cache_resource
def get_api_provider() -> APIProvider:
    return APIProvider()

@st.cache_data
def get_model_name(provider: APIProvider) -> str:
    return PROVIDER_TO_DEFAULT_MODEL_NAME[provider]

def display_chat_message(
    message: ChatMessage,
    is_tool_result: bool = False,
    delta_generator: Optional[DeltaGenerator] = None,
) -> None:
    if delta_generator is None:
        delta_generator = st

    if message.role == "assistant":
        delta_generator.markdown(f"**Assistant:** {message.content}")
    elif message.role == "user":
        delta_generator.markdown(f"**You:** {message.content}")
    elif message.role == "system":
        delta_generator.markdown(f"**System:** {message.content}")

    if is_tool_result and hasattr(message, "error") and message.error:
        delta_generator.error(message.error)

def display_image(
    image: Optional[bytes],
    is_tool_result: bool = False,
    delta_generator: Optional[DeltaGenerator] = None,
) -> None:
    if delta_generator is None:
        delta_generator = st

    if image is not None:
        delta_generator.image(image)
    elif is_tool_result:
        delta_generator.error("Failed to display image.")

def main():
    st.set_page_config(page_title="Computer Use Demo", page_icon=":robot:")

    st.title("Computer Use Demo")

    provider = get_api_provider()
    model_name = get_model_name(provider)

    st.sidebar.title("Settings")
    st.sidebar.write(f"Using {provider.name} with the {model_name} model.")

    hide_images = st.sidebar.checkbox("Hide images", value=False)
    st.session_state.hide_images = hide_images

    chat_history: List[ChatMessage] = []
    user_input = st.text_area("Enter your message:", height=100)

    if st.button("Send"):
        chat_history.append(ChatMessage(role="user", content=user_input))
        user_input = ""

        with st.spinner("Generating response..."):
            try:
                response = sampling_loop(provider, model_name, chat_history)
                chat_history.append(response)
            except Exception as e:
                error_message = f"Error: {str(e)}"
                chat_history.append(ChatMessage(role="assistant", content="", error=error_message))

        for message in chat_history:
            display_chat_message(message, is_tool_result=hasattr(message, "error"))

        if chat_history and not hasattr(chat_history[-1], "error"):
            display_image(
                chat_history[-1].image,
                is_tool_result=True,
                delta_generator=st if not hide_images else None,
            )

if __name__ == "__main__":
    main()
