import streamlit as st
import pandas as pd
import os

def show_asset():
    # --- 打印优化 CSS ---
    st.markdown("""
        <style>
        @media print {
            .stButton, .stDownloadButton, .stTextInput, header {display:none !important;}
            .main {padding: 0 !important;}
            .stDataFrame {width: 100% !important;}
        }
        </style>
    """, unsafe_allow_file_exists=True)

    st.header("🏥 医疗装备档案库")
    
    file_path = "data/equipment.csv"
    
    # 1. 检查文件是否存在
    if not os.path.exists(file_path):
        st.error(f"未找到数据文件：{file_path}")
        return

    # 2. 读取数据
    try:
        # 尝试读取，支持您自定义的长表头
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except Exception as e:
        st.error(f"读取 CSV 失败: {e}")
        return

    # 3. 顶部统计指标
    st.subheader("📊 全院资产概览")
    c1, c2, c3 = st.columns(3)
    c1.metric("管理设备总数", f"{len(df)} 台/套")
    
    status_col = "设备状态"
    if status_col in df.columns:
        active_count = len(df[df[status_col].isin(['正常', '在用', '运行中'])])
        c2.metric("正常运行设备", active_count)
    
    price_col = "购置金额"
    if price_col in df.columns:
        total_money = pd.to_numeric(df[price_col], errors='coerce').sum()
        c3.metric("资产总值", f"￥{total_money:,.2f}")

    st.divider()

    # 4. 数据查询与打印视图区
    st.subheader("🔍 档案明细 (支持 A4 打印预览)")
    
    # 搜索功能
    search = st.text_input("输入关键词搜索（打印前请清空搜索框以显示全部）：")
    if search:
        display_df = df[df.apply(lambda row: row.astype(str).str.contains(search).any(), axis=1)]
    else:
        display_df = df

    # --- 设置适合 A4 比例的表格 ---
    # 根据数据量动态调整高度，或者固定 800px 以模拟 A4 长度
    table_height = min(len(display_df) * 35 + 100, 800) 

    edited_df = st.data_editor(
        display_df, 
        num_rows="dynamic", 
        use_container_width=True, # 铺满宽度
        height=table_height,       # 增加高度，使其在视觉上更长
        column_config={
            "科室名称": st.column_config.TextColumn("科室名称", width="medium"),
            "设备名称": st.column_config.TextColumn("设备名称", width="large"),
            "购置金额": st.column_config.NumberColumn("金额", format="￥%.2f"),
            "购买日期": st.column_config.DateColumn("购买日期"),
            "设备状态": st.column_config.SelectboxColumn(
                "状态",
                options=["正常", "维修中", "待报废", "封存", "计量中"],
                required=True
            )
        }
    )
    
    # 5. 操作区
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
    if col_btn1.button("💾 保存数据"):
        edited_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        st.success("✅ 档案已保存！")
        st.rerun()
    
    with col_btn2:
        # 提供一个 CSV 下载按钮，方便在 Excel 中按照精确 A4 格式排版打印
        csv_data = edited_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 导出 Excel", data=csv_data, file_name="医疗装备档案导出.csv")

    st.caption("💡 提示：如需直接打印网页，请按 Ctrl+P。建议在打印设置中选择『横向』并勾选『背景图形』。")
