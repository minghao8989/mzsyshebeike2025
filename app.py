import streamlit as st
import json
import os

# 尝试导入功能模块
try:
    from modules.asset_page import show_asset
    from modules.repair_page import show_repair
    from modules.file_library import show_library
except ImportError as e:
    st.error(f"模块导入失败，请检查 modules 文件夹。错误: {e}")

# --- 配置与用户数据加载 ---
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
users_db = load_json(USERS_PATH, {"admin": {"password": "123", "role": "admin", "name": "管理员"}})

# --- 初始化会话状态 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_name = None

# --- 侧边栏设计 ---
st.sidebar.title("🏥 医疗装备部 v2025")
st.sidebar.button(config.get('sidebar_tag'), disabled=True)

# 【核心修改】：根据登录状态动态生成菜单
if st.session_state.logged_in:
    # 登录后展示：核心业务模块 + 管理/退出
    menu = ["系统首页", "资产档案", "维修管理", "工作文件库"]
    if st.session_state.user_role == "admin":
        menu.append("后台管理")
    menu.append("注销登录")
else:
    # 未登录展示：仅首页和登录入口
    menu = ["系统首页", "用户登录"]

choice = st.sidebar.radio("功能导航", menu)
st.sidebar.markdown("---")
if st.session_state.logged_in:
    st.sidebar.success(f"当前用户：{st.session_state.user_name}")
else:
    st.sidebar.warning("当前状态：未登录")

# --- 路由逻辑 ---
if choice == "系统首页":
    st.title("欢迎使用医疗装备管理系统")
    if not st.session_state.logged_in:
        st.info("👋 您好！本系统包含核心医疗装备数据，请先完成登录以访问『资产档案』、『维修管理』和『文件库』。")
    else:
        st.success(f"您好，{st.session_state.user_name}！您可以开始处理业务了。")

elif choice == "资产档案":
    show_asset()

elif choice == "维修管理":
    show_repair()

elif choice == "工作文件库":
    show_library()

elif choice == "用户登录":
    st.subheader("👤 内部用户验证")
    with st.form("login_form"):
        username = st.text_input("账号")
        password = st.text_input("密码", type="password")
        if st.form_submit_button("立即登录"):
            if username in users_db and users_db[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.user_role = users_db[username]["role"]
                st.session_state.user_name = users_db[username]["name"]
                st.rerun()
            else:
                st.error("账号或密码错误。")

elif choice == "后台管理":
    st.header("⚙️ 系统后台配置")
    new_tag = st.text_input("修改侧边栏文字标签:", config.get('sidebar_tag'))
    if st.button("保存设置"):
        config['sidebar_tag'] = new_tag
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        st.success("设置已更新！")
        st.rerun()

elif choice == "注销登录":
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.rerun()
