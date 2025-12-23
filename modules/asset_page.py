import streamlit as st
import pandas as pd
import os
import time

def show_asset():
    st.markdown("""
        <style>
        div[data-testid="stDataFrame"] > div { overflow-x: auto !important; }
        .stDataFrame div[data-testid="stTable"] { font-size: 0.8rem; }
        [data-testid="stMetricValue"] { color: #3b82f6 !important; font-size: 1.8rem !important; }
        /* 强化边框方便粘贴定位 */
        [data-testid="stTable"] td { border: 1px solid #262730 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📊 医疗装备综合资产档案")
    file_path = "data/equipment.csv"
    
    if not os.path.exists(file_path):
        st.warning("📂 档案库目前为空，请先在后台执行导入。")
        return

    df = pd.read_csv(file_path, encoding='utf-8-sig')

    # 看板统计
    st.subheader("🏥 资产概览")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("已录入资产", f"{len(df)} 条")
    val = pd.to_numeric(df['价值'], errors='coerce').sum()
    c2.metric("总资产价值", f"￥{val:,.2f}")
    c3.metric("覆盖科室", f"{df['科室'].dropna().nunique()} 个")
    c4.metric("空缺条目", df.isnull().sum().sum())

    st.divider()

    # 原生支持粘贴的编辑器
    st.info("💡 **批量粘贴技巧**：在 Excel 中选中区域 Ctrl+C，在下表点击起始单元格，按 **Ctrl+V** 即可。")
    
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        height=650,
        column_config={
            "序号": st.column_config.NumberColumn(width="small"),
            "设备名称": st.column_config.TextColumn("设备名称", width="large"),
            "设备名": st.column_config.TextColumn("设备名", width="medium"),
            "价值": st.column_config.NumberColumn(format="￥%.2f")
        },
        key="main_asset_editor"
    )

    if st.button("💾 保存档案所有修改"):
        edited_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        st.success("✅ 档案库已保存！")
        time.sleep(1)
        st.rerun()
