import streamlit as st
from openai import OpenAI
import pandas as pd
import json
from mapneed import prompt, get_completion

# 初始化 OpenAI 客户端
client = OpenAI()

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

with st.sidebar:
    st.title("🔧 Settings")
    st.caption("🚀 Configure the chatbot")

left_column, right_column = st.columns(2)

with left_column:
    data_JSON = {}

    msg_contianer = st.container(height=700, border=True)
    msg_contianer.title("💬 Chatbot")
    msg_contianer.caption("🚀 A Streamlit chatbot powered by OpenAI")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
    
    for msg in st.session_state.messages:
        msg_contianer.chat_message(msg["role"]).write(msg["content"])

    with st.container(border=True):
        
        if use_msg := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": use_msg})
            msg_contianer.chat_message("user").write(use_msg)
            input_msg = prompt(use_msg)
            response = get_completion(input_msg)
            new_string = response.replace("```", "")
            new_res = new_string.replace("json", "")
            data_JSON = json.loads(new_res)
            st.session_state.messages.append({"role": "assistant", "content": response})
            msg_contianer.chat_message("assistant").write(response)

            with right_column:
                map_data = pd.DataFrame(
                data_JSON["制图信息"]["CoorList"],
                columns=['lat', 'lon'])

                st.map(map_data, use_container_width=True)
