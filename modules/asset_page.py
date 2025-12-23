import streamlit as st
import pandas as pd
import os
import time

def show_asset():
    st.markdown("""
        <style>
        div[data-testid="stDataFrame"] > div { overflow-x: auto !important; }
        .stDataFrame div[data-testid="stTable"] { font-size: 0.8rem; }
        [data-testid="stMetricValue"] { color: #3b82f6; font-size: 1.8rem !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📊 医疗装备综合资产档案")
    file_path = "data/equipment.csv"
    
    if not os.path.exists(file_path):
        st.warning("📂 档案库目前为空，请在后台管理中执行数据导入。")
        return

    # 读取包含 25 个标准字段的数据
    df = pd.read_csv(file_path, encoding='utf-8-sig')

    # 看板统计 (空值不参与计算，由 Pandas 自动处理)
    st.subheader("🏥 资产运行态势")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("已录入资产", f"{len(df)} 条")
    
    val = pd.to_numeric(df['价值'], errors='coerce').sum()
    c2.metric("总资产价值", f"￥{val:,.2f}")
    
    dept_count = df['科室'].dropna().nunique()
    c3.metric("覆盖科室数", f"{dept_count} 个")
    
    c4.metric("待完善条目", df.isnull().any(axis=1).sum())

    st.divider()

    # 搜索功能
    q = st.text_input("🔍 档案全局检索 (支持科室、名称、国标码、SN码、老编号)...")
    if q:
        display_df = df[df.apply(lambda r: r.astype(str).str.contains(q, case=False).any(), axis=1)]
    else:
        display_df = df

    # 渲染 25 位标准表格
    st.info("💡 提示：您可以直接在下表中补全未完善的空格，修改后点击『保存』。")
    edited_df = st.data_editor(
        display_df,
        num_rows="dynamic",
        use_container_width=True,
        height=600,
        column_config={
            "序号": st.column_config.NumberColumn(width="small"),
            "设备名称": st.column_config.TextColumn("设备名称 (主)", width="medium"),
            "设备名": st.column_config.TextColumn("设备名 (别名)", width="medium"),
            "资产国标代码": st.column_config.TextColumn("国标码", width="medium"),
            "价值": st.column_config.NumberColumn(format="￥%.2f"),
        }
    )

    # 操作按钮
    col_save, col_down, _ = st.columns([1, 1, 4])
    if col_save.button("💾 保存档案变更"):
        edited_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        st.success("✅ 资产档案修改已保存。")
        time.sleep(1)
        st.rerun()
    
    with col_down:
        csv_bin = edited_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 导出报表", data=csv_bin, file_name="资产档案导出.csv", mime="text/csv")
