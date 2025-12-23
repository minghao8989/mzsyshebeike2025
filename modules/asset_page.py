import streamlit as st
import pandas as pd
import os

def show_asset():
    # 注入 CSS 优化：确保 24 列超长表格在任何屏幕下都可平滑横向滚动，且表头不换行
    st.markdown("""
        <style>
        .stDataFrame div[data-testid="stTable"] { font-size: 0.8rem; }
        [data-testid="stMetricValue"] { font-size: 1.8rem !important; }
        /* 强制表格容器支持横向滚动 */
        div[data-testid="stDataFrame"] > div { overflow-x: auto !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📋 医院资产综合档案管理")
    
    file_path = "data/equipment.csv"
    
    if not os.path.exists(file_path):
        st.error("未找到数据文件，请检查 data/equipment.csv 是否已创建并上传。")
        return

    # 1. 读取数据 (处理重复列名)
    try:
        # 您的目录中有两个"设备名"，Pandas会自动将其重命名为"设备名"和"设备名.1"
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except Exception as e:
        st.error(f"档案读取失败: {e}")
        return

    # 2. 顶部核心指标统计
    st.subheader("🏥 资产运行态势")
    col1, col2, col3, col4 = st.columns(4)
    
    # 总台数 (基于数量列求和)
    if '数量' in df.columns:
        total_qty = pd.to_numeric(df['数量'], errors='coerce').sum()
        col1.metric("资产总数量", f"{int(total_qty) if not pd.isna(total_qty) else 0} 件/套")
    else:
        col1.metric("资产总条数", len(df))

    # 总价值 (基于“价值”列)
    if '价值' in df.columns:
        total_val = pd.to_numeric(df['价值'], errors='coerce').sum()
        col2.metric("固定资产总值", f"￥{total_val:,.2f}")

    # 正常运行数
    status_col = '设备状态'
    if status_col in df.columns:
        normal_df = df[df[status_col].isin(['正常', '在用', '良好'])]
        col3.metric("运行正常", len(normal_df))
    
    # 报废预警 (模拟逻辑：可报废年限 <= 2025)
    if '可报废年限' in df.columns:
        warning_count = len(df[pd.to_numeric(df['可报废年限'], errors='coerce') <= 2025])
        col4.metric("近期待报废", warning_count)

    st.divider()

    # 3. 档案明细查询与维护
    st.subheader("🔍 资产档案全字段检索")
    
    # 全局搜索
    q = st.text_input("输入科室、SN码、编号或品牌进行快速定位...", placeholder="例如：精神科一区")
    if q:
        # 在所有列中搜索关键词
        mask = df.apply(lambda row: row.astype(str).str.contains(q, case=False).any(), axis=1)
        display_df = df[mask]
    else:
        display_df = df

    # 4. 高级数据编辑器 (24 列全字段开启)
    st.info("💡 提示：您可以横向滑动表格查看所有 24 个字段。双击单元格可编辑，完成后点击下方保存。")
    
    edited_df = st.data_editor(
        display_df,
        num_rows="dynamic",
        use_container_width=True,
        height=600,
        column_config={
            "科室": st.column_config.TextColumn("所属科室", width="medium"),
            "设备名": st.column_config.TextColumn("设备名称", width="large"),
            "价值": st.column_config.NumberColumn("总价值", format="￥%.2f"),
            "价格": st.column_config.NumberColumn("单价", format="￥%.2f"),
            "出厂日期": st.column_config.DateColumn("出厂日期"),
            "验收日期": st.column_config.DateColumn("验收日期"),
            "设备状态": st.column_config.SelectboxColumn(
                "设备状态",
                options=["正常", "维修中", "封存", "待报废", "计量中"],
                required=True
            ),
            "厂家电话": st.column_config.TextColumn("厂家/售后电话")
        }
    )

    # 5. 保存与同步
    btn_col1, btn_col2, _ = st.columns([1, 1, 4])
    if btn_col1.button("💾 同步变更到数据库"):
        edited_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        st.success("✅ 档案库已成功更新并保存！")
        st.rerun()

    with btn_col2:
        output_csv = edited_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            "📥 导出当前报表",
            data=output_csv,
            file_name=f"资产档案导出_{time.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
