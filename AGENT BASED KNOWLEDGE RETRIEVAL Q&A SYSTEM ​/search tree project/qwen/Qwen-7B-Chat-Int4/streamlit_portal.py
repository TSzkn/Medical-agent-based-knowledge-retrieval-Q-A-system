# # import streamlit as st
# # import requests
# # import time
# # # import matplotlib.pyplot as plt

# # # 设置页面标题和图标
# # st.set_page_config(page_title="AI助手对话", page_icon=":robot_face:")
        
# # from streamlit_chat import message
# # # 设置页面背景颜色和字体

# # import streamlit as st


# # image = {
# #     "user":"patient.png",
# #     "assistant":"Nurse.png"
    
# # }

# # def display_existing_messages():
# #     if "messages" not in st.session_state:
# #         st.session_state["messages"] = []
# #     for message in st.session_state["messages"]:
# #         with st.chat_message(message["role"], avatar=image[message["role"]]):
# #             st.markdown(message["content"])


# # def add_user_message_to_session(prompt):
# #     if prompt:
# #         st.session_state["messages"].append({"role": "user", "content": prompt})
# #         with st.chat_message("user", avatar=image["user"]):
# #             st.markdown(prompt)

# # def generate_assistant_response(query):
# #     # add_user_message_to_session 显示消息的时候做了处理，所以这里不需要再次添加最新提问
# #     print('history-->')
# #     history = st.session_state["messages"]
# #     print(history)
# #     with st.chat_message("assistant", avatar=image["assistant"]):
# #         message_placeholder = st.empty()
# #         full_response = "default response"
# #         start_time = time.time()
# #         # for response in client.chat.completions.create(
# #         #         model=model,
# #         #         temperature=0,
# #         #         messages=history,
# #         #         stream=True,
# #         # ):
# #         #     try:
# #         #         full_response += response.choices[0].delta.content
# #         #     except Exception as e:
# #         #         print("")
# #         #     message_placeholder.markdown(full_response + "▌")
# #         message_placeholder.markdown(full_response)
# #         end_time = time.time()
# #         elapsed_time = end_time - start_time
# #         st.session_state["messages"].append(
# #             {"role": "assistant", "content": full_response}
# #         )
# #         st.session_state.setdefault("elapsed_times", []).append(elapsed_time)
# #     return full_response


# # def hide_streamlit_header_footer():
# #     hide_st_style = """
# #             <style>
# #             #MainMenu {visibility: hidden;}
# #             footer {visibility: hidden;}
# #             header {visibility: hidden;}
# #             #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
# #             </style>
# #             """
# #     st.markdown(hide_st_style, unsafe_allow_html=True)


# # def main():
# #     # 显示标题和描述
# #     st.title("AI助手对话")
# #     st.write("欢迎与我们的AI助手进行交互对话！")
# #     # 显示机器人助手的图像,并将其居中
# #     col2 = st.columns(3)
# #     with col2:
# #         st.image("Nurse.png", width=200)
# #     hide_streamlit_header_footer()
# #     display_existing_messages()
# #     query = st.chat_input("你可以问我任何你想问的问题")
# #     if query:
# #         print(query)
# #         add_user_message_to_session(query)
# #         response = generate_assistant_response(query)
# #         print(response)

# #     st.sidebar.title("聊天内容生成时长")
# #     elapsed_times = st.session_


# import streamlit as st
# import requests

# # 设置页面标题和图标
# st.set_page_config(page_title="AI助手对话", page_icon=":robot_face:",
#                        layout="wide",  # 页面布局
#     initial_sidebar_state="expanded",  # 侧边栏初始状态
#     )

# from streamlit_chat import message
# # 设置页面背景颜色和字体
# import streamlit as st

# image = {
#     "user":"Patient.png",
#     "assistant":"Nurse.png"
# }

# def display_existing_messages():
#     if "messages" not in st.session_state:
#         st.session_state["messages"] = []
#     for message in st.session_state["messages"]:
#         with st.chat_message(message["role"], avatar=image[message["role"]]):
#             st.markdown(message["content"])

