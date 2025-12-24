import streamlit as st
import json
import os
import time
import pandas as pd

# --- 模块导入保护 ---
try:
    from modules.asset_page import show_asset
    from modules.repair_page import show_repair
    from modules.file_library import show_library
except Exception as e:
    st.error(f"⚠️ 核心模块加载失败，请检查 modules 文件夹。错误: {e}")

# --- 1. 数据管理核心逻辑 ---
CONFIG_PATH, USERS_PATH, EQUIPMENT_PATH = "data/config.json", "data/users.json", "data/equipment.csv"

def load_json(path, default):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f: json.dump(default, f, ensure_ascii=False, indent=4)
        return default
    with open(path, 'r', encoding='utf-8') as f:
        try: return json.load(f)
        except: return default

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

# --- 2. 资产数据一键合并逻辑 ---
def run_import():
    cols = ["序号", "科室", "设备名称", "资产国标代码", "国标代码+地点+流水", "设备SN码", "老编号", "价值", "设备名", "数量", "品牌", "型号", "生产编号", "出厂日期", "价格", "验收日期", "设备状态", "械字号", "使用年限", "调拨情况", "可报废年限", "厂家电话", "工作站厂家", "工作站厂家电话", "备注"]
    all_df = []
    for i in range(1, 5):
        f = f"三院资产表_已填充国标码.xlsx - Sheet{i}.csv"
        if os.path.exists(f):
            tmp = pd.read_csv(f, encoding='utf-8-sig')
            std = pd.DataFrame(columns=cols)
            for c in tmp.columns:
                if c == "设备名": std["设备名称"] = tmp["设备名"]
                elif c == "设备名.1": std["设备名"] = tmp["设备名.1"]
                elif c in cols: std[c] = tmp[c]
                elif c == "编号": std["老编号"] = tmp["编号"]
            all_df.append(std)
    if all_df:
        df = pd.concat(all_df, ignore_index=True)
        df['序号'] = range(1, len(df) + 1)
        df.to_csv(EQUIPMENT_PATH, index=False, encoding='utf-8-sig')
        return len(df)
    return 0

# --- 3. 视觉风格定制 (仿图2，极高清晰度) ---
def apply_style():
    st.markdown("""
        <style>
        /* 背景与基础文字 */
        .stApp { background-color: #0F172A; color: #FFFFFF; }
        
        /* 侧边栏样式 */
        [data-testid="stSidebar"] { background-color: #1E293B !important; border-right: 1px solid #334155; }
        .sb-title { color: #38BDF8 !important; font-size: 1.6rem; font-weight: 800; line-height: 1.2; white-space: pre-wrap; }
        [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { color: #FFFFFF !important; font-weight: 600; }
        
        /* 按钮：深蓝底亮蓝框，文字纯白 */
        div.stButton > button {
            background-color: #2563EB !important; color: #FFFFFF !important;
            border: 2px solid #60A5FA !important; border-radius: 8px; font-weight: 700;
        }
        div.stButton > button:hover { background-color: #3B82F6 !important; border-color: #FFFFFF !important; }
        
        /* 首页 Banner */
        .hero { background: linear-gradient(135deg, #1E40AF 0%, #0F172A 100%); border: 1px solid #3B82F6; border-radius: 15px; padding: 40px; margin-bottom: 25px; }
        .hero-h1 { color: #FFFFFF; font-size: 3rem; font-weight: 850; white-space: pre-wrap; }
        
        #MainMenu, footer, header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

# --- 4. 逻辑控制 ---
st.set_page_config(page_title="智慧医疗装备管理平台", layout="wide")
apply_style()

ALL = ["资产档案", "维修管理", "工作文库", "核心文件", "后台管理"]
cfg = load_json(CONFIG_PATH, {"sidebar_title": "梅州市\n第三人民医院\n装备科平台", "main_title": "医疗装备\n全生命周期管理平台"})
udb = load_json(USERS_PATH, {"admin": {"password": "123", "name": "科长", "perms": ALL}})

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

with st.sidebar:
    st.markdown(f'<div class="sb-title">🏥 {cfg["sidebar_title"]}</div>', unsafe_allow_html=True)
    st.markdown("---")
    menu = ["✨ 平台主页"]
    if st.session_state.logged_in:
        perms = ALL if st.session_state.user_id == "admin" else st.session_state.get('user_perms', [])
        if "资产档案" in perms: menu.append("📊 资产档案")
        if "维修管理" in perms: menu.append("🛠️ 维修管理")
        if "工作文库" in perms: menu.append("📂 工作文库")
        menu.append("👤 个人中心")
        if "后台管理" in perms or st.session_state.user_id == "admin": menu.append("⚙️ 后台管理")
        menu.append("🔓 注销退出")
    else: menu.append("🔑 用户登录")
    
    choice = st.sidebar.radio("N", menu, label_visibility="collapsed")
    if st.session_state.logged_in:
        st.sidebar.info(f"欢迎：{st.session_state.user_name}")

if "平台主页" in choice:
    st.markdown(f'<div class="hero"><div class="hero-h1">{cfg["main_title"]}</div></div>', unsafe_allow_html=True)
    if not st.session_state.logged_in: st.info("🔐 核心业务已锁定，请先登录。")

elif "用户登录" in choice:
    with st.form("L"):
        u = st.text_input("账号"); p = st.text_input("密码", type="password")
        if st.form_submit_button("验证登录"):
            if u in udb and udb[u]["password"] == p:
                st.session_state.logged_in = True; st.session_state.user_id = u
                st.session_state.user_name = udb[u]["name"]; st.session_state.user_perms = udb[u].get("perms", [])
                st.rerun()
            else: st.error("登录失败")

elif "后台管理" in choice:
    t1, t2, t3, t4 = st.tabs(["🖼️ 视觉", "👥 账号", "🔐 权限", "🚀 导入"])
    with t1:
        cfg['sidebar_title'] = st.text_area("侧边栏标题", cfg['sidebar_title'])
        cfg['main_title'] = st.text_area("主标题", cfg['main_title'])
        if st.button("保存视觉"): save_json(CONFIG_PATH, cfg); st.rerun()
    with t2:
        st.write("### 账号列表")
        st.table(pd.DataFrame([{"账号": k, "姓名": v["name"]} for k, v in udb.items()]))
        with st.form("A"):
            n_u, n_n, n_p = st.text_input("新账号"), st.text_input("姓名"), st.text_input("密码")
            if st.form_submit_button("创建"): 
                udb[n_u] = {"password": n_p, "name": n_n, "perms": ["资产档案"]}; save_json(USERS_PATH, udb); st.rerun()
    with t3:
        target = st.selectbox("选择员工", list(udb.keys()))
        with st.form("P"):
            p_a = st.checkbox("资产档案", value="资产档案" in udb[target]["perms"])
            p_ad = st.checkbox("后台管理", value="后台管理" in udb[target]["perms"])
            if st.form_submit_button("应用权限"):
                udb[target]["perms"] = (["资产档案"] if p_a else []) + (["后台管理"] if p_ad else [])
                save_json(USERS_PATH, udb); st.rerun()
    with t4:
        if st.button("🚀 一键合并资产"):
            num = run_import()
            if num > 0: st.success(f"已成功导入 {num} 条记录！"); time.sleep(1); st.rerun()

elif "资产档案" in choice: show_asset()
elif "注销退出" in choice: st.session_state.logged_in = False; st.rerun()
