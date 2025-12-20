import streamlit as st
import json
import os
import time

# 尝试导入业务模块
try:
    from modules.asset_page import show_asset
    from modules.repair_page import show_repair
    from modules.file_library import show_library
except ImportError as e:
    st.error(f"核心模块导入失败，请检查 modules 文件夹。错误信息: {e}")

# --- 1. 核心数据持久化函数 ---
CONFIG_PATH = "data/config.json"
USERS_PATH = "data/users.json"

def load_json_data(path, default_val):
    """通用的数据加载函数"""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default_val, f, ensure_ascii=False, indent=4)
        return default_val
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return default_val

def save_json_data(path, data):
    """通用的数据保存函数"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 2. 高端视觉样式定制 (CSS) ---
def apply_premium_style():
    st.markdown("""
        <style>
        /* 全局高端医疗深蓝配色 */
        .stApp {
            background-color: #050a14;
            color: #f8fafc;
        }
        
        /* 首页大图遮罩区域 (Hero Section) - HID 风格 */
        .hero-banner {
            background: linear-gradient(rgba(5, 10, 20, 0.75), rgba(5, 10, 20, 0.95)), 
                        url('https://images.unsplash.com/photo-1516549655169-df83a0774514?q=80&w=2070');
            background-size: cover;
            background-position: center;
            padding: 90px 50px;
            border-radius: 24px;
            margin-bottom: 40px;
            border: 1px solid rgba(59, 130, 246, 0.2);
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }
        
        /* 渐变流光大标题 */
        .premium-title {
            font-size: 3.8rem;
            font-weight: 850;
            background: linear-gradient(90deg, #3b82f6, #60a5fa, #ffffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
            letter-spacing: -1.5px;
        }

        .premium-subtitle {
            font-size: 1.3rem;
            color: #94a3b8;
            max-width: 750px;
            line-height: 1.6;
            font-weight: 300;
        }

        /* 磨砂玻璃功能卡片 */
        .info-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(12px);
            border-radius: 18px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        }
        .info-card:hover {
            background: rgba(59, 130, 246, 0.08);
            border-color: #3b82f6;
            transform: translateY(-10px);
            box-shadow: 0 15px 30px rgba(59, 130, 246, 0.15);
        }
        
        /* 侧边栏与表单美化 */
        [data-testid="stSidebar"] {
            background-color: #0a0f1d !important;
            border-right: 1px solid rgba(255,255,255,0.05);
        }
        .stButton>button {
            border-radius: 10px;
            background: linear-gradient(90deg, #3b82f6, #2563eb) !important;
            color: white !important;
            border: none !important;
            font-weight: 600;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
            transform: scale(1.02);
        }

        /* 隐藏Streamlit原生组件 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {background: rgba(0,0,0,0) !important;}
        </style>
    """, unsafe_allow_html=True)

# --- 3. 系统初始化逻辑 ---
st.set_page_config(page_title="智慧医疗装备管理平台", layout="wide")
apply_premium_style()

# 加载配置
config = load_json_data(CONFIG_PATH, {
    "sidebar_title": "装备科平台",
    "sidebar_tag": "三甲医院信息化工具",
    "main_title": "医疗装备全生命周期管理平台",
    "lock_message": "核心业务模块已锁定。请登录以获取实时资产数据与文件调阅权限。"
})

# 加载账号
users_db = load_json_data(USERS_PATH, {
    "admin": {"password": "123", "role": "admin", "name": "科主任"}
})

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 4. 侧边栏导航定制 ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#3b82f6; margin-bottom:0;'>🏥 {config['sidebar_title']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#64748b; font-size:0.85rem;'>{config['sidebar_tag']}</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # 动态权限菜单
    if st.session_state.logged_in:
        menu = ["✨ 平台主页", "📊 资产档案", "🛠️ 维修管理", "📂 工作文库"]
        if st.session_state.user_role == "admin":
            menu.append("⚙️ 后台管理")
        menu.append("🔓 注销注销")
    else:
        menu = ["✨ 平台主页", "🔑 身份登录"]
    
    choice = st.sidebar.radio("Navigation", menu, label_visibility="collapsed")
    
    st.sidebar.markdown("<br>"*10, unsafe_allow_html=True)
    if st.session_state.logged_in:
        st.sidebar.info(f"当前用户: {st.session_state.user_name}")

# --- 5. 核心路由与逻辑处理 ---

if "平台主页" in choice:
    # HID 风格 Hero Section
    st.markdown(f"""
        <div class="hero-banner">
            <div class="premium-title">{config['main_title']}</div>
            <div class="premium-subtitle">
                借助数字化技术重塑医疗资产效能，实现从购置论证、在运行监测到报废鉴定的
                全过程质量受控与数据溯源。
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        st.markdown(f"""
            <div style='background: rgba(59, 189, 248, 0.05); padding: 20px; border-radius: 12px; border: 1px dashed #3b82f6; color: #93c5fd;'>
                🔐 {config['lock_message']}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.success(f"🚀 系统就绪。欢迎回来，{st.session_state.user_name}。")

    # 底部核心模块概览
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""<div class="info-card"><h3>智能资产台账</h3><p style="color:#94a3b8;">全院资产全景透视，实时价值评估与台账在线维护。</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="info-card"><h3>精益维保体系</h3><p style="color:#94a3b8;">一键响应临床需求，维修进度透明化，设备开机率实时监控。</p></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="info-card"><h3>合规规范文库</h3><p style="color:#94a3b8;">强制检测标准与科室办公模板，支持多级权限安全调阅。</p></div>""", unsafe_allow_html=True)

elif "身份登录" in choice:
    st.markdown("<div style='max-width:450px; margin:0 auto; padding-top:80px;'>", unsafe_allow_html=True)
    st.subheader("🔐 系统访问授权")
    with st.form("login_form"):
        u_name = st.text_input("工号 / 登录账号")
        u_pass = st.text_input("访问密码", type="password")
        if st.form_submit_button("验证并进入平台"):
            if u_name in users_db and users_db[u_name]["password"] == u_pass:
                st.session_state.logged_in = True
                st.session_state.user_role = users_db[u_name]["role"]
                st.session_state.user_name = users_db[u_name]["name"]
                st.rerun()
            else:
                st.error("授权验证失败，请核对凭证。")
    st.markdown("</div>", unsafe_allow_html=True)

elif "后台管理" in choice:
    st.header("⚙️ 平台高级设置")
    with st.expander("📝 视觉主题与标题自定义", expanded=True):
        col_set1, col_set2 = st.columns(2)
        config['sidebar_title'] = col_set1.text_input("左侧边栏大标题", config['sidebar_title'])
        config['sidebar_tag'] = col_set2.text_input("机构标识标签内容", config['sidebar_tag'])
        config['main_title'] = st.text_input("首页 Slogan 动态流光标题", config['main_title'])
        config['lock_message'] = st.text_area("未登录锁定状态提示语", config['lock_message'])

    if st.button("💾 应用并同步全局配置"):
        save_json_data(CONFIG_PATH, config)
        st.success("全局配置更新成功，界面已即时生效！")
        time.sleep(1)
        st.rerun()

elif "资产档案" in choice:
    show_asset()

elif "维修管理" in choice:
    show_repair()

elif "工作文库" in choice:
    show_library()

elif "注销注销" in choice:
    st.session_state.logged_in = False
    st.rerun()
