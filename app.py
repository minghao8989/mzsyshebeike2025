import streamlit as st
import json
import os
import time
import pandas as pd

# 导入业务模块
try:
    from modules.asset_page import show_asset
    from modules.repair_page import show_repair
    from modules.file_library import show_library
except ImportError as e:
    st.error(f"核心模块导入失败: {e}")

# --- 1. 数据管理核心逻辑 ---
CONFIG_PATH = "data/config.json"
USERS_PATH = "data/users.json"

def load_json_data(path, default_val):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default_val, f, ensure_ascii=False, indent=4)
        return default_val
    with open(path, 'r', encoding='utf-8') as f:
        try: return json.load(f)
        except: return default_val

def save_json_data(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 2. 响应式科技感 CSS ---
def apply_style():
    st.markdown("""
        <style>
        .stApp { background-color: #050a14; color: #f8fafc; }
        .hero-banner {
            background: linear-gradient(rgba(5, 10, 20, 0.75), rgba(5, 10, 20, 0.95)), 
                        url('https://images.unsplash.com/photo-1516549655169-df83a0774514?q=80&w=2070');
            background-size: cover; background-position: center;
            border-radius: 20px; border: 1px solid rgba(59, 130, 246, 0.2);
            padding: 40px clamp(15px, 4vw, 50px); margin-bottom: 2rem;
        }
        .premium-title {
            font-weight: 850; background: linear-gradient(90deg, #3b82f6, #60a5fa, #ffffff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            white-space: nowrap; font-size: clamp(1.5rem, 4vw, 3.5rem); 
            letter-spacing: -1.5px; line-height: 1.2;
        }
        [data-testid="stSidebar"] { background-color: #0a0f1d !important; min-width: 260px !important; }
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [aria-selected="true"] { color: #3b82f6 !important; border-bottom-color: #3b82f6 !important; }
        #MainMenu, footer, header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. 系统初始化 ---
st.set_page_config(page_title="智慧医疗装备管理平台", layout="wide")
apply_style()

# 默认权限全集
ALL_PERMS = ["资产档案", "维修管理", "工作文库", "核心文件", "后台管理"]

config = load_json_data(CONFIG_PATH, {
    "sidebar_title": "装备科平台",
    "sidebar_tag": "三甲医院信息化工具",
    "main_title": "医疗装备全生命周期管理平台",
    "lock_message": "核心业务已锁定。请登录后访问业务数据。"
})

users_db = load_json_data(USERS_PATH, {
    "admin": {"password": "123", "role": "admin", "name": "科主任", "perms": ALL_PERMS}
})

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 4. 侧边栏动态导航 ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#3b82f6; font-size:1.6rem;'>🏥 {config['sidebar_title']}</h2>", unsafe_allow_html=True)
    st.caption(f"{config['sidebar_tag']}")
    st.markdown("---")
    
    menu = ["✨ 平台主页"]
    
    if st.session_state.logged_in:
        # 权限自愈：如果是管理员登录，强制拥有所有权限
        if st.session_state.user_id == "admin":
            st.session_state.user_perms = ALL_PERMS
        
        user_perms = st.session_state.get('user_perms', [])
        
        if "资产档案" in user_perms: menu.append("📊 资产档案")
        if "维修管理" in user_perms: menu.append("🛠️ 维修管理")
        if "工作文库" in user_perms: menu.append("📂 工作文库")
        
        menu.append("👤 个人中心")
        
        if "后台管理" in user_perms or st.session_state.user_id == "admin":
            menu.append("⚙️ 后台管理")
        
        menu.append("🔓 注销退出")
    else:
        menu.append("🔑 用户登录")
    
    choice = st.sidebar.radio("Navigation", menu, label_visibility="collapsed")
    
    if st.session_state.logged_in:
        st.sidebar.markdown(f"<div style='margin-top:20px; padding:10px; background:rgba(59,130,246,0.1); border-radius:10px; color:#3b82f6; font-size:0.85rem;'>欢迎：{st.session_state.user_name}</div>", unsafe_allow_html=True)

# --- 5. 路由逻辑 ---

if "平台主页" in choice:
    st.markdown(f'<div class="hero-banner"><div class="premium-title">{config["main_title"]}</div><div style="color:#94a3b8; font-size:clamp(0.85rem, 1.2vw, 1.1rem); margin-top:10px;">智能监测 · 精准统计 · 流程溯源</div></div>', unsafe_allow_html=True)
    if not st.session_state.logged_in:
        st.info(f"🔐 {config['lock_message']}")
    else:
        st.success(f"🚀 系统已就绪。您的功能权限：{', '.join(st.session_state.user_perms)}")

elif "用户登录" in choice:
    st.markdown("<div style='max-width:400px; margin:0 auto; padding-top:5vh;'>", unsafe_allow_html=True)
    st.subheader("🔑 身份授权登录")
    with st.form("login_form"):
        u = st.text_input("账号")
        p = st.text_input("密码", type="password")
        if st.form_submit_button("验证登录"):
            if u in users_db and users_db[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user_id = u
                st.session_state.user_name = users_db[u].get("name", "未知用户")
                # 加载权限，若无则设为空列表
                st.session_state.user_perms = users_db[u].get("perms", [])
                st.rerun()
            else: st.error("登录凭据不正确")
    st.markdown("</div>", unsafe_allow_html=True)

elif "后台管理" in choice:
    tab1, tab2, tab3 = st.tabs(["🖼️ 视觉配置", "👥 账号列表", "🔐 权限分配"])
    
    with tab1:
        st.subheader("系统标题管理")
        config['sidebar_title'] = st.text_input("侧边栏标题", config['sidebar_title'])
        config['main_title'] = st.text_input("主标题内容", config['main_title'])
        if st.button("更新配置"):
            save_json_data(CONFIG_PATH, config)
            st.rerun()

    with tab2:
        st.subheader("全员账号概览")
        user_list = [{"账号": k, "姓名": v["name"], "密码": v["password"], "角色": v.get("role", "staff")} for k, v in users_db.items()]
        st.table(pd.DataFrame(user_list))
        
        st.markdown("---")
        st.write("➕ **添加新账号**")
        with st.form("add_user_form"):
            n_u = st.text_input("新账号ID")
            n_n = st.text_input("用户姓名")
            n_p = st.text_input("初始密码", value="123456")
            if st.form_submit_button("确认创建"):
                if n_u and n_u not in users_db:
                    users_db[n_u] = {"password": n_p, "name": n_n, "perms": ["资产档案"], "role": "staff"}
                    save_json_data(USERS_PATH, users_db)
                    st.success("创建成功")
                    st.rerun()

    with tab3:
        st.subheader("精准权限控制")
        target_u = st.selectbox("选择账号进行授权", list(users_db.keys()))
        u_data = users_db[target_u]
        
        with st.form("perm_edit"):
            st.write(f"正在配置：**{u_data['name']}**")
            p_asset = st.checkbox("📊 资产档案权限", value="资产档案" in u_data.get("perms", []))
            p_repair = st.checkbox("🛠️ 维修管理权限", value="维修管理" in u_data.get("perms", []))
            p_library = st.checkbox("📂 工作文库权限", value="工作文库" in u_data.get("perms", []))
            p_core = st.checkbox("🔐 核心隐藏文件权限", value="核心文件" in u_data.get("perms", []))
            p_admin = st.checkbox("⚙️ 后台管理权限", value="后台管理" in u_data.get("perms", []))
            
            if st.form_submit_button("保存权限设置"):
                new_ps = []
                if p_asset: new_ps.append("资产档案")
                if p_repair: new_ps.append("维修管理")
                if p_library: new_ps.append("工作文库")
                if p_core: new_ps.append("核心文件")
                if p_admin: new_ps.append("后台管理")
                users_db[target_u]["perms"] = new_ps
                save_json_data(USERS_PATH, users_db)
                st.success("权限已更新")
                st.rerun()

elif "个人中心" in choice:
    st.header("👤 个人中心")
    with st.form("pwd_form"):
        new_p = st.text_input("新密码", type="password")
        if st.form_submit_button("修改密码"):
            users_db[st.session_state.user_id]["password"] = new_p
            save_json_data(USERS_PATH, users_db)
            st.success("成功")

elif "资产档案" in choice: show_asset()
elif "维修管理" in choice: show_repair()
elif "工作文库" in choice: show_library()
elif "注销退出" in choice:
    st.session_state.logged_in = False
    st.rerun()
