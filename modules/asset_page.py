import streamlit as st
import pandas as pd
import os
import time

def show_asset():
    st.markdown("""
        <style>
        div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
            color: #FFFFFF !important; font-size: 0.95rem !important;
            white-space: normal !important; word-break: break-all !important;
        }
        [data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 800 !important; }
        div[data-testid="metric-container"]:nth-child(1) [data-testid="stMetricValue"] { color: #38bdf8; }
        div[data-testid="metric-container"]:nth-child(2) [data-testid="stMetricValue"] { color: #fbbf24; }
        div[data-testid="metric-container"]:nth-child(3) [data-testid="stMetricValue"] { color: #f59e0b; }
        div[data-testid="metric-container"]:nth-child(4) [data-testid="stMetricValue"] { color: #ef4444; }
        [data-testid="stTable"] { background-color: #111827 !important; border: 1px solid #374151 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📊 医疗装备综合资产档案")
    file_path = "data/equipment.csv"
    
    if not os.path.exists(file_path):
        st.warning("📂 数据不见了？请去『后台管理』->『资产导入』点击『一键合并资产』即可恢复。")
        return

    df = pd.read_csv(file_path, encoding='utf-8-sig')
    
    # 核心：计算年限
    current_year = 2025
    if '出厂日期' in df.columns:
        df['age'] = current_year - pd.to_datetime(df['出厂日期'], errors='coerce').dt.year
    else: df['age'] = 0

    # 1. 年限统计看板
    st.subheader("⚠️ 资产老旧程度统计 (基准2025年)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("5年以上", len(df[df['age'] >= 5]))
    c2.metric("7年以上", len(df[df['age'] >= 7]))
    c3.metric("10年以上", len(df[df['age'] >= 10]))
    c4.metric("13年以上", len(df[df['age'] >= 13]))

    st.divider()

    # 2. 全院总表 (支持粘贴)
    st.subheader("⌨️ 数据维护总表 (支持 Excel 粘贴)")
    df['序号'] = range(1, len(df) + 1)
    edited_df = st.data_editor(
        df.drop(columns=['age'], errors='ignore'),
        num_rows="dynamic", use_container_width=True, height=450,
        column_config={"序号": st.column_config.NumberColumn(disabled=True), "价值": st.column_config.NumberColumn(format="￥%.2f")},
        key="main_editor"
    )

    if st.button("💾 保存所有修改"):
        edited_df['序号'] = range(1, len(edited_df) + 1)
        edited_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        st.success("✅ 保存成功！"); time.sleep(1); st.rerun()

    st.divider()

    # 3. 树状视图
    st.subheader("🌳 科室资产树状视图")
    depts = sorted(edited_df['科室'].dropna().unique().tolist())
    for d in depts:
        with st.expander(f"📁 {d}"):
            st.dataframe(edited_df[edited_df['科室'] == d], use_container_width=True)
