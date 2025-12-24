import streamlit as st
import json
import os
import time
import pandas as pd
import base64

# --- 1. 基础配置与模块导入 ---
st.set_page_config(page_title="智慧医疗装备管理平台", layout="wide")

try:
    from modules.asset_page import show_asset
    from modules.repair_page import show_repair
    from modules.file_library import show_library
except ImportError as e:
    st.error(f"核心模块导入失败: {e}")

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

# 将上传的图片转为 Base64 字符串
def img_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode()

# --- 资产数据合并导入逻辑 ---
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

# --- 2. 深度视觉样式优化 ---
def apply_premium_style():
    st.markdown("""
        <style>
        .stApp { background-color: #111827; color: #FFFFFF; }
        
        /* 侧边栏整体背景 */
        [data-testid="stSidebar"] { 
            background-color: #1E293B !important; 
            border-right: 1px solid #334155; 
        }

        /* Logo 容器样式 */
        .sidebar-logo-container {
            display: flex;
            justify-content: center;
            padding: 20px 0 10px 0;
        }
        .sidebar-logo {
            max-width: 180px;
            max-height: 90px;
            object-fit: contain;
            filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.3));
        }
        
        /* 左侧大标题 */
        .sidebar-main-title {
            color: #38BDF8 !important; 
            font-size: 1.25rem !important;
            font-weight: 850 !important;
            text-shadow: 0px 2px 4px #000000;
            text-align: center;
            padding: 0.5rem 0.4rem 1.2rem 0.4rem !important;
            line-height: 1.1 !important; 
            white-space: pre-line !important; 
        }

        /* 导航分组标题 */
        .nav-section-title {
            color: #94A3B8 !important;
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            margin: 15px 0 5px 15px !important;
            letter-spacing: 1px;
        }

        /* 强制清除英文标签及占位 */
        [data-testid="stSidebarNav"] + div [data-testid="stWidgetLabel"],
        [data-testid="stSidebar"] .stRadio > label,
        [data-testid="stSidebar"] div[data-baseweb="radio"] > div:first-child {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }
        
        /* 导航卡片美化 */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] { 
            gap: 8px; 
            padding: 0 10px; 
            margin-top: -15px !important; 
        }

        [data-testid="stSidebar"] .stRadio label {
            background-color: rgba(51, 65, 85, 0.4) !important;
            border-radius: 8px !important;
            padding: 10px 15px !important;
            border: 1px solid #334155 !important;
            transition: all 0.2s ease !important;
            cursor: pointer;
            display: block !important;
        }

        [data-testid="stSidebar"] .stRadio div[aria-checked="true"] label {
            background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        }

        [data-testid="stSidebar"] .stRadio p { 
            color: #F1F5F9 !important; 
            font-weight: 600 !important; 
            font-size: 0.95rem !important;
        }

        /* 首页 Banner 与 按钮 */
        .hero-banner { background: linear-gradient(135deg, #1E3A8A 0%, #111827 100%); border: 1px solid #3B82F6; border-radius: 12px; padding: 30px; }
        .premium-title { font-weight: 850; color: #FFFFFF; font-size: 2.8rem; white-space: pre-wrap; }
        div.stButton > button { background-color: #2563EB !important; color: #FFFFFF !important; font-weight: 700 !important; }
        
        #MainMenu, footer, header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

apply_premium_style()

# --- 3. 初始化配置 ---
ALL_PERMS = ["资产档案", "维修管理", "工作文库", "核心文件", "后台管理"]
config = load_json_data(CONFIG_PATH, {
    "sidebar_title": "梅州市\n第三人民医院\n装备科平台", 
    "main_title": "医疗装备\n全生命周期管理平台",
    "nav_label": "导航栏",
    "logo_base64": ""
})
users_db = load_json_data(USERS_PATH, {"admin": {"password": "123", "name": "设备科科长", "perms": ALL_PERMS}})

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- 4. 侧边栏渲染 ---
with st.sidebar:
    # 新增：显示 Logo 逻辑
    if config.get("logo_base64"):
        st.markdown(f'''
            <div class="sidebar-logo-container">
                <img src="data:image/png;base64,{config["logo_base64"]}" class="sidebar-logo">
            </div>
        ''', unsafe_allow_html=True)
        
    st.markdown(f'<div class="sidebar-main-title">{config["sidebar_title"]}</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown(f'<div class="nav-section-title">{config.get("nav_label", "导航栏")}</div>', unsafe_allow_html=True)
    
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
    
    choice = st.radio("sidebar_nav_internal", menu, label_visibility="collapsed")

# --- 5. 路由与业务逻辑 ---
if "平台主页" in choice:
    st.markdown(f'<div class="hero-banner"><div class="premium-title">{config["main_title"]}</div></div>', unsafe_allow_html=True)
    if not st.session_state.logged_in: st.info("🔐 核心业务已锁定。请登录后访问。")
    else: st.success(f"🚀 欢迎回来，{st.session_state.user_name}。")

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
        st.subheader("品牌视觉自定义")
        
        # 新增：Logo 上传功能
        new_logo = st.file_uploader("上传 Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
        if new_logo:
            if st.button("🆙 应用新 Logo"):
                config["logo_base64"] = img_to_base64(new_logo)
                save_json_data(CONFIG_PATH, config)
                st.success("Logo 已更新！")
                time.sleep(1)
                st.rerun()
        
        if config.get("logo_base64") and st.button("🗑️ 移除当前 Logo"):
            config["logo_base64"] = ""
            save_json_data(CONFIG_PATH, config)
            st.rerun()
            
        st.divider()
        config['sidebar_title'] = st.text_area("左侧大标题", config['sidebar_title'])
        config['nav_label'] = st.text_input("导航分组标题", config.get('nav_label', '导航栏'))
        config['main_title'] = st.text_area("首页流光标题", config['main_title'])
        if st.button("💾 保存文字配置"): save_json_data(CONFIG_PATH, config); st.rerun()
        
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