# def add_user_message_to_session(prompt):
#     if prompt:
#         st.session_state["messages"].append({"role": "user", "content": prompt})
#         with st.chat_message("user", avatar=image["user"]):
#             st.markdown(prompt)

# def generate_assistant_response(query):
#     # add_user_message_to_session 显示消息的时候做了处理，所以这里不需要再次添加最新提问
#     print('history-->')
#     history = st.session_state["messages"]
#     print(history)
#     with st.chat_message("assistant", avatar=image["assistant"]):
#         message_placeholder = st.empty()
#         full_response = "default response"
#         # for response in client.chat.completions.create(
#         #         model=model,
#         #         temperature=0,
#         #         messages=history,
#         #         stream=True,
#         # ):
#         #     try:
#         #         full_response += response.choices[0].delta.content
#         #     except Exception as e:
#         #         print("")
#         #     message_placeholder.markdown(full_response + "▌")
#         message_placeholder.markdown(full_response)
#         st.session_state["messages"].append(
#             {"role": "assistant", "content": full_response}
#         )
#     return full_response

# def hide_streamlit_header_footer():
#     hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
#             </style>
#             """
#     st.markdown(hide_st_style, unsafe_allow_html=True)

# def main():
#         # 显示标题和描述
#     col1, col2, col3 = st.columns(3)
#     with col2:
#         st.title("医疗助手")
#         st.image("Nurse.png", width=200)

#     hide_streamlit_header_footer()
#     display_existing_messages()

#     query = st.chat_input("你可以问我任何你想问的问题")

#     if query:
#         print(query)
#         add_user_message_to_session(query)
#         response = generate_assistant_response(query)
#         print(response)

# if __name__ == "__main__":
#     main()

import streamlit as st
import requests
from streamlit_chat import message

# 设置页面标题和图标
st.set_page_config(page_title="AI助手对话", page_icon=":robot_face:",
                   layout="wide",  # 页面布局
                   initial_sidebar_state="expanded",  # 侧边栏初始状态
                   )

image = {
    "user": "Patient.png",
    "assistant": "Nurse2.png"
}

def display_existing_messages():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"], avatar=image[message["role"]]):
            st.markdown(message["content"])

def add_user_message_to_session(prompt):
    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=image["user"]):
            st.markdown(prompt)

def generate_assistant_response(query):
    url = "http://36.212.25.245:5110/generate"
    payload = {"text": query}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        generated_text = data.get("generated_text")
        st.session_state["messages"].append(
            {"role": "assistant", "content": generated_text}
        )
        return generated_text
    else:
        error_message = f"Error: {response.status_code}"
        st.session_state["messages"].append(
            {"role": "assistant", "content": error_message}
        )
        return error_message

def hide_streamlit_header_footer():
    hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)

def main():
    # 显示标题和描述
    col1, col2, col3 = st.columns(3)
    with col2:
        # st.title("医疗助手")
        st.image("Nurse2.png", width=250)

    st.markdown(
        "<div style='text-align: center; font-size: 20px; font-weight: bold; margin: 0 auto; width: 80%;'>"
        "您好，我是您的医疗小助手"
        "</div>",
        unsafe_allow_html=True
    )
    
    st.markdown(
        "<div style='text-align: center; font-size: 12px; font-weight: bold; margin: 0 auto; width: 80%;'>"
        "我是基于通义千文以及GLM开发的医疗对话机器人，配备有医疗规范的知识库以及常见疾病的诊断功能，你可以对我进行问诊，心理咨询等～"
        "</div>",
        unsafe_allow_html=True
    )
    
    hide_streamlit_header_footer()
    display_existing_messages()

    query = st.chat_input("你可以问我任何你想问的问题")
    

    if query:
        print(query)
        add_user_message_to_session(query)
        with st.chat_message("assistant", avatar=image["assistant"]):
            message_placeholder = st.empty()
            full_response = generate_assistant_response(query)
            message_placeholder.markdown(full_response)

if __name__ == "__main__":
    main()
