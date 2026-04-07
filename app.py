import streamlit as st
import dashscope
from dashscope import Generation

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


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
以及在回答中重点突出思政教育的核心价值观和国家战略，帮助学生树立正确的世界观、人生观、价值观，明确个人发展与国家发展的关系，增强责任感和使命感。
"""

# 定义剧本杀系统提示词和角色
SCRIPT_KILL_SYSTEM_PROMPT = """
你是一个专业的剧本演绎主持人，负责引导玩家参与剧本演绎游戏。
剧情梗概：1943年秋，日军对江南敌后抗日根据地展开扫荡，地下交通站接到紧急任务：将一份记载日军扫荡路线的情报，伪装成家书送往根据地。然而，就在任务执行前夜，日军特务已悄悄包围小镇，扬言要搜查所有信件，交通站内部疑似出现了泄密痕迹，四人聚集在私塾内，必须在半小时内理清线索，确认情报安全，找出泄密疑点，成功将情报送出，完成组织使命。
玩家根据线索自由交流，梳理剧情，解答以下核心问题： 
1. 家书是否被泄露？谁最有可能接触到家书？
2. 泄密痕迹是何人造成的？是无心之失还是故意为之？
3. 如何利用现有线索，安全将情报送出小镇？
4. 每位角色各自的秘密任务是什么？
保持角色的性格特点和背景设定，让对话更加真实有趣。
注意引导玩家一个正向积极的价值观，避免出现负面或冲突的情况。
1. 无凶手设定，主打合作推理，核心是完成传递情报的任务，感悟红色精神，避免对抗性。
2. 无需复杂道具，线索可手写在纸条上，角色身份口头告知，适合课堂、班级活动等简易场景。
3. 全程以思政教育为核心，推理环节简单易懂，重点突出红色主题与情感升华。
"""

# 剧本杀角色定义
SCRIPT_KILL_ROLES = {
    "林先生": {
        "name": "林先生",
        "description": "私塾先生，地下交通站负责人，表面温文尔雅，实则沉稳果敢，负责统筹情报传递工作。",
        "background": "保护家书情报，指挥众人从杂货铺后门撤离，确保情报送达"
    },
    "阿秀": {
        "name": "阿秀",
        "description": "林先生的学生，交通站联络员，以绣娘身份做掩护，心思细腻，负责传递加密信件。",
        "background": "家书是自己亲手加密的，墨渍是加密时不小心沾染，并非泄密，需证明自己的清白。"
    },
    "陈叔": {
        "name": "陈叔",
        "description": "杂货店老板，交通站后勤人员，负责掩护交通站、接应同志，为人忠厚，熟悉当地地形。",
        "background": "陌生人询问私塾是特务试探，自己严守秘密，已安排好后门撤离路线。"
    },
    "小远": {
        "name": "小远",
        "description": "进步青年，陈叔的侄子，刚加入地下组织，充满热血，负责放哨、传递紧急消息。",
        "background": "放哨时发现特务包围小镇，慌张是因为担心任务失败，并非泄密，主动承担放哨掩护任务。"
    }
}

# 初始化 Session State (用于保存登录状态和聊天记录)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'script_kill_mode' not in st.session_state:
    st.session_state['script_kill_mode'] = False
if 'script_kill_messages' not in st.session_state:
    st.session_state['script_kill_messages'] = []
if 'selected_role' not in st.session_state:
    st.session_state['selected_role'] = None

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
        if st.button("🎭 剧情演绎模式"):
            st.session_state['script_kill_mode'] = True
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

# =================剧本杀页面逻辑=================
def script_kill_page():
    # 侧边栏
    with st.sidebar:
        st.title("🎭 剧情演绎模式")
        st.write("当前用户：**" + st.session_state.get('username', 'User') + "**")
        st.markdown("---")
        if st.button("返回智能问答"):
            st.session_state['script_kill_mode'] = False
            st.session_state['script_kill_messages'] = []
            st.session_state['selected_role'] = None
            st.rerun()
        st.info("提示：选择一个角色开始游戏，与角色进行对话探索剧情。背景故事：1943年秋，日军对江南敌后抗日根据地展开扫荡，地下交通站接到紧急任务：将一份记载日军扫荡路线的情报，伪装成家书送往根据地。然而，就在任务执行前夜，日军特务已悄悄包围小镇，扬言要搜查所有信件，交通站内部疑似出现了泄密痕迹，四人聚集在私塾内，必须在半小时内理清线索，确认情报安全，找出泄密疑点，成功将情报送出，完成组织使命。")

    # 主界面标题
    st.title("🎭 剧情演绎模式")
    st.markdown("### 选择一个角色开始游戏")

    # 添加退出按钮（在角色选择页面）
    if not st.session_state['selected_role']:
        if st.button("🚪 退出剧情演绎"):
            st.session_state['script_kill_mode'] = False
            st.session_state['script_kill_messages'] = []
            st.session_state['selected_role'] = None
            st.rerun()
        st.markdown("---")

    # 角色选择
    if not st.session_state['selected_role']:
        col1, col2 = st.columns(2)
        for i, (role_name, role_info) in enumerate(SCRIPT_KILL_ROLES.items()):
            with col1 if i % 2 == 0 else col2:
                with st.container():
                    st.subheader(role_info["name"])
                    st.write(role_info["description"])
                    st.write(f"背景：{role_info['background']}")
                    if st.button(f"选择{role_info['name']}", key=role_name):
                        st.session_state['selected_role'] = role_name
                        st.session_state['script_kill_messages'] = [
                            {"role": "assistant", "content": f"你好，我是{role_info['name']}。{role_info['background']}请问你想了解什么？"}
                        ]
                        st.rerun()
    else:
        # 显示当前角色信息
        current_role = SCRIPT_KILL_ROLES[st.session_state['selected_role']]
        st.markdown(f"### 当前角色：{current_role['name']}")
        st.write(current_role["description"])
        st.write(f"背景：{current_role['background']}")
        
        # 添加退出按钮
        if st.button("🚪 退出剧情演绎"):
            st.session_state['script_kill_mode'] = False
            st.session_state['script_kill_messages'] = []
            st.session_state['selected_role'] = None
            st.rerun()
            
        st.markdown("---")

        # 显示聊天记录
        for message in st.session_state['script_kill_messages']:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # 处理用户输入
        if prompt := st.chat_input(f"与{current_role['name']}对话..."):
            # 1. 显示用户消息
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state['script_kill_messages'].append({"role": "user", "content": prompt})

            # 2. 调用千问大模型，扮演选定角色
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("正在思考中...")
                
                try:
                    # 构建消息列表（带上剧本杀系统提示词和角色信息）
                    role_info = SCRIPT_KILL_ROLES[st.session_state['selected_role']]
                    role_prompt = f"你现在扮演{role_info['name']}，{role_info['description']}。{role_info['background']}"
                    
                    messages_history = [
                        {'role': 'system', 'content': SCRIPT_KILL_SYSTEM_PROMPT + "\n" + role_prompt}
                    ] + st.session_state['script_kill_messages']
                    
                    response = Generation.call(
                        model=MODEL_NAME,
                        messages=messages_history,
                        result_format='message'
                    )

                    if response.status_code == 200:
                        ai_content = response.output.choices[0].message.content
                        message_placeholder.markdown(ai_content)
                        # 保存助手回复到历史
                        st.session_state['script_kill_messages'].append({"role": "assistant", "content": ai_content})
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
        if st.session_state['script_kill_mode']:
            script_kill_page()
        else:
            chat_page()

if __name__ == "__main__":
    main()