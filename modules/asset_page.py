import streamlit as st
import pandas as pd
import os
import time

def show_asset():
    st.markdown("""
        <style>
        /* 强制表格显示完整文字，消除朦胧感 */
        div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
            color: #FFFFFF !important; font-size: 0.95rem !important;
            white-space: normal !important; word-break: break-all !important;
        }
        /* 指标颜色：蓝、黄、橙、红 */
        [data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 800; }
        div[data-testid="metric-container"]:nth-child(1) [data-testid="stMetricValue"] { color: #38BDF8; }
        div[data-testid="metric-container"]:nth-child(2) [data-testid="stMetricValue"] { color: #FACC15; }
        div[data-testid="metric-container"]:nth-child(3) [data-testid="stMetricValue"] { color: #FB923C; }
        div[data-testid="metric-container"]:nth-child(4) [data-testid="stMetricValue"] { color: #F87171; }
        /* 表格线条 */
        [data-testid="stTable"] { border: 1px solid #475569 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📊 医疗装备资产档案与年限统计")
    path = "data/equipment.csv"
    
    if not os.path.exists(path):
        st.error("❌ 数据文件丢失！请前往『后台管理』->『🚀 导入』点击一键合并。")
        return

    df = pd.read_csv(path, encoding='utf-8-sig')
    
    # 年限计算逻辑
    curr_yr = 2025
    if '出厂日期' in df.columns:
        df['年限'] = curr_yr - pd.to_datetime(df['出厂日期'], errors='coerce').dt.year
    else: df['年限'] = 0

    # 1. 年限分布看板
    st.subheader("⚠️ 关键年限设备统计 (基准2025年)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("5年以上", len(df[df['年限'] >= 5]))
    c2.metric("7年以上", len(df[df['年限'] >= 7]))
    c3.metric("10年以上", len(df[df['年限'] >= 10]))
    c4.metric("13年以上", len(df[df['年限'] >= 13]))

    st.divider()

    # 2. 数据编辑 (支持粘贴)
    st.subheader("⌨️ 数据维护 (支持 Excel 粘贴)")
    df['序号'] = range(1, len(df) + 1)
    edited = st.data_editor(
        df.drop(columns=['年限'], errors='ignore'),
        num_rows="dynamic", use_container_width=True, height=450,
        column_config={"价值": st.column_config.NumberColumn(format="￥%.2f")},
        key="asset_edit"
    )

    if st.button("💾 保存档案"):
        edited['序号'] = range(1, len(edited) + 1)
        edited.to_csv(path, index=False, encoding='utf-8-sig')
        st.success("✅ 保存成功！"); time.sleep(1); st.rerun()

    # 3. 树状视图
    st.subheader("🌳 科室资产树状视图")
    depts = sorted(edited['科室'].dropna().unique().tolist())
    for d in depts:
        with st.expander(f"📁 {d}"):
            st.dataframe(edited[edited['科室'] == d], use_container_width=True)
