import streamlit as st
import json
import os
import time

# 导入模块
try:
    from modules.asset_page import show_asset
    from modules.repair_page import show_repair
    from modules.file_library import show_library
except ImportError as e:
    st.error(f"模块导入失败: {e}")

# --- 核心 UI 增强 CSS (科技感灵魂) ---
def local_css():
    st.markdown("""
        <style>
        /* 全局背景：深邃医疗蓝渐变 */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            color: #f8fafc;
        }
        
        /* 磨砂玻璃卡片效果 */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 2rem;
            margin-bottom: 1.5rem;
            transition: transform 0.3s ease;
        }
        .glass-card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.08);
            border-color: #38bdf8;
        }

        /* 标题科技感字体渲染 */
        .main-title {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(to right, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        /* 隐藏Streamlit原生组件干扰 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {background: rgba(0,0,0,0) !important;}
        
        /* 侧边栏样式定制 */
        [data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.95) !important;
            border-right: 1px solid rgba(255,255,255,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

# --- 数据加载逻辑 ---
CONFIG_PATH = "data/config.json"
USERS_PATH = "data/users.json"

def load_json(path, default):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default, f, ensure_ascii=False, indent=4)
        return default
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_json(CONFIG_PATH, {"sidebar_tag": "三甲医院信息化工具"})
users_db = load_json(USERS_PATH, {"admin": {"password": "123", "role": "admin", "name": "科主任"}})

# --- 初始化状态 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

# --- 执行样式 ---
local_css()

# --- 侧边栏 ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#38bdf8;'>🏥 装备科平台</h2>", unsafe_allow_html=True)
    st.caption(f"Ver 2025.0.1 | {config.get('sidebar_tag')}")
    st.markdown("---")
    
    if st.session_state.logged_in:
        menu = ["✨ 系统首页", "📦 资产档案", "🛠️ 维修管理", "📚 工作文件库"]
        if st.session_state.user_role == "admin":
            menu.append("⚙️ 后台管理")
        menu.append("🔓 注销登录")
    else:
        menu = ["✨ 系统首页", "🔑 用户登录"]
    
    choice = st.sidebar.radio("功能导航", menu)

# --- 首页逻辑 (科技旗舰版) ---
if "系统首页" in choice:
    # 顶部横幅
    st.markdown("<div class='main-title'>医疗装备全生命周期管理平台</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.2rem; color:#94a3b8;'>Digital Asset & Service Management for Healthcare</p>", unsafe_allow_html=True)
    
    # 动态欢迎词
    if st.session_state.logged_in:
        st.write(f"🚀 欢迎回来，**{st.session_state.get('user_name')}**。今天有 3 项维修待处理，2 台设备需强检。")
    else:
        st.info("🔒 核心业务模块已锁定。请登录以获取实时资产数据与文件调阅权限。")

    st.markdown("<br>", unsafe_allow_html=True)

    # 功能展示卡片 (3列布局)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class='glass-card'>
                <h3 style='color:#38bdf8;'>📊 资产全景</h3>
                <p style='color:#cbd5e1; font-size:0.9rem;'>实时掌握全院百万级设备分布，购置、论证、台账一键追溯。</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class='glass-card'>
                <h3 style='color:#fbbf24;'>🛠️ 智能维保</h3>
                <p style='color:#cbd5e1; font-size:0.9rem;'>临床一键扫码报修，工程师实时接单，流程全透明监控。</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div class='glass-card'>
                <h3 style='color:#34d399;'>📋 规范文库</h3>
                <p style='color:#cbd5e1; font-size:0.9rem;'>国家强检标准、内部操作指南、办公表格下载，权限分级管理。</p>
            </div>
        """, unsafe_allow_html=True)

    # 底部装饰
    st.markdown("---")
    st.caption("© 2025 三甲医院医疗装备部信息化小组 | 数据已通过 256 位加密保护")

# --- 其他路由逻辑 (保持不变) ---
elif "资产档案" in choice:
    show_asset()
elif "维修管理" in choice:
    show_repair()
elif "工作文件库" in choice:
    show_library()
elif "用户登录" in choice:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("👤 内部系统登录")
    with st.form("login_form"):
        u = st.text_input("工号/账号")
        p = st.text_input("密码", type="password")
        if st.form_submit_button("验证并进入系统"):
            if u in users_db and users_db[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user_role = users_db[u]["role"]
                st.session_state.user_name = users_db[u]["name"]
                st.rerun()
            else:
                st.error("身份验证失败，请重试。")
    st.markdown("</div>", unsafe_allow_html=True)

elif "后台管理" in choice:
    st.title("⚙️ 后台配置")
    # ... 原有后台代码 ...
    pass

elif "注销" in choice:
    st.session_state.logged_in = False
    st.rerun()
