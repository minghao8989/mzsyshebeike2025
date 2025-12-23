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

# --- 🚀 自动导入合并逻辑 (收纳在后台使用) ---
def run_auto_import_logic():
    standard_columns = [
        "序号", "科室", "设备名称", "资产国标代码", "国标代码+地点+流水", "设备SN码", 
        "老编号", "价值", "设备名", "数量", "品牌", "型号", "生产编号", 
        "出厂日期", "价格", "验收日期", "设备状态", "械字号", "使用年限", 
        "调拨情况", "可报废年限", "厂家电话", "工作站厂家", "工作站厂家电话", "备注"
    ]
    files = [
        "三院资产表_已填充国标码.xlsx - Sheet1.csv",
        "三院资产表_已填充国标码.xlsx - Sheet2.csv",
        "三院资产表_已填充国标码.xlsx - Sheet3.csv",
        "三院资产表_已填充国标码.xlsx - Sheet4.csv"
    ]
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

# --- 2. 旗舰版 CSS 样式 ---
def apply_premium_style():
    st.markdown("""
        <style>
        .stApp { background-color: #050a14; color: #f8fafc; }
        .hero-banner {
            background: linear-gradient(rgba(5, 10, 20, 0.75), rgba(5, 10, 20, 0.95)), 
                        url('https://images.unsplash.com/photo-1516549655169-df83a0774514?q=80&w=2070');
            background-size: cover; background-position: center;
            border-radius: 20px; border: 1px solid rgba(59, 130, 246, 0.2);
            padding: 5% 4%; margin-bottom: 2rem; width: 100%; overflow: hidden;
        }
        .premium-title {
            font-weight: 850; background: linear-gradient(90deg, #3b82f6, #60a5fa, #ffffff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            white-space: pre-wrap; font-size: clamp(1.5rem, 4vw, 3.5rem); 
            letter-spacing: -1.5px; line-height: 1.2; display: block;
        }
        .sidebar-main-title {
            color: #3b82f6 !important; font-size: 1.6rem !important; font-weight: 800 !important;
            line-height: 1.3 !important; white-space: pre-wrap !important; 
            text-shadow: 0px 2px 4px rgba(0,0,0,0.5);
        }
        div.stButton > button {
            background-color: #1e40af !important; color: #ffffff !important;
            border: 1px solid #3b82f6 !important; border-radius: 8px !important;
            padding: 0.6rem 2rem !important; font-weight: 700 !important;
        }
        [data-testid="stSidebar"] { background-color: #0a0f1d !important; border-right: 1px solid rgba(255,255,255,0.05); }
        [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { color: #FFFFFF !important; font-weight: 500; }
        [data-testid="stSidebar"] [aria-selected="true"] { color: #3b82f6 !important; font-weight: 700; }
        #MainMenu, footer, header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. 系统初始化 ---
st.set_page_config(page_title="智慧医疗装备管理平台", layout="wide")
apply_premium_style()

ALL_PERMS = ["资产档案", "维修管理", "工作文库", "核心文件", "后台管理"]

config = load_json_data(CONFIG_PATH, {
    "sidebar_title": "梅州市\n第三人民医院\n装备科平台",
    "sidebar_tag": "设备科信息化工具",
    "main_title": "医疗装备\n全生命周期管理平台",
    "lock_message": "核心业务已锁定。请登录后访问业务数据。"
})

users_db = load_json_data(USERS_PATH, {
    "admin": {"password": "123", "role": "admin", "name": "设备科科长", "perms": ALL_PERMS}
})

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 4. 侧边栏导航 (全功能恢复) ---
with st.sidebar:
    st.markdown(f'<div class="sidebar-main-title">🏥 {config["sidebar_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#60a5fa; font-size:0.85rem; margin-top:0;'>{config['sidebar_tag']}</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu = ["✨ 平台主页"]
    if st.session_state.logged_in:
        # 管理员强制拥有所有权限
        if st.session_state.user_id == "admin": st.session_state.user_perms = ALL_PERMS
        
        user_perms = st.session_state.get('user_perms', [])
        
        # 按照您的习惯恢复所有菜单项
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
        st.sidebar.markdown(f"<div style='margin-top:20px; padding:12px; background:rgba(59,130,246,0.15); border-radius:10px; border:1px solid #3b82f6; color:#FFFFFF;'>欢迎：{st.session_state.user_name}</div>", unsafe_allow_html=True)

# --- 5. 路由逻辑 ---
if "平台主页" in choice:
    st.markdown(f'<div class="hero-banner"><div class="premium-title">{config["main_title"]}</div><div style="color:#94a3b8; font-size:clamp(0.9rem, 1.3vw, 1.2rem);">智能监测 · 精准统计 · 流程溯源</div></div>', unsafe_allow_html=True)
    if not st.session_state.logged_in:
        st.info(f"🔐 {config['lock_message']}")
    else:
        st.success(f"🚀 系统已就绪。")

elif "用户登录" in choice:
    st.markdown("<div style='max-width:420px; margin: 0 auto; padding-top:8vh;'>", unsafe_allow_html=True)
    st.subheader("🔑 身份授权登录")
    with st.form("login_form"):
        u = st.text_input("工号 / 登录账号")
        p = st.text_input("访问密码", type="password")
        if st.form_submit_button("验证登录"):
            if u in users_db and users_db[u]["password"] == p:
                st.session_state.logged_in = True
                st.session_state.user_id = u
                st.session_state.user_name = users_db[u].get("name", "用户")
                st.session_state.user_perms = users_db[u].get("perms", [])
                st.rerun()
            else: st.error("账号或密码错误")
    st.markdown("</div>", unsafe_allow_html=True)

elif "后台管理" in choice:
    t1, t2, t3, t4 = st.tabs(["🖼️ 视觉配置", "👥 账号运维", "🔐 权限分配", "🚀 数据一键合并"])
    with t1:
        config['sidebar_title'] = st.text_area("左侧大标题 (支持回车换行)", config['sidebar_title'], height=100)
        config['main_title'] = st.text_area("首页流光大标题 (支持回车换行)", config['main_title'], height=100)
        config['sidebar_tag'] = st.text_input("下方标识文字", config['sidebar_tag'])
        if st.button("💾 保存视觉配置"):
            save_json_data(CONFIG_PATH, config)
            st.success("配置更新成功！")
            st.rerun()
    with t2:
        user_list = [{"账号": k, "姓名": v["name"], "密码": v["password"]} for k, v in users_db.items()]
        st.table(pd.DataFrame(user_list))
        with st.form("add_user"):
            n_u = st.text_input("新账号ID"); n_n = st.text_input("姓名"); n_p = st.text_input("初始密码")
            if st.form_submit_button("确认创建"):
                users_db[n_u] = {"password": n_p, "name": n_n, "perms": ["资产档案"], "role": "staff"}
                save_json_data(USERS_PATH, users_db); st.rerun()
    with t3:
        target = st.selectbox("选择目标员工", list(users_db.keys()))
        with st.form("perm_edit"):
            u_d = users_db[target]
            p_a = st.checkbox("📊 资产档案", value="资产档案" in u_d.get("perms", []))
            p_r = st.checkbox("🛠️ 维修管理", value="维修管理" in u_d.get("perms", []))
            p_l = st.checkbox("📂 工作文库", value="工作文库" in u_d.get("perms", []))
            p_c = st.checkbox("🔐 核心文件", value="核心文件" in u_d.get("perms", []))
            p_ad = st.checkbox("⚙️ 后台管理", value="后台管理" in u_d.get("perms", []))
            if st.form_submit_button("应用权限"):
                new_ps = []
                if p_a: new_ps.append("资产档案")
                if p_r: new_ps.append("维修管理")
                if p_l: new_ps.append("工作文库")
                if p_c: new_ps.append("核心文件")
                if p_ad: new_ps.append("后台管理")
                users_db[target]["perms"] = new_ps
                save_json_data(USERS_PATH, users_db); st.rerun()
    with t4:
        st.subheader("资产分表一键导入")
        if st.button("🚀 开始合并 4 个分表并更新数据库"):
            count = run_auto_import_logic()
            if count > 0: st.success(f"✅ 成功合并 {count} 条记录！")
            else: st.error("❌ 未找到分表，请检查文件名。")

elif "资产档案" in choice: show_asset()
elif "维修管理" in choice: show_repair()
elif "工作文库" in choice: show_library()
elif "个人中心" in choice:
    with st.form("pwd"):
        new_p = st.text_input("新密码", type="password")
        if st.form_submit_button("确认修改密码"):
            users_db[st.session_state.user_id]["password"] = new_p
            save_json_data(USERS_PATH, users_db); st.success("修改成功")
elif "注销退出" in choice:
    st.session_state.logged_in = False
    st.rerun()
