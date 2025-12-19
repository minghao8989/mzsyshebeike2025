import streamlit as st
import os

def show_library():
    st.header("📚 医疗装备科工作文件库")
    
    # 1. 渲染公共文件区 (所有人可见)
    st.subheader("🔓 公共办公文件")
    display_files("work_files/public")

    st.markdown("---")

    # 2. 渲染核心文件区 (仅登录后的员工或管理员可见)
    st.subheader("🔐 核心管理文件")
    if st.session_state.get('logged_in'):
        st.success(f"已授权：{st.session_state.user_name} ({'管理员' if st.session_state.user_role == 'admin' else '员工'})")
        display_files("work_files/core")
    else:
        st.warning("⚠️ 此区域包含核心机密文件，请在左侧『用户登录』后查看。")

def display_files(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        st.write("文件夹为空")
        return

    files = os.listdir(folder_path)
    if not files:
        st.write("暂无文件")
    else:
        for file_name in files:
            file_ext = os.path.splitext(file_name)[1].lower()
            icon = "📕" if file_ext == ".pdf" else "📗" if "xls" in file_ext else "📘"
            
            col1, col2 = st.columns([4, 1])
            col1.write(f"{icon} {file_name}")
            with open(os.path.join(folder_path, file_name), "rb") as f:
                col2.download_button("下载", f, file_name=file_name, key=f"{folder_path}_{file_name}")
