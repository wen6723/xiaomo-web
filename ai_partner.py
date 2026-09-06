import streamlit as st
import os
import json
import hmac
import hashlib
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


def normalize_doc(data):
    if data is None:
        return {"users": {}, "legacy": None}
    if "users" not in data:
        legacy = {
            "profile": data.get("profile", BASE_PROFILE),
            "messages": data.get("messages", []),
        }
        return {"users": {}, "legacy": legacy}
    data.setdefault("users", {})
    data.setdefault("legacy", None)
    return data


def load_cloud_doc():
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
        return json.loads(content)
    except Exception:
        return None


def save_cloud_doc(doc):
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
        content = json.dumps(doc, ensure_ascii=False, indent=2)
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


def load_storage_doc():
    cloud_data = load_cloud_doc()
    if cloud_data is not None:
        return normalize_doc(cloud_data)
    if env_or_secret("GITHUB_TOKEN") and env_or_secret("GIST_ID"):
        st.warning("云端记忆读取失败，请检查网络、GitHub Token 和 Gist ID 设置。")
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return normalize_doc(json.load(f))
        except (OSError, json.JSONDecodeError):
            pass
    return normalize_doc(None)


def save_storage_doc(doc):
    if save_cloud_doc(doc):
        return True
    if env_or_secret("GITHUB_TOKEN") and env_or_secret("GIST_ID"):
        st.error("云端记忆保存失败，请检查 GitHub Token 和 Gist ID 是否正确。")
        return False
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        st.error("记忆保存失败，请检查 ai_partner.py 所在文件夹的写入权限。")
        return False


def hash_password(password, salt_hex):
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return digest.hex()


def verify_password(user, password):
    return hmac.compare_digest(
        user.get("password_hash", ""),
        hash_password(password, user.get("salt", ""))
    )


def create_account(doc, username, password, api_key, owner_code=""):
    if not username or not password or not api_key:
        return "用户名、密码和 DeepSeek API Key 都不能为空"
    username = username.strip()
    if len(username) < 2:
        return "用户名至少需要 2 个字符"
    if len(password) < 6:
        return "密码至少需要 6 位"
    if username in doc["users"]:
        return "这个用户名已经存在"
    salt = os.urandom(16).hex()
    doc["users"][username] = {
        "salt": salt,
        "password_hash": hash_password(password, salt),
        "profile": BASE_PROFILE,
        "messages": [],
    }
    owner_secret = env_or_secret("OWNER_CODE")
    if owner_code and owner_secret and hmac.compare_digest(owner_code, owner_secret):
        if doc.get("legacy"):
            doc["users"][username]["profile"] = doc["legacy"].get("profile", BASE_PROFILE)
            doc["users"][username]["messages"] = doc["legacy"].get("messages", [])
            doc["legacy"] = None
    return None


def load_current_user_memory():
    username = st.session_state.auth_user
    if "loaded_user" in st.session_state and st.session_state.loaded_user == username:
        return
    doc = load_storage_doc()
    user = doc["users"].get(username)
    if user is None:
        st.session_state.profile = BASE_PROFILE
        st.session_state.messages = []
    else:
        st.session_state.profile = user.get("profile", BASE_PROFILE)
        st.session_state.messages = user.get("messages", [])
    st.session_state.loaded_user = username


def save_current_user_memory():
    username = st.session_state.auth_user
    doc = load_storage_doc()
    if username not in doc["users"]:
        salt = os.urandom(16).hex()
        doc["users"][username] = {
            "salt": salt,
            "password_hash": hash_password("", salt),
            "profile": st.session_state.profile,
            "messages": st.session_state.messages,
        }
    user = doc["users"][username]
    user["profile"] = st.session_state.profile
    user["messages"] = st.session_state.messages
    save_storage_doc(doc)


