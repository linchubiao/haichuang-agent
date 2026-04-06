import streamlit as st
import dashscope
from dashscope import Generation
import base64

# =================配置区域=================
# 请在这里填入你的阿里云 API KEY
DASHSCOPE_API_KEY = "sk-6ef773f5f0f84a11bff331c699635036"
dashscope.api_key = DASHSCOPE_API_KEY
# 设置模型名称
MODEL_NAME = "qwen-plus" 
# =================配置区域=================

# 设置页面配置
st.set_page_config(
    page_title="海创智驱思政智能体", 
    page_icon="🚩",
    layout="wide"  # 宽屏布局适配视频展示
)

# 自定义CSS美化样式
def load_custom_css():
    st.markdown("""
    <style>
    /* 全局样式 */
    .main {
        background-color: #f0f8ff;
    }
    /* 登录界面容器 */
    .login-container {
        max-width: 600px;
        margin: 0 auto;
        padding: 2rem;
        background: linear-gradient(135deg, #e6f7ff 0%, #f0f9ff 100%);
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 123, 255, 0.15);
        border: 1px solid #b3d9ff;
    }
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 123, 255, 0.2);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 123, 255, 0.3);
        background: linear-gradient(135deg, #0069d9 0%, #004085 100%);
    }
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 4px rgba(0, 123, 255, 0.2);
    }
    /* 输入框样式 */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #b3d9ff;
        padding: 0.6rem;
        box-shadow: inset 0 2px 4px rgba(0, 123, 255, 0.05);
    }
    /* 视频卡片样式 */
    .video-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease;
        height: 100%;
    }
    .video-card:hover {
        transform: translateY(-5px);
    }
    /* 标题样式 */
    .page-title {
        color: #004085;
        text-align: center;
        font-weight: 700;
        margin-bottom: 2rem;
    }
    /* 人物名称样式 */
    .person-name {
        color: #0056b3;
        font-weight: 600;
        margin-top: 1rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 定义思政智能体的系统提示词 (System Prompt)
SYSTEM_PROMPT = """
你是一名专业前景分析与学生规划顾问，任务是：
1. 结合中国当前核心政治方向与国家战略，以及视频中人物的行业背景、贡献领域；
2. 分析相关行业发展、就业市场、政策导向，进而分析学生所选专业的前景；
3. 针对学生提出的具体问题，结合视频人物的职业路径和行业特点，给出清晰、务实、可执行的回答，包括专业优势、劣势、就业方向、学习建议、升学与职业规划。
"""

# 初始化 Session State
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'selected_person' not in st.session_state:
    st.session_state['selected_person'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# =================登录页面逻辑=================
def login_page():
    load_custom_css()
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    
    # 登录界面标题
    st.markdown("<h2 style='text-align:center; color:#004085;'>🚩 海创智驱思政智能体平台</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#6c757d;'>中国海军风范 · 海洋人才思政教育</p >", unsafe_allow_html=True)
    
    # 嵌入中国海军风范视频（支持本地视频/在线视频）
    # 注意：替换为实际视频链接/本地路径，建议使用MP4格式
    st.markdown("<h5 style='color:#0056b3; margin-top:1.5rem;'>🇨🇳 中国海军风范展示</h5>", unsafe_allow_html=True)
    # 示例使用在线视频，本地视频可替换为: video_file = open("navy_video.mp4", "rb"); video_bytes = video_file.read()
    st.video("https://example.com/navy_video.mp4")  # 替换为实际视频URL
    
    # 登录表单
    with st.form("login_form", clear_on_submit=True):
        st.markdown("<br>", unsafe_allow_html=True)
        username = st.text_input("📚 学号/用户名", placeholder="请输入您的学号")
        password = st.text_input("🔒 密码", type="password", placeholder="请输入您的密码")
        submit = st.form_submit_button("登录系统")
        
        if submit:
            # 模拟验证（实际项目请连接数据库）
            if username == "admin" and password == "123456":
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success("✅ 登录成功！正在跳转至人物视频页面...")
                st.rerun()
            else:
                st.error("❌ 用户名或密码错误 (试用账号: admin / 123456)")
    
    st.markdown("</div>", unsafe_allow_html=True)

# =================人物视频页面逻辑=================
def person_video_page():
    load_custom_css()
    
    # 侧边栏
    with st.sidebar:
        st.title("🚩 海创智驱思政智能体")
        st.write(f"当前用户：**{st.session_state['username']}**")
        st.markdown("---")
        if st.button("🔚 退出登录"):
            st.session_state['logged_in'] = False
            st.session_state['selected_person'] = None
            st.rerun()
        st.info("💡 提示：选择下方人物视频，查看详情后可进入智能问答分析专业前景")
    
    # 页面标题
    st.markdown("<h1 class='page-title'>🌊 海洋领域杰出人物展示</h1>", unsafe_allow_html=True)
    
    # 定义人物信息（替换视频URL为实际地址）
    persons = [
        {
            "name": "王书茂",
            "desc": "海洋维权与渔业生产模范",
            "video_url": "https://example.com/wangshumao.mp4"
        },
        {
            "name": "谯禾林",
            "desc": "海洋工程技术专家",
            "video_url": "https://example.com/qiahelin.mp4"
        },
        {
            "name": "曾呈奎",
            "desc": "海洋生物学家，中国海藻学奠基人",
            "video_url": "https://example.com/zengchengkui.mp4"
        },
        {
            "name": "杨金海",
            "desc": "海洋经济与政策研究专家",
            "video_url": "https://example.com/yangjinhai.mp4"
        }
    ]
    
    # 网格布局展示视频卡片
    cols = st.columns(2)  # 2列布局
    for idx, person in enumerate(persons):
        with cols[idx % 2]:
            st.markdown("<div class='video-card'>", unsafe_allow_html=True)
            st.markdown(f"<h3 class='person-name'>{person['name']}</h3>", unsafe_allow_html=True)
            st.caption(f"📝 领域：{person['desc']}")
            st.video(person['video_url'])  # 嵌入人物视频
            # 进入聊天框按钮
            if st.button(f"🎯 分析{person['name']}相关专业前景", key=f"btn_{idx}"):
                st.session_state['selected_person'] = person
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# =================AI 问答页面逻辑=================
def chat_page():
    load_custom_css()
    selected_person = st.session_state['selected_person']
    
    # 侧边栏
    with st.sidebar:
        st.title("🚩 海创智驱思政智能体")
        st.write(f"当前用户：**{st.session_state['username']}**")
        st.markdown(f"📌 分析人物：**{selected_person['name']}**")
        st.markdown("---")
        if st.button("🔙 返回人物列表"):
            st.session_state['selected_person'] = None
            st.rerun()
        if st.button("🔚 退出登录"):
            st.session_state['logged_in'] = False
            st.session_state['selected_person'] = None
            st.rerun()
        st.info(f"💡 可提问：{selected_person['name']}相关专业有哪些？海洋类专业就业前景？")
    
    # 主界面标题
    st.markdown(f"<h1 class='page-title'>🤖 {selected_person['name']} 相关专业前景分析</h1>", unsafe_allow_html=True)
    
    # 显示选中人物的视频（顶部）
    st.markdown(f"<h4 style='color:#0056b3;'>🎬 {selected_person['name']} 视频回顾</h4>", unsafe_allow_html=True)
    st.video(selected_person['video_url'])
    st.markdown("---", unsafe_allow_html=True)
    
    # 显示历史聊天记录
    for message in st.session_state['messages']:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 处理用户输入
    if prompt := st.chat_input(f"请输入关于{selected_person['name']}相关的专业问题..."):
        # 1. 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state['messages'].append({"role": "user", "content": prompt})

        # 2. 调用千问大模型（结合人物信息）
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🤔 正在结合人物背景分析中...")
            
            try:
                # 构建增强版消息（加入人物信息）
                enhanced_system_prompt = f"{SYSTEM_PROMPT}\n当前分析人物：{selected_person['name']}，领域：{selected_person['desc']}"
                messages_history = [{'role': 'system', 'content': enhanced_system_prompt}] + \
                                   st.session_state['messages']
                
                response = Generation.call(
                    model=MODEL_NAME,
                    messages=messages_history,
                    result_format='message',
                    stream=False,  # 非流式输出
                    temperature=0.7  # 调整创造性
                )

                if response.status_code == 200:
                    ai_content = response.output.choices[0].message.content
                    message_placeholder.markdown(ai_content)
                    # 保存助手回复到历史
                    st.session_state['messages'].append({"role": "assistant", "content": ai_content})
                else:
                    message_placeholder.error(f"❌ 请求失败: {response.message}")
                    
            except Exception as e:
                message_placeholder.error(f"❌ 发生错误: {str(e)}")

# =================主程序入口=================
def main():
    # 状态路由
    if not st.session_state['logged_in']:
        login_page()
    else:
        if st.session_state['selected_person'] is None:
            person_video_page()
        else:
            chat_page()

if __name__ == "__main__":
    main()