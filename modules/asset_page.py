import streamlit as st
import pandas as pd
import os
import time

def show_asset():
    # 注入高级 CSS：适配 25 列超长表格，确保在大屏和小屏下都能横向滚动且文字清晰
    st.markdown("""
        <style>
        /* 强制表格容器支持横向滚动 */
        div[data-testid="stDataFrame"] > div { overflow-x: auto !important; }
        /* 调整表格字号，适配多列显示 */
        .stDataFrame div[data-testid="stTable"] { font-size: 0.8rem; }
        /* 优化统计指标卡片 */
        [data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 700; color: #3b82f6; }
        /* 打印模式优化 */
        @media print {
            [data-testid="stSidebar"], .stButton, .stDownloadButton, header { display:none !important; }
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("📊 医疗装备综合资产档案")
    
    file_path = "data/equipment.csv"
    
    if not os.path.exists(file_path):
        st.error("未找到数据文件，请检查 data/equipment.csv 是否已上传。")
        return

    # 1. 读取数据
    try:
        # 使用 utf-8-sig 确保 Excel 导出不乱码
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except Exception as e:
        st.error(f"档案读取失败: {e}")
        return

    # 2. 顶部核心数据看板 (基于您的 25 列字段)
    st.subheader("🏥 资产运行态势概览")
    c1, c2, c3, c4 = st.columns(4)
    
    # 统计总数量 (基于“数量”列)
    if '数量' in df.columns:
        total_qty = pd.to_numeric(df['数量'], errors='coerce').sum()
        c1.metric("资产总数量", f"{int(total_qty) if not pd.isna(total_qty) else 0} 件/套")
    
    # 统计总价值 (基于“价值”列)
    if '价值' in df.columns:
        total_val = pd.to_numeric(df['价值'], errors='coerce').sum()
        c2.metric("固定资产总额", f"￥{total_val:,.2f}")

    # 统计设备状态 (基于“设备状态”列)
    if '设备状态' in df.columns:
        normal_count = len(df[df['设备状态'].isin(['正常', '在用', '良好'])])
        c3.metric("运行正常率", f"{int(normal_count/len(df)*100) if len(df)>0 else 0}%")
    
    # 统计待报废 (基于“可报废年限”列，假设当前年份为 2025)
    if '可报废年限' in df.columns:
        scrap_count = len(df[pd.to_numeric(df['可报废年限'], errors='coerce') <= 2025])
        c4.metric("近期待报废", f"{scrap_count} 台")

    st.divider()

    # 3. 搜索与筛选 (全字段匹配)
    st.subheader("🔍 档案明细查询")
    search_q = st.text_input("🔍 全文检索：输入序号、科室、设备名、SN码、编号或厂家...", placeholder="支持任意字段搜索")
    
    if search_q:
        display_df = df[df.apply(lambda row: row.astype(str).str.contains(search_q, case=False).any(), axis=1)]
    else:
        display_df = df

    # 4. 高级资产编辑器 (精准适配 25 列)
    st.info("💡 提示：点击表头可排序。您可以直接双击单元格修改数据，完成后点击下方『保存』。")
    
    # 计算表格高度
    dynamic_height = min(len(display_df) * 35 + 100, 700)

    edited_df = st.data_editor(
        display_df,
        num_rows="dynamic",
        use_container_width=True,
        height=dynamic_height,
        column_config={
            "序号": st.column_config.NumberColumn("序号", width="small", format="%d"),
            "科室": st.column_config.TextColumn("所属科室", width="medium"),
            "设备名": st.column_config.TextColumn("设备名称", width="large"),
            "价值": st.column_config.NumberColumn("价值", format="￥%.2f"),
            "价格": st.column_config.NumberColumn("单价", format="￥%.2f"),
            "出厂日期": st.column_config.DateColumn("出厂日期", format="YYYY-MM-DD"),
            "验收日期": st.column_config.DateColumn("验收日期", format="YYYY-MM-DD"),
            "设备状态": st.column_config.SelectboxColumn(
                "状态",
                options=["正常", "维修中", "封存", "待报废", "计量中"],
                required=True
            ),
            "厂家电话": st.column_config.TextColumn("厂家电话")
        }
    )

    # 5. 数据持久化与导出
    btn1, btn2, btn3 = st.columns([1, 1, 4])
    
    if btn1.button("💾 保存档案"):
        edited_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        st.success("✅ 资产档案已同步至 GitHub 数据库！")
        time.sleep(1)
        st.rerun()

    with btn2:
        csv_data = edited_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            "📥 导出 CSV",
            data=csv_data,
            file_name=f"资产报表_{time.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
