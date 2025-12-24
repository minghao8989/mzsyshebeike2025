import streamlit as st
import json
import os
import time
import pandas as pd

# 尝试导入业务模块
try:
    from modules.asset_page import show_asset
    from modules.repair_page import show_repair
    from modules.file_library import show_library
except ImportError as e:
    st.error(f"核心模块导入失败: {e}")

# --- 1. 数据管理核心逻辑 ---
CONFIG_PATH = "data/config.json"
USERS_PATH = "data/users.json"
EQUIPMENT_PATH = "data/equipment.csv"

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

# --- 🚀 资产数据合并导入逻辑 ---
def run_hospital_import_logic():
    standard_columns = [
        "序号", "科室", "设备名称", "资产国标代码", "国标代码+地点+流水", "设备SN码", 
        "老编号", "价值", "设备名", "数量", "品牌", "型号", "生产编号", 
        "出厂日期", "价格", "验收日期", "设备状态", "械字号", "使用年限", 
        "调拨情况", "可报废年限", "厂家电话", "工作站厂家", "工作站厂家电话", "备注"
    ]
    files = [f"三院资产表_已填充国标码.xlsx - Sheet{i}.csv" for i in range(1, 5)]
    all_data = []
    for f in files:
        if os.path.exists(f):
            df_temp = pd.read_csv(f, encoding='utf-8-sig')
            df_std = pd.DataFrame(columns=standard_columns)
            for col in df_temp.columns:
                if col == "设备名": df_std["设备名称"] = df_temp["设备名"]
                elif col == "设备名.1": df_std["设备名"] = df_temp["设备名.1"]
                elif col in standard_columns: df_std[col] = df_temp[col]
                elif col == "编号": df_std["老编号"] = df_temp["编号"]
            all_data.append(df_std)
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df['序号'] = range(1, len(final_df) + 1)
        os.makedirs("data", exist_ok=True)
        final_df.to_csv(EQUIPMENT_PATH, index=False, encoding='utf-8-sig')
        return len(final_df)
    return 0

