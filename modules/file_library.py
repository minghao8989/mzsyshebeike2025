import streamlit as st
import os

def show_library():
    st.markdown("### 📚 医疗装备科工作文件库")
    
    # 定义分类路径
    public_path = "work_files/public"
    core_path = "work_files/core"

    # 1. 所有人可见区域
    st.markdown("#### 🔓 公共办公文件")
    display_file_list(public_path, "public")

    st.markdown("---")

    # 2. 权限可见区域
    st.markdown("#### 🔐 核心管理文件")
    if st.session_state.get('logged_in'):
        st.success(f"✅ 已授权查看：{st.session_state.user_name}")
        display_file_list(core_path, "core")
    else:
        st.warning("⚠️ 此区域包含核心机密，请在左侧『用户登录』后查看。")

def display_file_list(folder_path, key_prefix):
    # 自动创建目录（如果不存在）
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
    
    # 获取目录下所有条目
    all_entries = os.listdir(folder_path)
    
    # 过滤出真正的文件，排除文件夹
    files = [f for f in all_entries if os.path.isfile(os.path.join(folder_path, f))]
    
    if not files:
        st.caption("📂 该文件夹暂无办公文件")
    else:
        for file_name in files:
            # 排除系统隐藏文件 (如 .DS_Store)
            if file_name.startswith('.'):
                continue
                
            file_ext = os.path.splitext(file_name)[1].lower()
            icon = "📕" if file_ext == ".pdf" else "📗" if "xls" in file_ext else "📘"
            
            # 使用容器包裹，确保在大屏小屏下对齐美观
            with st.container():
                c1, c2 = st.columns([4, 1])
                c1.write(f"{icon} {file_name}")
                
                try:
                    file_full_path = os.path.join(folder_path, file_name)
                    with open(file_full_path, "rb") as f:
                        c2.download_button(
                            label="📥 下载",
                            data=f,
                            file_name=file_name,
                            key=f"{key_prefix}_{file_name}",
                            use_container_width=True # 按钮宽度自适应
                        )
                except Exception as e:
                    c2.error("读取错误")
