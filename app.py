import streamlit as st
import json
import os
import time
import pandas as pd

# --- 核心路径 ---
CONFIG_PATH = "data/config.json"
USERS_PATH = "data/users.json"
EQUIPMENT_PATH = "data/equipment.csv"

# --- 1. 资产数据合并 (保留原表所有价值、价格数据) ---
def run_hospital_import_logic():
    # 您的 25 位标准目录
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
            try:
                df_temp = pd.read_csv(f, encoding='utf-8-sig')
                df_std = pd.DataFrame(columns=standard_columns)
                
                # 核心映射：保护价值、品牌、数量等字段
                for col in df_temp.columns:
                    if col == "设备名": df_std["设备名称"] = df_temp["设备名"]
                    elif col == "设备名.1": df_std["设备名"] = df_temp["设备名.1"]
                    elif "价格" in col: df_std["价格"] = df_temp[col]
                    elif "验收" in col: df_std["验收日期"] = df_temp[col]
                    elif col == "价值": df_std["价值"] = df_temp["价值"]
                    elif col == "数量": df_std["数量"] = df_temp["数量"]
                    elif col == "品牌": df_std["品牌"] = df_temp["品牌"]
                    elif col == "编号": df_std["老编号"] = df_temp["编号"]
                    elif col in standard_columns: df_std[col] = df_temp[col]
                
                all_data.append(df_std)
            except: continue
    
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        final_df['序号'] = range(1, len(final_df) + 1)
        os.makedirs("data", exist_ok=True)
        final_df.to_csv(EQUIPMENT_PATH, index=False, encoding='utf-8-sig')
        return len(final_df)
    return 0

# --- 2. 旗舰版高清晰视觉 ---
def apply_premium_style():
    st.markdown("""
        <style>
        .stApp { background-color: #111827; color: #FFFFFF; }
        [data-testid="stSidebar"] { background-color: #1F2937 !important; border-right: 1px solid #374151; }
        .sb-title { color: #38BDF8 !important; font-size: 1.6rem; font-weight: 800; white-space: pre-wrap; }
        div.stButton > button { background-color: #2563EB !important; color: #FFFFFF !important; border: 1px solid #60A5FA !important; font-weight:700; }
        .hero-banner { background: linear-gradient(135deg, #1E3A8A 0%, #111827 100%); border: 1px solid #3B82F6; border-radius: 15px; padding: 40px; margin-bottom: 20px; }
        .premium-title { font-weight: 850; color: #FFFFFF; font-size: 2.8rem; white-space: pre-wrap; }
        #MainMenu, footer, header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. 系统核心 ---
st.set_page_config(page_title="智慧医疗装备管理平台", layout="wide")
apply_premium_style()

# 动态加载模块防止报错
try:
    from modules.asset_page import show_asset
    from modules.repair_page import show_repair
    from modules.file_library import show_library
except:
    st.error("模块加载异常")

def load_j(p, d):
    if not os.path.exists(p): 
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f: json.dump(d, f, ensure_ascii=False)
        return d
    with open(p, 'r', encoding='utf-8') as f: return json.load(f)

cfg = load_j(CONFIG_PATH, {"sidebar_title": "梅州市\n第三人民医院\n装备科平台", "main_title": "医疗装备\n全生命周期管理平台"})
ALL_PERMS = ["资产档案", "维修管理", "工作文库", "后台管理"]
udb = load_j(USERS_PATH, {"admin": {"password": "123", "name": "设备科科长", "perms": ALL_PERMS}})

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

with st.sidebar:
    st.markdown(f'<div class="sb-title">🏥 {cfg["sidebar_title"]}</div>', unsafe_allow_html=True)
    st.markdown("---")
    menu = ["✨ 平台主页"]
    if st.session_state.logged_in:
        p = udb.get(st.session_state.user_id, {}).get("perms", [])
        if "资产档案" in p: menu.append("📊 资产档案")
        if "维修管理" in p: menu.append("🛠️ 维修管理")
        if "工作文库" in p: menu.append("📂 工作文库")
        menu.append("👤 个人中心")
        if "后台管理" in p or st.session_state.user_id == "admin": menu.append("⚙️ 后台管理")
        menu.append("🔓 注销退出")
    else: menu.append("🔑 用户登录")
    choice = st.sidebar.radio("N", menu, label_visibility="collapsed")

if "平台主页" in choice:
    st.markdown(f'<div class="hero-banner"><div class="premium-title">{cfg["main_title"]}</div></div>', unsafe_allow_html=True)
elif "用户登录" in choice:
    with st.form("L"):
        u = st.text_input("账号"); p = st.text_input("密码", type="password")
        if st.form_submit_button("登录"):
            if u in udb and udb[u]["password"] == p:
                st.session_state.logged_in = True; st.session_state.user_id = u
                st.session_state.user_name = udb[u]["name"]; st.rerun()
            else: st.error("登录失败")
elif "后台管理" in choice:
    t1, t2, t3, t4 = st.tabs(["🖼️ 视觉", "👥 账号", "🔐 权限", "🚀 导入"])
    with t2:
        st.table(pd.DataFrame([{"账号": k, "姓名": v["name"]} for k, v in udb.items()]))
        with st.form("add"):
            n_u, n_n, n_p = st.text_input("新账号"), st.text_input("姓名"), st.text_input("密码")
            if st.form_submit_button("创建"):
                udb[n_u] = {"password": n_p, "name": n_n, "perms": ["资产档案"]}
                save_json(USERS_PATH, udb); st.rerun()
    with t3:
        target = st.selectbox("选择员工", list(udb.keys()))
        with st.form("P"):
            u_d = udb[target]
            p_a = st.checkbox("资产档案", value="资产档案" in u_d["perms"])
            p_ad = st.checkbox("后台管理", value="后台管理" in u_d["perms"])
            if st.form_submit_button("更新"):
                udb[target]["perms"] = (["资产档案"] if p_a else []) + (["后台管理"] if p_ad else [])
                save_json(USERS_PATH, udb); st.rerun()
    with t4:
        if st.button("🚀 开始同步原表全部数据"):
            n = run_hospital_import_logic()
            if n > 0: st.success(f"成功合并 {n} 条资产")
elif "资产档案" in choice: show_asset()
elif "注销退出" in choice: st.session_state.logged_in = False; st.rerun()