# --- 2. 仿图2高清晰视觉样式 ---
def apply_premium_style():
    st.markdown("""
        <style>
        /* 全局背景：深灰蓝，文字：纯白 */
        .stApp { background-color: #111827; color: #FFFFFF; }
        
        /* 侧边栏样式 */
        [data-testid="stSidebar"] { background-color: #1F2937 !important; border-right: 1px solid #374151; }
        .sidebar-main-title {
            color: #38BDF8 !important; font-size: 1.6rem !important; font-weight: 800 !important;
            text-shadow: 0px 2px 4px #000000;
        }
        [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
            color: #F0F9FF !important; font-weight: 600 !important;
        }

        /* 首页 Banner */
        .hero-banner {
            background: linear-gradient(135deg, #1E3A8A 0%, #111827 100%);
            border: 1px solid #3B82F6; border-radius: 15px; padding: 40px; margin-bottom: 20px;
        }
        .premium-title {
            font-weight: 850; color: #FFFFFF; font-size: 3rem; white-space: pre-wrap;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
        }

        /* 按钮：强制可见，深蓝底白字 */
        div.stButton > button {
            background-color: #2563EB !important; color: #FFFFFF !important;
            border: 1px solid #60A5FA !important; border-radius: 6px !important;
            padding: 10px 30px !important; font-weight: 700 !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        }
        div.stButton > button:hover { background-color: #3B82F6 !important; border-color: #FFFFFF !important; }

        /* 表格强化 */
        [data-testid="stTable"] { background-color: #1F2937 !important; color: #FFFFFF !important; }
        
        #MainMenu, footer, header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. 初始化 ---
st.set_page_config(page_title="智慧医疗装备管理平台", layout="wide")
apply_premium_style()

ALL_PERMS = ["资产档案", "维修管理", "工作文库", "核心文件", "后台管理"]
config = load_json_data(CONFIG_PATH, {"sidebar_title": "梅州市\n第三人民医院\n装备科平台", "main_title": "医疗装备\n全生命周期管理平台"})
users_db = load_json_data(USERS_PATH, {"admin": {"password": "123", "name": "设备科科长", "perms": ALL_PERMS}})

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- 4. 侧边栏导航 (全功能恢复) ---
with st.sidebar:
    st.markdown(f'<div class="sidebar-main-title">🏥 {config["sidebar_title"]}</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    menu = ["✨ 平台主页"]
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

# --- 5. 路由逻辑 ---
if "平台主页" in choice:
    st.markdown(f'<div class="hero-banner"><div class="premium-title">{config["main_title"]}</div></div>', unsafe_allow_html=True)
    if not st.session_state.logged_in: st.info("🔐 核心业务已锁定。请登录后访问。")
    else: st.success("🚀 欢迎回来。")

elif "用户登录" in choice:
    st.markdown("<div style='max-width:400px; margin:0 auto; padding-top:5vh;'>", unsafe_allow_html=True)
    st.subheader("🔑 身份授权登录")
    with st.form("login"):
        u = st.text_input("账号"); p = st.text_input("密码", type="password")
        if st.form_submit_button("验证登录"):
            if u in users_db and users_db[u]["password"] == p:
                st.session_state.logged_in = True; st.session_state.user_id = u
                st.session_state.user_name = users_db[u].get("name", "用户")
                st.session_state.user_perms = users_db[u].get("perms", [])
                st.rerun()
            else: st.error("登录失败")
    st.markdown("</div>", unsafe_allow_html=True)

elif "后台管理" in choice:
    t1, t2, t3, t4 = st.tabs(["🖼️ 视觉配置", "👥 账号运维", "🔐 权限分配", "🚀 资产导入"])
    with t1:
        config['sidebar_title'] = st.text_area("左侧大标题", config['sidebar_title'])
        config['main_title'] = st.text_area("首页流光标题", config['main_title'])
        if st.button("💾 保存配置"): save_json_data(CONFIG_PATH, config); st.rerun()
    with t2:
        st.subheader("账号运维")
        user_df = pd.DataFrame([{"账号": k, "姓名": v["name"]} for k, v in users_db.items()])
        st.table(user_df)
        with st.form("add_user"):
            n_u = st.text_input("新账号"); n_n = st.text_input("姓名"); n_p = st.text_input("密码")
            if st.form_submit_button("确认创建"):
                users_db[n_u] = {"password": n_p, "name": n_n, "perms": ["资产档案"]}
                save_json_data(USERS_PATH, users_db); st.rerun()
    with t3:
        st.subheader("权限分配")
        target = st.selectbox("选择员工", list(users_db.keys()))
        with st.form("perms"):
            u_d = users_db[target]
            p_a = st.checkbox("📊 资产档案", value="资产档案" in u_d.get("perms", []))
            p_r = st.checkbox("🛠️ 维修管理", value="维修管理" in u_d.get("perms", []))
            p_l = st.checkbox("📂 工作文库", value="工作文库" in u_d.get("perms", []))
            p_ad = st.checkbox("⚙️ 后台管理", value="后台管理" in u_d.get("perms", []))
            if st.form_submit_button("更新权限"):
                new_ps = []
                if p_a: new_ps.append("资产档案")
                if p_r: new_ps.append("维修管理")
                if p_l: new_ps.append("工作文库")
                if p_ad: new_ps.append("后台管理")
                users_db[target]["perms"] = new_ps; save_json_data(USERS_PATH, users_db); st.rerun()
    with t4:
        if st.button("🚀 合并导入资产"):
            count = run_hospital_import_logic()
            if count > 0: st.success(f"成功合并 {count} 条记录")

elif "资产档案" in choice: show_asset()
elif "维修管理" in choice: show_repair()
elif "工作文库" in choice: show_library()
elif "个人中心" in choice:
    with st.form("pwd"):
        np = st.text_input("新密码", type="password")
        if st.form_submit_button("修改"):
            users_db[st.session_state.user_id]["password"] = np
            save_json_data(USERS_PATH, users_db); st.success("成功")
elif "注销退出" in choice: st.session_state.logged_in = False; st.rerun()
