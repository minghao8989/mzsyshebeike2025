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
    st.error(f"核心模块导入失败，请检查 modules 文件夹。错误信息: {e}")

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
            white-space: nowrap; font-size: clamp(1.5rem, 4vw, 4rem); 
            letter-spacing: -1.5px; line-height: 1.2;
        }
        .info-card {
            background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px);
            border-radius: 15px; padding: 1.2rem; border: 1px solid rgba(255, 255, 255, 0.08);
            height: 100%; transition: all 0.3s ease;
        }
        [data-testid="stSidebar"] { background-color: #0a0f1d !important; min-width: 260px !important; }
        #MainMenu, footer, header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. 系统初始化 ---
st.set_page_config(page_title="智慧医疗装备管理平台", layout="wide")
apply_style()

config = load_json_data(CONFIG_PATH, {
    "sidebar_title": "装备科平台",
    "sidebar_tag": "三甲医院信息化工具",
    "main_title": "医疗装备全生命周期管理平台",
    "lock_message": "核心业务已锁定。请登录后访问资产与维保数据。"
})
users_db = load_json_data(USERS_PATH, {"admin": {"password": "123", "role": "admin", "name": "科主任"}})

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 4. 侧边栏导航 ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#3b82f6; font-size:1.6rem;'>🏥 {config['sidebar_title']}</h2>", unsafe_allow_html=True)
    st.caption(f"{config['sidebar_tag']}")
    st.markdown("---")
    
    if st.session_state.logged_in:
        menu = ["✨ 平台主页", "📊 资产档案", "🛠️ 维修管理", "📂 工作文库", "👤 个人中心"]
        if st.session_state.user_role == "admin":
            menu.append("⚙️ 后台管理")
        menu.append("🔓 注销退出")
    else:
        menu = ["✨ 平台主页", "🔑 用户登录"]
    
    choice = st.sidebar.radio("Navigation", menu, label_visibility="collapsed")
    
    if st.session_state.logged_in:
        st.sidebar.markdown(f"<div style='margin-top:20px; padding:10px; background:rgba(59,130,246,0.1); border-radius:10px; color:#3b82f6; font-size:0.85rem;'>当前用户：{st.session_state.user_name}</div>", unsafe_allow_html=True)

# --- 5. 路由逻辑 ---

if "平台主页" in choice:
    st.markdown(f'<div class="hero-banner"><div class="premium-title">{config["main_title"]}</div><div style="color:#94a3b8; font-size:clamp(0.85rem, 1.2vw, 1.1rem); margin-top:10px;">智能监测 · 精准统计 · 流程溯源</div></div>', unsafe_allow_html=True)
    if not st.session_state.logged_in:
        st.info(f"🔐 {config['lock_message']}")
    
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="info-card"><h3 style="color:#3b82f6;">资产台账</h3><p style="color:#64748b; font-size:0.9rem;">全生命周期追溯，掌握全院设备分布。</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="info-card"><h3 style="color:#3b82f6;">智能维保</h3><p style="color:#64748b; font-size:0.9rem;">临床一键扫码，流程全透明监控。</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="info-card"><h3 style="color:#3b82f6;">规范文库</h3><p style="color:#64748b; font-size:0.9rem;">国家强检标准与办公模板共享。</p></div>', unsafe_allow_html=True)

elif "用户登录" in choice:
    st.markdown("<div style='max-width:400px; margin:0 auto; padding-top:5vh;'>", unsafe_allow_html=True)
    st.subheader("🔑 身份授权登录")
    with st.form("login_form"):
        u = st.text_input("账号")
        p = st.text_input("密码", type="password")
        if st.form_submit_button("验证登录"):
            if u in users_db and users_db[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user_role = users_db[u]["role"]
                st.session_state.user_name = users_db[u]["name"]
                st.session_state.user_id = u
                st.rerun()
            else: st.error("验证失败")
    st.markdown("</div>", unsafe_allow_html=True)

elif "个人中心" in choice:
    st.header("👤 个人账号安全")
    with st.form("change_pwd"):
        st.write(f"当前用户：{st.session_state.user_name} ({st.session_state.user_id})")
        new_pw = st.text_input("设置新密码", type="password")
        confirm_pw = st.text_input("确认新密码", type="password")
        if st.form_submit_button("确认修改"):
            if new_pw and new_pw == confirm_pw:
                users_db[st.session_state.user_id]["password"] = new_pw
                save_json_data(USERS_PATH, users_db)
                st.success("密码修改成功！下次登录生效。")
            else: st.error("两次密码输入不一致或为空")

elif "后台管理" in choice:
    tab1, tab2 = st.tabs(["🖼️ 界面配置", "👥 账号管理"])
    
    with tab1:
        st.subheader("系统文案设置")
        config['sidebar_title'] = st.text_input("侧边栏标题", config['sidebar_title'])
        config['main_title'] = st.text_input("首页流光标题", config['main_title'])
        config['lock_message'] = st.text_area("未登录提示", config['lock_message'])
        if st.button("保存界面配置"):
            save_json_data(CONFIG_PATH, config)
            st.success("界面更新成功")
            st.rerun()

    with tab2:
        st.subheader("科室账号运维")
        # 显示当前用户表
        user_list = [{"账号": k, "姓名": v["name"], "角色": v["role"], "密码": v["password"]} for k, v in users_db.items()]
        df_users = pd.DataFrame(user_list)
        st.dataframe(df_users, use_container_width=True)
        
        st.markdown("---")
        st.write("➕ **添加新账号**")
        with st.form("add_user"):
            new_u = st.text_input("新账号 (ID)")
            new_n = st.text_input("姓名")
            new_p = st.text_input("初始密码")
            new_r = st.selectbox("权限角色", ["staff", "admin"])
            if st.form_submit_button("确认添加"):
                if new_u and new_u not in users_db:
                    users_db[new_u] = {"password": new_p, "role": new_r, "name": new_n}
                    save_json_data(USERS_PATH, users_db)
                    st.success(f"用户 {new_n} 添加成功")
                    st.rerun()
                else: st.error("账号已存在或信息不全")

elif "资产档案" in choice: show_asset()
elif "维修管理" in choice: show_repair()
elif "工作文库" in choice: show_library()
elif "注销退出" in choice:
    st.session_state.logged_in = False
    st.rerun()
