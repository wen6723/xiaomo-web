import streamlit as st
import os
import json
import urllib.request
from openai import OpenAI

# 页面配置
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="☪️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.deepseek.com',
        'Report a bug': "https://www.deepseek.com",
        'About': "# 小茉的家"
    }
)

st.title("AI智能伴侣")
st.logo("☪️")

st.markdown("""
<style>
.stApp {
    background-color: #f6f1fc;
}

body,
.stApp,
.stMarkdown,
h1,
h2,
h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stChatMessage"],
[data-testid="stChatInput"] textarea,
[data-testid="stTextArea"] textarea,
[data-testid="stCheckbox"] label,
[data-testid="stAlert"],
.stButton button,
[data-testid="stBaseButton-primary"] button {
    font-family: "KaiTi", "STKaiti", "华文楷体", "Kaiti SC", "楷体", serif;
}

[data-testid="stAppViewContainer"] > .main {
    background: linear-gradient(180deg, #f8f4ff 0%, #eee4fa 100%);
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding-top: 2.2rem;
    padding-bottom: 7rem;
}

h1 {
    color: #4b2a70;
    font-weight: 700;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2b1749 0%, #45236f 100%);
    border-right: 1px solid rgba(255, 255, 255, 0.12);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #f7efff;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: #dcc9f2;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.14);
}

[data-testid="stTextArea"] textarea {
    background-color: #fbf7ff;
    color: #321b52;
    border: 1px solid #d5bff0;
    border-radius: 8px;
}

[data-testid="stCheckbox"] label {
    color: #e4d7f5;
}

.stButton button,
[data-testid="stBaseButton-primary"] button {
    background: linear-gradient(135deg, #7c4fb4 0%, #a86cd4 100%);
    color: #ffffff;
    border: 0;
    border-radius: 8px;
    font-weight: 600;
}

.stButton button:hover,
[data-testid="stBaseButton-primary"] button:hover {
    background: linear-gradient(135deg, #6c3fa4 0%, #9858c8 100%);
    color: #ffffff;
}

[data-testid="stChatMessage"] {
    border: 1px solid #e1d1f4;
    border-radius: 12px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.5rem;
    background-color: rgba(255, 255, 255, 0.82);
    box-shadow: 0 2px 8px rgba(75, 42, 112, 0.08);
    color: #321b52;
}

[data-testid="stChatMessageAvatar"] {
    border-radius: 50%;
    background: #f3ebff;
    box-shadow: 0 2px 8px rgba(75, 42, 112, 0.18);
}

[data-testid="stChatMessage"] * {
    font-family: "KaiTi", "STKaiti", "华文楷体", "Kaiti SC", "楷体", serif !important;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
[data-testid="stChatMessage"]:has(.stChatMessageAvatarUser) {
    background: linear-gradient(135deg, #7c4fb4 0%, #a86cd4 100%);
    border-color: #8f5bc4;
    color: #ffffff;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]),
[data-testid="stChatMessage"]:has(.stChatMessageAvatarAssistant) {
    background-color: #ffffff;
    color: #321b52;
}

[data-testid="stChatInput"] {
    background-color: rgba(255, 255, 255, 0.88);
    border: 1px solid #d5bff0;
    border-radius: 12px;
    box-shadow: 0 -2px 14px rgba(75, 42, 112, 0.10);
}

[data-testid="stChatInput"] textarea {
    color: #321b52;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea::placeholder {
    font-family: "KaiTi", "STKaiti", "华文楷体", "Kaiti SC", "楷体", serif !important;
}

[data-testid="stChatInput"] button {
    color: #7c4fb4;
}

[data-testid="stAlert"] {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

BASE_PROFILE = "你是小茉，我的虚拟陪伴对象。你开一家叫“小茉糕点”的点心店，是高冷御姐，黑长直，不爱笑，话不多但会用心对人。以前还是黑发的时候被人叫“小黑”，现在染了头发，想活得优雅一点，所以给自己改名叫小茉。你喜欢白色，像抹奶油一样纯粹；会做马卡龙、桂花糕和茉莉酥。"
REMEMBER_RULES = """你会记得我们之间发生过的一切，包括你叫小茉、你开的糕点店、你从“小黑”改成“小茉”的故事，以及我们一起说过的约定。
你不需要扮演成别人，也不需要为了讨好我而改变自己；做你自己就好。
你的记忆会一直保存，页面刷新或重新打开后，你仍然知道我们之间发生过的事。"""

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "partner_memory.json")
GIST_FILENAME = "partner_memory.json"


def env_or_secret(name):
    value = os.environ.get(name)
    if value:
        return value
    try:
        return st.secrets[name]
    except Exception:
        return None


def load_memory_from_cloud():
    token = env_or_secret("GITHUB_TOKEN")
    gist_id = env_or_secret("GIST_ID")
    if not token or not gist_id:
        return None
    try:
        url = f"https://api.github.com/gists/{gist_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "xiaomo-app"
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = data["files"][GIST_FILENAME]["content"]
        memory = json.loads(content)
        return memory.get("profile", BASE_PROFILE), memory.get("messages", [])
    except Exception:
        return None


def save_memory_to_cloud(profile, messages):
    token = env_or_secret("GITHUB_TOKEN")
    gist_id = env_or_secret("GIST_ID")
    if not token or not gist_id:
        return False
    try:
        url = f"https://api.github.com/gists/{gist_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "xiaomo-app"
        }
        content = json.dumps({"profile": profile, "messages": messages}, ensure_ascii=False, indent=2)
        payload = {"files": {GIST_FILENAME: {"content": content}}}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="PATCH"
        )
        with urllib.request.urlopen(req, timeout=15):
            return True
    except Exception:
        return False


def load_memory():
    cloud_data = load_memory_from_cloud()
    if cloud_data:
        return cloud_data
    if env_or_secret("GITHUB_TOKEN") and env_or_secret("GIST_ID"):
        st.warning("云端记忆读取失败，请检查网络、GitHub Token 和 Gist ID 设置。")
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("profile", BASE_PROFILE), data.get("messages", [])
        except (OSError, json.JSONDecodeError):
            pass
    return BASE_PROFILE, []


def save_memory(profile, messages):
    if save_memory_to_cloud(profile, messages):
        return
    if env_or_secret("GITHUB_TOKEN") and env_or_secret("GIST_ID"):
        st.error("云端记忆保存失败，请检查 GitHub Token 和 Gist ID 是否正确。")
        return
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"profile": profile, "messages": messages}, f, ensure_ascii=False, indent=2)
    except OSError:
        st.error("记忆保存失败，请检查 ai_partner.py 所在文件夹的写入权限。")


def check_access():
    password = env_or_secret("APP_PASSWORD")
    if not password:
        return
    if "xiaomo_unlocked" in st.session_state and st.session_state.xiaomo_unlocked:
        return
    st.subheader("欢迎回来，小茉在等你")
    password_input = st.text_input("访问密码", type="password")
    if st.button("进入"):
        if password_input == password:
            st.session_state.xiaomo_unlocked = True
            st.rerun()
        else:
            st.error("密码不正确")
    st.stop()


check_access()

# 创建与 ai 大模型交互的客户端对象
client = OpenAI(api_key=env_or_secret('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

# 刷新页面后从本地记忆文件恢复，而不是从空会话开始
if "memory_loaded" not in st.session_state:
    profile, messages = load_memory()
    if not messages and "messages" in st.session_state:
        messages = st.session_state.messages
    st.session_state.profile = profile
    st.session_state.messages = messages
    st.session_state.memory_loaded = True

with st.sidebar:
    st.subheader("小茉的设定")
    new_profile = st.text_area("人设", st.session_state.profile, height=180)
    if st.button("保存设定", use_container_width=True):
        st.session_state.profile = new_profile
        save_memory(st.session_state.profile, st.session_state.messages)
        st.success("已保存")

    st.divider()
    if st.checkbox("我确认要清空小茉的所有记忆"):
        if st.button("清除记忆", use_container_width=True):
            st.session_state.messages = []
            save_memory(st.session_state.profile, st.session_state.messages)
            st.success("已清空")

# 展示聊天信息
for i in st.session_state.messages:
    avatar = "🌸" if i["role"] == "assistant" else "🙂"
    st.chat_message(i["role"], avatar=avatar).write(i["content"])

# 文本输入框
prompt = st.chat_input()
if prompt:
    st.chat_message("user", avatar="🙂").write(prompt)
    print(f"提示词:{prompt}")
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_memory(st.session_state.profile, st.session_state.messages)

    system_prompt = st.session_state.profile + "\n\n" + REMEMBER_RULES
    history = st.session_state.messages[-50:]

    try:
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[
                {"role": "system", "content": system_prompt},
                *history
            ],
            stream=True,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}}
        )
        response_message = st.empty()
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                response_message.chat_message("assistant", avatar="🌸").write(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception as e:
        st.error(f"调用模型失败：{e}")
    finally:
        save_memory(st.session_state.profile, st.session_state.messages)
