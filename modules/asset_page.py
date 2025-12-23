import streamlit as st
import pandas as pd
import os
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

def show_asset():
    # 注入高级 CSS 以匹配您的旗舰视觉风格
    st.markdown("""
        <style>
        .ag-theme-alpine { --ag-background-color: #050a14; --ag-foreground-color: #f8fafc; }
        .stMetricValue { color: #3b82f6 !important; font-size: 1.8rem !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📊 医疗装备综合资产档案")
    file_path = "data/equipment.csv"
    
    if not os.path.exists(file_path):
        st.warning("📂 档案库目前为空。")
        return

    # 读取包含 25 个标准字段的数据
    df = pd.read_csv(file_path, encoding='utf-8-sig')

    # 看板统计
    st.subheader("🏥 资产运行态势")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("已录入资产", f"{len(df)} 条")
    val = pd.to_numeric(df['价值'], errors='coerce').sum()
    c2.metric("总资产价值", f"￥{val:,.2f}")
    c3.metric("覆盖科室数", f"{df['科室'].dropna().nunique()} 个")
    c4.metric("待完善条目", df.isnull().any(axis=1).sum())

    st.divider()

    # --- 核心：Ag-Grid 高级配置 (支持复制粘贴) ---
    st.subheader("🔍 智能档案编辑器")
    st.info("💡 操作指南：您可以直接从 Excel 复制数据，在下方表格选中单元格后按 Ctrl+V 粘贴。")

    gb = GridOptionsBuilder.from_dataframe(df)
    
    # 启用 Excel 风格的功能
    gb.configure_default_column(
        editable=True,           # 允许编辑
        groupable=True, 
        value=True, 
        enableRowGroup=True, 
        aggFunc='sum', 
        filterable=True, 
        sortable=True,
        resizable=True
    )
    
    # 针对您的 25 位目录配置特定列
    gb.configure_column("序号", width=80, pinned='left')
    gb.configure_column("科室", width=150, pinned='left')
    gb.configure_column("设备名称", width=200)
    
    # 启用单元格选择和多选，这是实现粘贴的基础
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    
    # 核心参数：允许在组件内进行文本选择和粘贴
    gridOptions = gb.build()
    gridOptions['enableCellTextSelection'] = True
    gridOptions['ensureDomOrder'] = True

    # 渲染表格
    response = AgGrid(
        df,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=False,
        theme='alpine', # 匹配深色背景
        height=600,
        reload_data=False
    )

    # 获取修改后的数据
    updated_df = response['data']

    # 操作按钮
    col_save, col_down, _ = st.columns([1, 1, 4])
    if col_save.button("💾 保存档案修改"):
        updated_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        st.success("✅ 资产档案修改已保存。")
        st.rerun()
    
    with col_down:
        csv_bin = updated_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 导出报表", data=csv_bin, file_name="资产档案导出.csv", mime="text/csv")
