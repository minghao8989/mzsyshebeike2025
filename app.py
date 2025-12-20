import streamlit as st
import json
import os
import time

# 导入业务模块
try:
    from modules.asset_page import show_asset
    from modules.repair_page import show_repair
    from modules.file_library import show_library
except ImportError as e:
    st.error(f"核心模块导入失败，请检查 modules 文件夹。错误信息: {e}")

# --- 1. 数据管理函数 ---
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

# --- 2. 深度适配样式定制 (CSS) ---
def apply_responsive_style():
    st.markdown("""
        <style>
        /* 全局深色底色 */
        .stApp {
            background-color: #050a14;
            color: #f8fafc;
        }
        
        /* 响应式 Hero Section */
        .hero-banner {
            background: linear-gradient(rgba(5, 10, 20, 0.75), rgba(5, 10, 20, 0.95)), 
                        url('https://images.unsplash.com/photo-1516549655169-df83a0774514?q=80&w=2070');
            background-size: cover;
            background-position: center;
            border-radius: 20px;
            border: 1px solid rgba(59, 130, 246, 0.2);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            
            /* 弹性内边距：在窄屏下自动缩小左右间距 */
            padding: 40px clamp(15px, 4vw, 50px);
            margin-bottom: 2rem;
            width: 100%;
            overflow: hidden; /* 防止文字溢出容器 */
        }
        
        /* 核心修复：强制单行且自适应字号 */
        .premium-title {
            font-weight: 850;
            background: linear-gradient(90deg, #3b82f6, #60a5fa, #ffffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            
            /* 强制不换行 */
            white-space: nowrap; 
            
            /* 字号随屏幕宽度自动呼吸缩放 */
            /* 1.5rem 是手机端最小值，3.5vw 是比例值，4rem 是大屏最大值 */
            font-size: clamp(1.5rem, 4vw, 4rem); 
            
            letter-spacing: -1.5px;
            line-height: 1.2;
            margin-bottom: 0.8rem;
            display: block;
        }

        .premium-subtitle {
            color: #94a3b8;
            font-weight: 300;
            line-height: 1.4;
            font-size: clamp(0.85rem, 1.2vw, 1.1rem);
            max-width: 90%;
            /* 开启多行显示，但限制宽度 */
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        /* 磨砂卡片适配 */
        .info-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1.2rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            height: 100%;
            transition: all 0.3s ease;
        }
        
        .info-card h3 {
            font-size: clamp(1rem, 1.5vw, 1.3rem);
            color: #3b82f6;
            margin-bottom: 0.5rem;
            white-space: nowrap;
        }
        
        .info-card p {
            font-size: clamp(0.75rem, 1vw, 0.9rem);
            color: #64748b;
            line-height: 1.4;
        }

        /* 侧边栏宽度优化 */
        [data-testid="stSidebar"] {
            background-color: #0a0f1d !important;
            min-width: 260px !important;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {background: rgba(0,0,0,0) !important;}
        </style>
    """, unsafe_allow_html=True)

# --- 3. 初始化 ---
st.set_page_config(page_title="智慧医疗装备管理平台", layout="wide")
apply_responsive_style()

config = load_json_data(CONFIG_PATH, {
    "sidebar_title": "装备科平台",
    "sidebar_tag": "三甲医院信息化工具",
    "main_title": "医疗装备全生命周期管理平台",
    "lock_message": "核心业务已锁定。请登录后访问资产与维保数据。"
})

users_db = load_json_data(USERS_PATH, {"admin": {"password": "123", "role": "admin", "name": "科主任"}})

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 4. 侧边栏 ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#3b82f6; font-size:1.6rem;'>🏥 {config['sidebar_title']}</h2>", unsafe_allow_html=True)
    st.caption(f"{config['sidebar_tag']}")
    st.markdown("---")
    
    if st.session_state.logged_in:
        menu = ["✨ 平台主页", "📊 资产档案", "🛠️ 维修管理", "📂 工作文库"]
        if st.session_state.user_role == "admin": menu.append("⚙️ 后台管理")
        menu.append("🔓 注销退出")
    else:
        menu = ["✨ 平台主页", "🔑 用户登录"]
    
    choice = st.sidebar.radio("Navigation", menu, label_visibility="collapsed")

# --- 5. 主逻辑 ---

if "平台主页" in choice:
    # 响应式 Hero Section
    st.markdown(f"""
        <div class="hero-banner">
            <div class="premium-title">{config['main_title']}</div>
            <div class="premium-subtitle">
                基于 IoT 与大数据技术构建的智慧医院装备管理方案。
                实现资产从采购论证、在运行监测到报废鉴定的全流程闭环管理。
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        st.markdown(f"""
            <div style='background: rgba(59, 189, 248, 0.05); padding: 15px; border-radius: 10px; border: 1px dashed #3b82f6; color: #93c5fd; font-size: 0.9rem;'>
                🔐 {config['lock_message']}
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown('<div class="info-card"><h3>智能资产台账</h3><p>全生命周期追溯，实时掌握全院设备分布与价值评估。</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="info-card"><h3>精益维保体系</h3><p>临床一键扫码报修，维保全流程节点透明化可追踪。</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="info-card"><h3>合规规范文库</h3><p>强检标准与办公模板，权限分级下的安全共享。</p></div>', unsafe_allow_html=True)

elif "用户登录" in choice:
    st.markdown("<div style='max-width:400px; margin:0 auto; padding-top:5vh;'>", unsafe_allow_html=True)
    st.subheader("🔑 身份授权登录")
    with st.form("login_form"):
        u_name = st.text_input("工号 / 登录账号")
        u_pass = st.text_input("访问密码", type="password")
        if st.form_submit_button("验证登录"):
            if u_name in users_db and users_db[u_name]["password"] == u_pass:
                st.session_state.logged_in = True
                st.session_state.user_role = users_db[u_name]["role"]
                st.session_state.user_name = users_db[u_name]["name"]
                st.rerun()
            else:
                st.error("验证失败")
    st.markdown("</div>", unsafe_allow_html=True)

elif "后台管理" in choice:
    st.header("⚙️ 平台全局配置")
    with st.expander("📝 视觉与文案自定义", expanded=True):
        config['sidebar_title'] = st.text_input("左侧标题", config['sidebar_title'])
        config['main_title'] = st.text_input("首页流光标题 (建议12字内以保美观)", config['main_title'])
        config['lock_message'] = st.text_area("锁定提示语", config['lock_message'])
        config['sidebar_tag'] = st.text_input("底部标签内容", config['sidebar_tag'])

    if st.button("💾 保存配置"):
        save_json_data(CONFIG_PATH, config)
        st.success("配置已更新！")
        time.sleep(1)
        st.rerun()

elif "资产档案" in choice: show_asset()
elif "维修管理" in choice: show_repair()
elif "工作文库" in choice: show_library()
elif "注销退出" in choice:
    st.session_state.logged_in = False
    st.rerun()
