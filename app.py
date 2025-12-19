import streamlit as st
import json
import os
from modules.asset_page import show_asset
from modules.repair_page import show_repair

# --- 1. 配置文件读取函数 ---
CONFIG_FILE = "data/config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"sidebar_tag": "三甲医院信息化工具", "admin_user": "admin", "admin_password": "123"}
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config_data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

# --- 2. 界面初始化 ---
st.set_page_config(page_title="医疗装备部综合管理系统", layout="wide")
config = load_config()

# 初始化登录状态
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 3. 侧边栏设计 ---
st.sidebar.title("🏥 医疗装备部 v2025")

# 这里就是您要求的：后台可以随意编辑的文字内容
st.sidebar.button(config['sidebar_tag'], disabled=True)

# 导航菜单
if st.session_state.logged_in:
    menu = ["系统首页", "资产档案", "维修管理", "后台管理", "注销登录"]
else:
    menu = ["系统首页", "资产档案", "维修管理", "管理员登录"]

choice = st.sidebar.radio("请选择功能模块", menu)

# --- 4. 路由逻辑 ---

if choice == "系统首页":
    st.title("欢迎使用医疗装备管理系统")
    st.markdown(f"当前单位状态：**{config['sidebar_tag']}**")
    st.info("请通过左侧菜单访问各个功能模块。")

elif choice == "资产档案":
    show_asset()

elif choice == "维修管理":
    show_repair()

elif choice == "管理员登录":
    st.subheader("🔑 管理员身份验证")
    with st.form("login_form"):
        user = st.text_input("账号")
        pw = st.text_input("密码", type="password")
        if st.form_submit_button("登录"):
            if user == config['admin_user'] and pw == config['admin_password']:
                st.session_state.logged_in = True
                st.success("登录成功！已开启管理权限。")
                st.rerun()
            else:
                st.error("账号或密码错误")

elif choice == "后台管理":
    if not st.session_state.logged_in:
        st.warning("请先登录管理员账号")
    else:
        st.header("⚙️ 系统后台管理")
        st.subheader("1. 边栏文字设置")
        new_tag = st.text_input("编辑左侧蓝色按钮文字", config['sidebar_tag'])
        
        st.subheader("2. 账号密码设置")
        new_user = st.text_input("修改管理员账号", config['admin_user'])
        new_pw = st.text_input("修改管理员密码", config['admin_password'], type="password")
        
        if st.button("保存所有设置"):
            config['sidebar_tag'] = new_tag
            config['admin_user'] = new_user
            config['admin_password'] = new_pw
            save_config(config)
            st.success("设置已保存！系统将自动更新。")
            st.rerun()

elif choice == "注销登录":
    st.session_state.logged_in = False
    st.rerun()
