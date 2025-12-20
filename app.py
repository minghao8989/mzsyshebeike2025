import streamlit as st
import json
import os
import time

# 导入模块逻辑
try:
    from modules.asset_page import show_asset
    from modules.repair_page import show_repair
    from modules.file_library import show_library
except ImportError as e:
    st.error(f"模块导入失败，请检查文件结构。错误: {e}")

# --- 1. 核心功能函数 (必须放在调用之前) ---

CONFIG_PATH = "data/config.json"
USERS_PATH = "data/users.json"

def load_json(path, default):
    """通用JSON加载函数"""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default, f, ensure_ascii=False, indent=4)
        return default
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return default

def save_json(path, data):
    """通用JSON保存函数"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 2. 加载配置与初始化 ---

# 确保在这一步之前 load_json 已经定义好了
config = load_json(CONFIG_PATH, {
    "sidebar_tag": "三甲医院信息化工具",
    "sidebar_title": "装备科平台",
    "main_title": "医疗装备全生命周期管理平台",
    "lock_message": "核心业务模块已锁定。请登录以获取实时资产数据与文件调阅权限。"
})

users_db = load_json(USERS_PATH, {
    "admin": {"password": "123", "role": "admin", "name": "主任"}
})

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 3. 科技感 UI 渲染 ---

st.set_page_config(page_title="医疗装备管理系统", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        color: #f8fafc;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
        margin-bottom: 1.5rem;
    }
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    header {background: rgba(0,0,0,0) !important;}
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. 侧边栏 ---

with st.sidebar:
    st.markdown(f"<h2 style='color:#38bdf8;'>🏥 {config['sidebar_title']}</h2>", unsafe_allow_html=True)
    st.caption(f"{config['sidebar_tag']}")
    st.markdown("---")
    
    if st.session_state.logged_in:
        menu = ["✨ 系统首页", "📦 资产档案", "🛠️ 维修管理", "📚 工作文件库"]
        if st.session_state.user_role == "admin":
            menu.append("⚙️ 后台管理")
        menu.append("🔓 注销登录")
    else:
        menu = ["✨ 系统首页", "🔑 用户登录"]
    
    choice = st.sidebar.radio("功能导航", menu)

# --- 5. 路由与逻辑 ---

if "系统首页" in choice:
    st.markdown(f"<div class='main-title'>{config['main_title']}</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.2rem; color:#94a3b8;'>Digital Asset & Service Management for Healthcare</p>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        st.markdown(f"""
            <div style='background: rgba(56, 189, 248, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #38bdf8;'>
                🔒 {config['lock_message']}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.success(f"🚀 您好，{st.session_state.user_name}。系统运行中。")

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='glass-card'><h3>📊 资产全景</h3></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='glass-card'><h3>🛠️ 智能维保</h3></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='glass-card'><h3>📋 规范文库</h3></div>", unsafe_allow_html=True)

elif "用户登录" in choice:
    st.subheader("👤 内部系统登录")
    with st.form("login_form"):
        u = st.text_input("账号")
        p = st.text_input("密码", type="password")
        if st.form_submit_button("进入系统"):
            if u in users_db and users_db[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user_role = users_db[u]["role"]
                st.session_state.user_name = users_db[u]["name"]
                st.rerun()
            else:
                st.error("验证失败")

elif "后台管理" in choice:
    st.header("⚙️ 后台自定义管理")
    with st.expander("📝 界面文字修改", expanded=True):
        config['sidebar_title'] = st.text_input("侧边栏标题", config['sidebar_title'])
        config['main_title'] = st.text_input("首页大标题", config['main_title'])
        config['lock_message'] = st.text_area("未登录提示语", config['lock_message'])
        config['sidebar_tag'] = st.text_input("蓝色小标签", config['sidebar_tag'])

    if st.button("💾 立即保存并更新"):
        save_json(CONFIG_PATH, config)
        st.success("配置已保存！")
        time.sleep(1)
        st.rerun()

elif "资产档案" in choice: show_asset()
elif "维修管理" in choice: show_repair()
elif "工作文件库" in choice: show_library()
elif "注销登录" in choice:
    st.session_state.logged_in = False
    st.rerun()
