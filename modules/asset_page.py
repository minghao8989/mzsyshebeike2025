import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

def show_asset():
    # 1. 注入 CSS：强化视觉对比度，确保文字极其清晰，解决“朦胧感”
    st.markdown("""
        <style>
        /* 全局背景与文字：深灰蓝底 + 高亮白字 */
        .stApp { background-color: #0f172a; color: #f8fafc; }
        
        /* 强化表格内容：纯白文字，自动换行 */
        div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
            color: #ffffff !important; 
            font-size: 0.9rem !important;
            white-space: normal !important; 
            word-break: break-all !important;
            line-height: 1.4 !important;
        }
        
        /* 指标卡片 (Metric) 特殊配色，按年限风险分层 */
        [data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 800 !important; }
        div[data-testid="metric-container"]:nth-child(1) [data-testid="stMetricValue"] { color: #38bdf8; } /* 蓝 */
        div[data-testid="metric-container"]:nth-child(2) [data-testid="stMetricValue"] { color: #fbbf24; } /* 黄 */
        div[data-testid="metric-container"]:nth-child(3) [data-testid="stMetricValue"] { color: #f59e0b; } /* 橙 */
        div[data-testid="metric-container"]:nth-child(4) [data-testid="stMetricValue"] { color: #ef4444; } /* 红 */
        
        /* 表格网格强化 */
        [data-testid="stTable"] td, [data-testid="stTable"] th { border: 1px solid #334155 !important; }
        
        .stExpander summary { color: #f1f5f9 !important; font-weight: 700 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📊 医疗装备档案与全生命周期统计")
    file_path = "data/equipment.csv"
    
    if not os.path.exists(file_path):
        st.warning("📂 资产库目前为空，请在后台执行合并导入。")
        return

    # 读取数据
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    
    # 核心：计算设备年限
    # 假设当前年份为 2025
    current_year = 2025
    if '出厂日期' in df.columns:
        # 将出厂日期转为日期格式，并提取年份，无法转换的设为 NaN
        df['year_temp'] = pd.to_datetime(df['出厂日期'], errors='coerce').dt.year
        df['age'] = current_year - df['year_temp']
    else:
        df['age'] = 0

    # --- 第一部分：资产年限分布统计 (新增需求) ---
    st.subheader("⚠️ 资产老旧程度实时监控 (当前2025年基准)")
    c1, c2, c3, c4 = st.columns(4)
    
    # 计算各年限段设备
    age_5 = len(df[df['age'] >= 5])
    age_7 = len(df[df['age'] >= 7])
    age_10 = len(df[df['age'] >= 10])
    age_13 = len(df[df['age'] >= 13])

    c1.metric("5年以上设备", f"{age_5} 台", help="出厂已满5年")
    c2.metric("7年以上设备", f"{age_7} 台", help="出厂已满7年")
    c3.metric("10年以上设备", f"{age_10} 台", help="出厂已满10年")
    c4.metric("13年以上设备", f"{age_13} 台", help="出厂已满13年")

    st.divider()

    # --- 第二部分：基础统计 ---
    st.subheader("📈 基础概览")
    b1, b2, b3 = st.columns(3)
    b1.metric("已录入资产总数", f"{len(df)} 条")
    val = pd.to_numeric(df['价值'], errors='coerce').sum()
    b2.metric("固定资产总值", f"￥{val:,.2f}")
    b3.metric("在管科室数", df['科室'].dropna().nunique())

    st.divider()

    # --- 第三部分：全院总表编辑 (支持粘贴) ---
    st.subheader("⌨️ 数据维护总表")
    st.info("💡 **温馨提示**：您可以在此直接粘贴 Excel 数据。系统会自动为您计算上方年限统计。")
    
    df['序号'] = range(1, len(df) + 1)
    edited_df = st.data_editor(
        df.drop(columns=['year_temp', 'age'], errors='ignore'), # 隐藏辅助计算列
        num_rows="dynamic",
        use_container_width=True,
        height=450,
        column_config={
            "序号": st.column_config.NumberColumn(width="small", disabled=True),
            "出厂日期": st.column_config.DateColumn("出厂日期", format="YYYY-MM-DD"),
            "价值": st.column_config.NumberColumn(format="￥%.2f"),
            "老编号": st.column_config.TextColumn(width="large")
        },
        key="main_asset_editor"
    )

    if st.button("💾 保存档案所有修改"):
        edited_df['序号'] = range(1, len(edited_df) + 1)
        edited_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        st.success("✅ 保存成功！年限统计已刷新。")
        time.sleep(1); st.rerun()

    st.divider()

    # --- 第四部分：树状视图 ---
    st.subheader("🌳 科室资产树状视图")
    depts = sorted(edited_df['科室'].dropna().unique().tolist())
    for d in depts:
        d_data = edited_df[edited_df['科室'] == d]
        with st.expander(f"📁 {d} (设备清单: {len(d_data)} 条)"):
            st.dataframe(d_data, use_container_width=True)
            if st.button(f"➕ 在 {d} 增行", key=f"add_{d}"):
                nr = pd.DataFrame([{"科室": d, "设备状态": "正常"}])
                sdf = pd.concat([edited_df, nr], ignore_index=True)
                sdf['序号'] = range(1, len(sdf) + 1)
                sdf.to_csv(file_path, index=False, encoding='utf-8-sig')
                st.rerun()
