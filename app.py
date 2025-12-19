import streamlit as st
import json
import os

# 导入您之前创建的各个功能模块
# 请确保您的 modules 文件夹下有这三个文件
try:
    from modules.asset_page import show_asset
    from modules.repair_page import show_repair
    from modules.file_library import show_library
except ImportError as e:
    st.error(f"模块导入失败，请检查 modules 文件夹下的文件名是否正确。错误信息: {e}")

# --- 1. 配置文件管理逻辑 ---
CONFIG_PATH = "data/config.json"

def load_config():
    """从本地 JSON 加载配置，如果不存在则创建默认配置"""
    default_config = {
        "sidebar_tag": "三甲医院信息化工具",
        "admin_user": "admin",
        "admin_password": "123"
    }
    if not os.path.exists(CONFIG_PATH):
        # 确保 data 目录存在
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
        return default_config
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config_data):
    """保存配置到本地 JSON"""
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)

# --- 2. 页面初始化 ---
st.set_page_config(page_title="医疗装备部综合管理系统", layout="wide")
config = load_config()

# 初始化登录状态（存储在浏览器会话中）
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 3. 侧边栏设计 ---
st.sidebar.title("🏥 医疗装备部 v2025")

# 动态显示管理员定义的侧边栏文字
st.sidebar.button(config.get('sidebar_tag', '三甲医院信息化工具'), disabled=True)

# 侧边栏菜单路由
# 根据登录状态动态调整菜单选项
if st.session_state.logged_in:
    menu = ["系统首页", "资产档案", "维修管理", "工作文件库", "后台管理", "注销登录"]
else:
    menu = ["系统首页", "资产档案", "维修管理", "工作文件库", "管理员登录"]

choice = st.sidebar.radio("请选择功能模块", menu)

st.sidebar.markdown("---")
st.sidebar.caption("技术支持：医疗装备科信息化小组")

# --- 4. 路由逻辑（点击菜单跳转） ---

if choice == "系统首页":
    st.title("欢迎使用医疗装备管理系统")
    st.markdown(f"当前单位标识：**:blue[{config.get('sidebar_tag')}]**")
    st.info("本系统旨在优化科室流程，提升医疗设备全生命周期管理效率。")
    
    # 首页快捷看板（示例）
    col1, col2 = st.columns(2)
    with col1:
        st.help("提示：初次使用请在『工作文件库』下载操作手册。")
    with col2:
        if not st.session_state.logged_in:
            st.warning("提醒：部分敏感数据需管理员登录后查看。")

elif choice == "资产档案":
    show_asset()

elif choice == "维修管理":
    show_repair()

elif choice == "工作文件库":
    show_library()

elif choice == "管理员登录":
    st.subheader("🔑 管理员身份验证")
    with st.form("login_form"):
        user_input = st.text_input("账号")
        pw_input = st.text_input("密码", type="password")
        if st.form_submit_button("立即登录"):
            if user_input == config.get('admin_user') and pw_input == config.get('admin_password'):
                st.session_state.logged_in = True
                st.success("验证通过！已开启管理权限。")
                st.rerun()
            else:
                st.error("账号或密码不正确，请联系科室负责人。")

elif choice == "后台管理":
    if not st.session_state.logged_in:
        st.warning("⚠️ 权限不足，请先登录。")
    else:
        st.header("⚙️ 系统后端配置")
        
        with st.expander("1️⃣ 修改侧边栏标签内容", expanded=True):
            new_tag = st.text_input("当前文字:", config.get('sidebar_tag'))
            
        with st.expander("2️⃣ 修改管理员安全凭证", expanded=False):
            new_user = st.text_input("管理员账号:", config.get('admin_user'))
            new_pw = st.text_input("管理员密码:", config.get('admin_password'), type="password")
        
        if st.button("💾 保存全局配置"):
            config['sidebar_tag'] = new_tag
            config['admin_user'] = new_user
            config['admin_password'] = new_pw
            save_config(config)
            st.success("配置已成功写入本地数据库！")
            st.balloons()
            st.rerun()

elif choice == "注销登录":
    st.session_state.logged_in = False
    st.info("您已安全退出。")
    st.rerun()
