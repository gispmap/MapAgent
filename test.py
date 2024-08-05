import streamlit as st
import matplotlib.pyplot as plt
from openai import OpenAI
import json
from mapneed import prompt, get_completion

# 初始化 OpenAI 客户端
client = OpenAI()

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

with st.sidebar:
    st.title("🔧 Settings")
    st.caption("🚀 Configure the chatbot")

left_column, right_column = st.columns([1, 2])

with left_column:
    msg_contianer = st.container(height=700, border=True)
    msg_contianer.title("💬 Chatbot")
    msg_contianer.caption("🚀 A Streamlit chatbot powered by OpenAI")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
    
    for msg in st.session_state.messages:
        msg_contianer.chat_message(msg["role"]).write(msg["content"])
    if "data_JSON" not in st.session_state:
        st.session_state["data_JSON"] = {}

    with st.container(border=True):
        
        if use_msg := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": use_msg})
            msg_contianer.chat_message("user").write(use_msg)
            input_msg = prompt(use_msg)
            response = get_completion(input_msg)
            new_string = response.replace("```", "")
            new_res = new_string.replace("json", "")
            data_JSON = json.loads(new_res)
            st.session_state["data_JSON"] = data_JSON
            st.session_state.messages.append({"role": "assistant", "content": response})
            msg_contianer.chat_message("assistant").write(response)

# 在右侧显示地图
with right_column:
    fig, ax = plt.subplots(figsize=(12, 7))
    if "制图信息" in st.session_state["data_JSON"]:
        try:
            points = st.session_state["data_JSON"]["制图信息"]["CoorList"]
            
            if points:
                fig.patch.set_facecolor('#FFDAB9')
                ax.set_facecolor('#FFDAB9')
                latitudes, longitudes = zip(*points)
                ax.plot(longitudes, latitudes, marker='o', linestyle='-', color='b', label='Route')
                ax.plot(longitudes[0], latitudes[0], marker='o', color='g', markersize=1, label='Start')
                ax.plot(longitudes[-1], latitudes[-1], marker='o', color='r', markersize=1, label='End')
                ax.set_title('Route Display')
                ax.set_xlabel('Longitude')
                ax.set_ylabel('Latitude')
                ax.grid(True)
                ax.legend()
                ax.set_aspect('equal', adjustable='box')
                ax.axis('off')
                # 强制坐标轴框的尺寸
                fig.tight_layout()  # 调整子图参数，以给坐标轴留出更多空间
            else:
                ax.text(0.5, 0.5, 'No data available', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        except KeyError:
            st.error("Error extracting coordinates for map display")
    else:
        # Display empty canvas with light orange background
        ax.set_facecolor('#FFDAB9')
        ax.set_xticks([])
        ax.set_yticks([])
    # 使用 Streamlit 显示图形
    st.pyplot(fig)
