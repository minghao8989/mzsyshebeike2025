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

# --- 2. 深度定制 CSS ---
def apply_premium_style():
    st.markdown("""
        <style>
        .stApp { background-color: #050a14; color: #f8fafc; }
        
        /* 首页 Hero Section */
        .hero-banner {
            background: linear-gradient(rgba(5, 10, 20, 0.75), rgba(5, 10, 20, 0.95)), 
                        url('https://images.unsplash.com/photo-1516549655169-df83a0774514?q=80&w=2070');
            background-size: cover; background-position: center;
            border-radius: 20px; border: 1px solid rgba(59, 130, 246, 0.2);
            padding: 5% 4%; margin-bottom: 2rem; width: 100%; overflow: hidden;
        }
        
        /* 首页流光标题 (保持单行不换行) */
        .premium-title {
            font-weight: 850;
            background: linear-gradient(90deg, #3b82f6, #60a5fa, #ffffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            white-space: nowrap; 
            font-size: clamp(1.5rem, 4vw, 3.5rem); 
            letter-spacing: -1.5px; line-height: 1.2;
            margin-bottom: 0.8rem; display: block;
        }

        /* --- 侧边栏样式精修 (核心修复：支持换行) --- */
        [data-testid="stSidebar"] {
            background-color: #0a0f1d !important;
            border-right: 1px solid rgba(255,255,255,0.05);
        }
        
        /* 侧边栏标题样式：取消强制单行，增加行高 */
        .sidebar-main-title {
            color: #3b82f6 !important;
            font-size: 1.6rem !important;
            font-weight: 800 !important;
            line-height: 1.3 !important;
            word-wrap: break-word !important;
            word-break: break-all !important;
            margin-bottom: 5px !important;
            text-shadow: 0px 2px 4px rgba(0,0,0,0.5);
        }

        /* 侧边栏文字整体增强 */
        [data-testid="stSidebar"] .stMarkdown p, 
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] label {
            color: #FFFFFF !important;
            font-weight: 500 !important;
        }

        /* 导航菜单选中色 */
        [data-testid="stSidebar"] [aria-selected="true"] {
            color: #3b82f6 !important;
            font-weight: 700 !important;
        }

        #MainMenu, footer, header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. 初始化 ---
st.set_page_config(page_title="智慧医疗装备管理平台", layout="wide")
apply_premium_style()

ALL_PERMS = ["资产档案", "维修管理", "工作文库", "核心文件", "后台管理"]

config = load_json_data(CONFIG_PATH, {
    "sidebar_title": "梅州市第三人民医院装备科平台",
    "sidebar_tag": "设备科信息化工具",
    "main_title": "医疗装备全生命周期管理平台",
    "lock_message": "核心业务已锁定。请登录后访问业务数据。"
})

users_db = load_json_data(USERS_PATH, {
    "admin": {"password": "123", "role": "admin", "name": "科主任", "perms": ALL_PERMS}
})

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 4. 侧边栏 ---
with st.sidebar:
    # 使用自定义 class 渲染标题，支持换行
    st.markdown(f'<div class="sidebar-main-title">🏥 {config["sidebar_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#60a5fa; font-size:0.85rem; margin-top:0;'>{config['sidebar_tag']}</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu = ["✨ 平台首页"]
    if st.session_state.logged_in:
        if st.session_state.user_id == "admin": st.session_state.user_perms = ALL_PERMS
        user_perms = st.session_state.get('user_perms', [])
        
        if "资产档案" in user_perms: menu.append("📊 资产档案")
        if "维修管理" in user_perms: menu.append("🛠️ 维修管理")
        if "工作文库" in user_perms: menu.append("📂 工作文库")
        menu.append("👤 个人中心")
        if "后台管理" in user_perms or st.session_state.user_id == "admin": menu.append("⚙️ 后台管理")
        menu.append("🔓 注销退出")
    else:
        menu.append("🔑 用户登录")
    
    choice = st.sidebar.radio("Nav", menu, label_visibility="collapsed")
    
    if st.session_state.logged_in:
        st.sidebar.markdown(f"<div style='margin-top:20px; padding:12px; background:rgba(59,130,246,0.15); border-radius:10px; border:1px solid #3b82f6; color:#FFFFFF;'>当前用户：{st.session_state.user_name}</div>", unsafe_allow_html=True)

# --- 5. 路由逻辑 ---
if "平台首页" in choice:
    st.markdown(f'<div class="hero-banner"><div class="premium-title">{config["main_title"]}</div><div style="color:#94a3b8; font-size:clamp(0.9rem, 1.3vw, 1.2rem);">智能监测 · 精准统计 · 流程溯源</div></div>', unsafe_allow_html=True)
    if not st.session_state.logged_in:
        st.info(f"🔐 {config['lock_message']}")
    else:
        st.success(f"🚀 系统已就绪。")

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div style="background:rgba(255,255,255,0.03); padding:1.5rem; border-radius:15px; border:1px solid rgba(255,255,255,0.1); height:100%;"><h3 style="color:#3b82f6;">资产全景</h3><p style="color:#64748b;">实时掌握设备分布与价值评估。</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div style="background:rgba(255,255,255,0.03); padding:1.5rem; border-radius:15px; border:1px solid rgba(255,255,255,0.1); height:100%;"><h3 style="color:#3b82f6;">智能维保</h3><p style="color:#64748b;">报修流程节点透明化可追踪。</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div style="background:rgba(255,255,255,0.03); padding:1.5rem; border-radius:15px; border:1px solid rgba(255,255,255,0.1); height:100%;"><h3 style="color:#3b82f6;">规范文库</h3><p style="color:#64748b;">强检标准与办公模板安全共享。</p></div>', unsafe_allow_html=True)

elif "用户登录" in choice:
    st.markdown("<div style='max-width:420px; margin:0 auto; padding-top:8vh;'>", unsafe_allow_html=True)
    st.subheader("🔑 身份授权登录")
    with st.form("login_form"):
        u = st.text_input("工号 / 登录账号")
        p = st.text_input("访问密码", type="password")
        if st.form_submit_button("进入系统"):
            if u in users_db and users_db[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user_id = u
                st.session_state.user_name = users_db[u].get("name", "用户")
                st.session_state.user_perms = users_db[u].get("perms", [])
                st.rerun()
            else: st.error("登录失败")
    st.markdown("</div>", unsafe_allow_html=True)

elif "后台管理" in choice:
    t1, t2, t3 = st.tabs(["🖼️ 视觉配置", "👥 账号运维", "🔐 权限分配"])
    with t1:
        config['sidebar_title'] = st.text_input("左侧大标题 (支持长名称自动换行)", config['sidebar_title'])
        config['main_title'] = st.text_input("首页流光标题", config['main_title'])
        config['sidebar_tag'] = st.text_input("下方标识文字", config['sidebar_tag'])
        config['lock_message'] = st.text_area("锁定提示语", config['lock_message'])
        if st.button("更新配置"):
            save_json_data(CONFIG_PATH, config)
            st.rerun()
    with t2:
        user_list = [{"账号": k, "姓名": v["name"], "密码": v["password"]} for k, v in users_db.items()]
        st.table(pd.DataFrame(user_list))
        with st.form("add_user"):
            n_u = st.text_input("ID"); n_n = st.text_input("姓名"); n_p = st.text_input("密码")
            if st.form_submit_button("创建账号"):
                users_db[n_u] = {"password": n_p, "name": n_n, "perms": ["资产档案"], "role": "staff"}
                save_json_data(USERS_PATH, users_db); st.rerun()
    with t3:
        target = st.selectbox("选择目标员工", list(users_db.keys()))
        with st.form("perm_edit"):
            p_a = st.checkbox("📊 资产档案", value="资产档案" in users_db[target].get("perms", []))
            p_r = st.checkbox("🛠️ 维修管理", value="维修管理" in users_db[target].get("perms", []))
            p_l = st.checkbox("📂 工作文库", value="工作文库" in users_db[target].get("perms", []))
            p_c = st.checkbox("🔐 核心文件", value="核心文件" in users_db[target].get("perms", []))
            p_ad = st.checkbox("⚙️ 后台管理", value="后台管理" in users_db[target].get("perms", []))
            if st.form_submit_button("应用权限"):
                new_ps = []
                if p_a: new_ps.append("资产档案")
                if p_r: new_ps.append("维修管理")
                if p_l: new_ps.append("工作文库")
                if p_c: new_ps.append("核心文件")
                if p_ad: new_ps.append("后台管理")
                users_db[target]["perms"] = new_ps
                save_json_data(USERS_PATH, users_db); st.rerun()

elif "资产档案" in choice: show_asset()
elif "维修管理" in choice: show_repair()
elif "工作文库" in choice: show_library()
elif "个人中心" in choice:
    with st.form("pwd"):
        new_p = st.text_input("新密码", type="password")
        if st.form_submit_button("修改"):
            users_db[st.session_state.user_id]["password"] = new_p
            save_json_data(USERS_PATH, users_db); st.success("成功")
elif "注销退出" in choice:
    st.session_state.logged_in = False
    st.rerun()
