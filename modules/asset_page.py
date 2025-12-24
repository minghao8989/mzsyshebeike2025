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
        /* 5/7/10/13年配色 */
        div[data-testid="metric-container"]:nth-child(1) [data-testid="stMetricValue"] { color: #38BDF8; }
        div[data-testid="metric-container"]:nth-child(2) [data-testid="stMetricValue"] { color: #FACC15; }
        div[data-testid="metric-container"]:nth-child(3) [data-testid="stMetricValue"] { color: #FB923C; }
        div[data-testid="metric-container"]:nth-child(4) [data-testid="stMetricValue"] { color: #F87171; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📊 资产档案 (保留原表全字段)")
    path = "data/equipment.csv"
    
    if not os.path.exists(path):
        st.error("❌ 数据未初始化。请去『后台管理』->『🚀 导入』点击同步。")
        return

    # 安全读取数据
    df = pd.read_csv(path, encoding='utf-8-sig')
    
    # --- 核心：安全计算年限 (不导致白屏) ---
    curr_yr = 2025
    def calc_age(row):
        try:
            val = str(row['出厂日期'])
            year = int(val[:4]) # 截取前4位，兼容 2020.12.18 等格式
            return curr_yr - year
        except: return 0

    df['age'] = df.apply(calc_age, axis=1)

    # 1. 看板 (5/7/10/13年)
    st.subheader("⚠️ 关键年限统计 (基准2025年)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("5年以上", len(df[df['age'] >= 5]))
    c2.metric("7年以上", len(df[df['age'] >= 7]))
    c3.metric("10年以上", len(df[df['age'] >= 10]))
    c4.metric("13年以上", len(df[df['age'] >= 13]))

    st.divider()

    # 2. 全院总表 (支持粘贴)
    st.subheader("⌨️ 数据维护 (价值/价格/数量已保留)")
    df['序号'] = range(1, len(df) + 1)
    
    # 移除计算辅助列再编辑
    edit_df = df.drop(columns=['age'], errors='ignore')
    
    edited = st.data_editor(
        edit_df,
        num_rows="dynamic", use_container_width=True, height=450,
        column_config={
            "序号": st.column_config.NumberColumn(disabled=True),
            "价值": st.column_config.NumberColumn(format="￥%.2f"),
            "价格": st.column_config.NumberColumn(format="￥%.2f")
        },
        key="main_editor"
    )

    if st.button("💾 保存档案所有修改"):
        edited['序号'] = range(1, len(edited) + 1)
        edited.to_csv(path, index=False, encoding='utf-8-sig')
        st.success("✅ 数据已安全保存。"); time.sleep(1); st.rerun()

    # 3. 树状视图
    st.subheader("🌳 科室资产树状视图")
    depts = sorted(edited['科室'].dropna().unique().tolist())
    for d in depts:
        d_data = edited[edited['科室'] == d]
        with st.expander(f"📁 {d} ({len(d_data)} 条)"):
            st.dataframe(d_data, use_container_width=True)
