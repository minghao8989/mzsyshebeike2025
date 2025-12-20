import streamlit as st
import json
import os

# 导入模块
try:
    from modules.asset_page import show_asset
    from modules.repair_page import show_repair
    from modules.file_library import show_library
except ImportError as e:
    st.error(f"模块导入失败: {e}")

# --- 核心 UI 增强 CSS ---
def local_css():
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
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {background: rgba(0,0,0,0) !important;}
        [data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.95) !important;
            border-right: 1px solid rgba(255,255,255,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

# --- 数据持久化逻辑 ---
CONFIG_PATH = "data/config.json"
USERS_PATH = "data/users.json"

def load_config():
    default = {
        "sidebar_tag": "三甲医院信息化工具",
        "sidebar_title": "装备科平台",
        "main_title": "医疗装备全生命周期管理平台",
        "lock_message": "核心业务模块已锁定。请登录以获取实时资产数据与文件调阅权限。"
    }
    if not os.path.exists(CONFIG_PATH):
        return default
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return {**default, **json.load(f)}

def save_config(new_config):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(new_config, f, ensure_ascii=False, indent=4)

# --- 初始化 ---
local_css()
config = load_config()
users_db = load_json(USERS_PATH, {"admin": {"password": "123", "role": "admin", "name": "主任"}})

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 侧边栏 ---
with st.sidebar:
    # 自定义：侧边栏标题
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

# --- 路由控制 ---
if "系统首页" in choice:
    # 自定义：首页大标题
    st.markdown(f"<div class='main-title'>{config['main_title']}</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.2rem; color:#94a3b8;'>Digital Asset & Service Management for Healthcare</p>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        # 自定义：未登录锁定信息
        st.markdown(f"""
            <div style='background: rgba(56, 189, 248, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #38bdf8;'>
                🔒 {config['lock_message']}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.success(f"🚀 欢迎回来，{st.session_state.user_name}。系统运行正常。")

    # 装饰卡片
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("<div class='glass-card'><h3>📊 资产全景</h3></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='glass-card'><h3>🛠️ 智能维保</h3></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='glass-card'><h3>📋 规范文库</h3></div>", unsafe_allow_html=True)

elif "用户登录" in choice:
    st.subheader("👤 内部系统登录")
    with st.form("login_form"):
        u = st.text_input("账号")
        p = st.text_input("密码", type="password")
        if st.form_submit_button("验证并进入系统"):
            if u in users_db and users_db[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user_role = users_db[u]["role"]
                st.session_state.user_name = users_db[u]["name"]
                st.rerun()
            else:
                st.error("失败")

elif "后台管理" in choice:
    st.header("⚙️ 后台文库与标题管理")
    
    with st.expander("📝 界面文字自定义", expanded=True):
        new_sidebar_title = st.text_input("左侧标题（原：装备科平台）", config['sidebar_title'])
        new_main_title = st.text_input("首页大标题", config['main_title'])
        new_lock_msg = st.text_area("未登录提示语", config['lock_message'])
        new_tag = st.text_input("蓝色小标签", config['sidebar_tag'])

    if st.button("💾 保存并更新全院界面"):
        config.update({
            "sidebar_title": new_sidebar_title,
            "main_title": new_main_title,
            "lock_message": new_lock_msg,
            "sidebar_tag": new_tag
        })
        save_config(config)
        st.success("配置已生效！")
        time.sleep(1)
        st.rerun()

elif "资产档案" in choice: show_asset()
elif "维修管理" in choice: show_repair()
elif "工作文件库" in choice: show_library()
elif "注销" in choice:
    st.session_state.logged_in = False
    st.rerun()
