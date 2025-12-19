import streamlit as st
import os

def show_library():
    st.header("📚 医疗装备科工作文件库")
    st.info("您可以在此处查看并下载最新的办公文件、政策规范及表格模板。")

    # 定义存放文件的文件夹路径
    file_path = "work_files"

    # 如果文件夹不存在，先创建一个（防止报错）
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    # 获取文件夹内所有文件列表
    files = os.listdir(file_path)

    if not files:
        st.warning("目前文件库中暂无文件，请管理员上传至 work_files 文件夹。")
    else:
        # 按照后缀分类显示（可选）
        for file_name in files:
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # 根据文件后缀设置图标
            icon = "📄"
            if file_ext == ".pdf": icon = "📕"
            elif file_ext in [".doc", ".docx"]: icon = "📘"
            elif file_ext in [".xls", ".xlsx"]: icon = "📗"
            elif file_ext in [".ppt", ".pptx"]: icon = "📙"

            # 创建一行，左侧显示文件名，右侧显示下载按钮
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"{icon} {file_name}")
            
            with col2:
                # 读取文件并提供下载
                with open(os.path.join(file_path, file_name), "rb") as f:
                    st.download_button(
                        label="下载",
                        data=f,
                        file_name=file_name,
                        key=file_name # 每个按钮需要唯一的key
                    )
            st.divider() # 画一条分割线