def show_auth():
    if "auth_user" in st.session_state:
        return
    login_tab, register_tab = st.tabs(["登录", "注册新账号"])
    with login_tab:
        st.subheader("登录小茉的小屋")
        username = st.text_input("用户名", key="login_username")
        password = st.text_input("密码", type="password", key="login_password")
        api_key = st.text_input(
            "你自己的 DeepSeek API Key",
            type="password",
            key="login_api_key",
            help="只用于本次会话，不会保存到记忆文件"
        )
        if st.button("进入", key="login_submit"):
            if not username or not password or not api_key:
                st.error("用户名、密码和 DeepSeek API Key 都不能为空")
            else:
                doc = load_storage_doc()
                user = doc["users"].get(username.strip())
                if user and verify_password(user, password):
                    st.session_state.auth_user = username.strip()
                    st.session_state.api_key = api_key.strip()
                    st.session_state.loaded_user = None
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
    with register_tab:
        st.subheader("创建自己的小茉")
        new_username = st.text_input("新用户名", key="register_username")
        new_password = st.text_input("设置密码（至少 6 位）", type="password", key="register_password")
        new_api_key = st.text_input(
            "你自己的 DeepSeek API Key",
            type="password",
            key="register_api_key",
            help="只用于你自己的账号，不会保存到记忆文件"
        )
        owner_code = st.text_input(
            "管理员开通码（可选）",
            type="password",
            key="register_owner_code",
            help="创建者开通第一个账号时可填写，用来恢复小茉的旧记忆"
        )
        if st.button("注册并进入", key="register_submit"):
            doc = load_storage_doc()
            error = create_account(
                doc,
                new_username,
                new_password,
                new_api_key,
                owner_code,
            )
            if error:
                st.error(error)
            else:
                if save_storage_doc(doc):
                    st.session_state.auth_user = new_username.strip()
                    st.session_state.api_key = new_api_key.strip()
                    st.session_state.loaded_user = None
                    st.rerun()
                else:
                    st.error("账号创建失败，记忆保存失败")
    st.stop()


show_auth()
load_current_user_memory()

with st.sidebar:
    st.write(f"当前账号：{st.session_state.auth_user}")
    new_key = st.text_input(
        "更换自己的 DeepSeek API Key",
        type="password",
        key="sidebar_api_key",
        value=st.session_state.api_key,
    )
    if st.button("更新 API Key", use_container_width=True):
        if new_key.strip():
            st.session_state.api_key = new_key.strip()
            st.success("已更新")
        else:
            st.error("API Key 不能为空")
    st.divider()
    st.subheader("小茉的设定")
    new_profile = st.text_area("人设", st.session_state.profile, height=180)
    if st.button("保存设定", use_container_width=True):
        st.session_state.profile = new_profile
        save_current_user_memory()
        st.success("已保存")
    st.divider()
    if st.checkbox("我确认要清空这个小茉的所有记忆"):
        if st.button("清除记忆", use_container_width=True):
            st.session_state.messages = []
            save_current_user_memory()
            st.success("已清空")
    st.divider()
    if st.checkbox("我确认要永久删除当前账号及其所有记忆"):
        if st.button("删除当前账号", use_container_width=True):
            username = st.session_state.auth_user
            doc = load_storage_doc()
            if username in doc["users"]:
                del doc["users"][username]
                if save_storage_doc(doc):
                    st.success("账号已删除")
                    for key in ("auth_user", "api_key", "loaded_user", "profile", "messages"):
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
                else:
                    st.error("账号删除失败，云端保存出错")
            else:
                st.error("账号不存在或已经删除")
    if st.button("退出登录", use_container_width=True):
        for key in ("auth_user", "api_key", "loaded_user", "profile", "messages"):
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

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
    save_current_user_memory()

    system_prompt = st.session_state.profile + "\n\n" + REMEMBER_RULES
    history = st.session_state.messages[-50:]

    try:
        client = OpenAI(
            api_key=st.session_state.api_key,
            base_url="https://api.deepseek.com"
        )
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
        save_current_user_memory()
