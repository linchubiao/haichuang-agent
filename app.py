import streamlit as st
import dashscope
from dashscope import Generation

# =================配置区域=================
# 请在这里填入你的阿里云 API KEY
DASHSCOPE_API_KEY = "sk-6ef773f5f0f84a11bff331c699635036"
dashscope.api_key = DASHSCOPE_API_KEY
# 设置模型名称
MODEL_NAME = "qwen-plus" 
# =================配置区域=================

# 设置页面配置
st.set_page_config(page_title="海创智驱思政智能体", page_icon="🚩")

# 定义思政智能体的系统提示词 (System Prompt)
SYSTEM_PROMPT = """
你是一名专业前景分析与学生规划顾问，任务是：
提炼中国当前核心政治方向与国家战略；
结合当代行业发展、就业市场、政策导向，分析学生所选专业的前景；
针对学生提出的具体问题，给出清晰、务实、可执行的回答，包括专业优势、劣势、就业方向、学习建议、升学与职业规划。
"""

# 初始化 Session State (用于保存登录状态和聊天记录)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# =================登录页面逻辑=================
def login_page():
    st.markdown("### 🚩 欢迎登录海创智驱思政智能体平台")
    st.markdown("请输入您的学号和密码进行验证。")
    
    with st.form("login_form"):
        username = st.text_input("学号/用户名")
        password = st.text_input("密码", type="password")
        submit = st.form_submit_button("登录")
        
        if submit:
            # 这里做一个简单的模拟验证
            # 实际项目中请连接数据库
            if username == "admin" and password == "123456":
                st.session_state['logged_in'] = True
                st.success("登录成功！正在跳转...")
                st.rerun()
            else:
                st.error("用户名或密码错误 (试用: admin / 123456)")

# =================AI 问答页面逻辑=================
def chat_page():
    # 侧边栏
    with st.sidebar:
        st.title("🚩 海创智驱思政智能体")
        st.write("当前用户：**" + st.session_state.get('username', 'User') + "**")
        st.markdown("---")
        if st.button("退出登录"):
            st.session_state['logged_in'] = False
            st.rerun()
        st.info("提示：我是您的专属学业规划顾问，可以问我关于专业选择、就业前景等问题。")

    # 主界面标题
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🤖 智能问答")
    
    # 显示历史聊天记录
    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 处理用户输入
    if prompt := st.chat_input("请输入您的问题..."):
        # 1. 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state['messages'].append({"role": "user", "content": prompt})

        # 2. 调用千问大模型
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("正在思考中...")
            
            try:
                # 构建消息列表（带上系统提示词和历史记录）
                messages_history = [{'role': 'system', 'content': SYSTEM_PROMPT}] + \
                                   st.session_state['messages']
                
                response = Generation.call(
                    model=MODEL_NAME,
                    messages=messages_history,
                    result_format='message'
                )

                if response.status_code == 200:
                    ai_content = response.output.choices[0].message.content
                    message_placeholder.markdown(ai_content)
                    # 保存助手回复到历史
                    st.session_state['messages'].append({"role": "assistant", "content": ai_content})
                else:
                    message_placeholder.error(f"请求失败: {response.message}")
                    
            except Exception as e:
                message_placeholder.error(f"发生错误: {str(e)}")

# =================主程序入口=================
def main():
    # 简单的登录状态路由
    if not st.session_state['logged_in']:
        login_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()