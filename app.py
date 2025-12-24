import streamlit as st
import pandas as pd
import os
import time

def show_asset():
    st.markdown("""
        <style>
        div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
            color: #FFFFFF !important; font-size: 0.9rem !important;
            white-space: normal !important; word-break: break-all !important;
        }
        [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 800; }
        div[data-testid="metric-container"]:nth-child(1) [data-testid="stMetricValue"] { color: #38BDF8; }
        div[data-testid="metric-container"]:nth-child(2) [data-testid="stMetricValue"] { color: #FACC15; }
        div[data-testid="metric-container"]:nth-child(3) [data-testid="stMetricValue"] { color: #FB923C; }
        div[data-testid="metric-container"]:nth-child(4) [data-testid="stMetricValue"] { color: #F87171; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📊 资产档案 (保留全字段+树状增删)")
    path = "data/equipment.csv"
    
    if not os.path.exists(path):
        st.error("❌ 数据未初始化，请前往『后台管理』->『🚀 导入』执行数据同步。")
        return

    df = pd.read_csv(path, encoding='utf-8-sig')
    curr_yr = 2025
    if '出厂日期' in df.columns:
        df['age'] = curr_yr - pd.to_datetime(df['出厂日期'], errors='coerce').dt.year
    else: df['age'] = 0

    # 1. 看板 (5/7/10/13年统计)
    st.subheader("⚠️ 关键年限统计 (基准2025年)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("5年以上", len(df[df['age'] >= 5]))
    c2.metric("7年以上", len(df[df['age'] >= 7]))
    c3.metric("10年以上", len(df[df['age'] >= 10]))
    c4.metric("13年以上", len(df[df['age'] >= 13]))

    st.divider()

    # 2. 全院总表 (保留原功能，修复显示不全)
    st.subheader("⌨️ 全院总表编辑 (支持粘贴)")
    df['序号'] = range(1, len(df) + 1)
    edited = st.data_editor(
        df.drop(columns=['age'], errors='ignore'),
        num_rows="dynamic", use_container_width=True, height=450,
        column_config={"序号": st.column_config.NumberColumn(disabled=True), "价值": st.column_config.NumberColumn(format="￥%.2f")},
        key="main_editor"
    )

    if st.button("💾 保存档案所有修改"):
        edited['序号'] = range(1, len(edited) + 1)
        edited.to_csv(path, index=False, encoding='utf-8-sig')
        st.success("✅ 档案库已同步。"); time.sleep(1); st.rerun()

    # 3. 树状视图 (保留科室分类功能)
    st.subheader("🌳 科室资产树状视图")
    depts = sorted(edited['科室'].dropna().unique().tolist())
    for d in depts:
        d_data = edited[edited['科室'] == d]
        with st.expander(f"📁 {d} ({len(d_data)} 条)"):
            st.dataframe(d_data, use_container_width=True)
            if st.button(f"➕ 在 {d} 快速增行", key=f"add_{d}"):
                nr = pd.DataFrame([{"科室": d, "设备状态": "正常"}])
                sdf = pd.concat([edited, nr], ignore_index=True)
                sdf['序号'] = range(1, len(sdf) + 1)
                sdf.to_csv(path, index=False, encoding='utf-8-sig')
                st.rerun()
