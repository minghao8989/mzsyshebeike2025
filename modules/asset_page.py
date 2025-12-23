import streamlit as st
import pandas as pd
import os
import time

def show_asset():
    # 注入高级 CSS：解决内容显示不全（换行）和美化树状结构
    st.markdown("""
        <style>
        /* 核心修复：允许单元格内容自动换行，显示完整编号 */
        div[data-testid="stDataFrame"] td {
            white-space: normal !important;
            word-break: break-all !important;
            line-height: 1.4 !important;
            vertical-align: top !important;
        }
        /* 强化科室标题行的视觉效果 */
        .dept-header {
            background-color: rgba(59, 130, 246, 0.1);
            padding: 8px 15px;
            border-radius: 8px;
            border-left: 5px solid #3b82f6;
            margin: 15px 0 10px 0;
            font-weight: bold;
            color: #3b82f6;
            cursor: pointer;
        }
        [data-testid="stMetricValue"] { color: #3b82f6 !important; font-size: 1.8rem !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📊 医院资产档案 (树状折叠版)")
    file_path = "data/equipment.csv"
    
    if not os.path.exists(file_path):
        st.warning("📂 档案库目前为空。")
        return

    # 读取 25 位标准数据
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    
    # 核心修复 1：自动重新生成全局连续序号
    df['序号'] = range(1, len(df) + 1)

    # 顶部统计
    c1, c2, c3 = st.columns(3)
    c1.metric("总资产条目", f"{len(df)} 条")
    val = pd.to_numeric(df['价值'], errors='coerce').sum()
    c2.metric("固定资产总值", f"￥{val:,.2f}")
    c3.metric("覆盖科室", f"{df['科室'].nunique()} 个")

    st.divider()

    # 搜索功能
    search_q = st.text_input("🔍 全文检索 (支持国标码、SN码、设备名)...")
    if search_q:
        df = df[df.apply(lambda r: r.astype(str).str.contains(search_q, case=False).any(), axis=1)]

    # 核心修复 3：树状折叠展示逻辑
    st.subheader("🏢 科室资产清单")
    st.caption("提示：点击下方科室名称即可展开或收起该科室的详细设备列表。")

    # 获取所有唯一科室
    all_depts = df['科室'].unique()
    
    # 用于存储所有修改后的数据
    all_edited_dfs = []

    for dept in all_depts:
        # 处理空科室名称
        dept_display = dept if pd.notna(dept) else "未归类科室"
        
        # 每一个科室创建一个折叠器 (Expander)
        with st.expander(f"📁 {dept_display} (包含 {len(df[df['科室']==dept])} 件设备)", expanded=False):
            dept_df = df[df['科室'] == dept]
            
            # 核心修复 2：配置表格，开启列宽自适应，显示完整内容
            edited_dept_df = st.data_editor(
                dept_df,
                num_rows="dynamic",
                use_container_width=True,
                # 关键：这里限制高度并允许滚动，同时 CSS 负责内部换行
                height=350,
                column_config={
                    "序号": st.column_config.NumberColumn(width="small", disabled=True),
                    "设备名称": st.column_config.TextColumn("设备名称", width="medium"),
                    "老编号": st.column_config.TextColumn("老编号/条码", width="large"),
                    "设备SN码": st.column_config.TextColumn("SN码", width="medium"),
                    "价值": st.column_config.NumberColumn(format="￥%.2f"),
                    "设备状态": st.column_config.SelectboxColumn(options=["正常", "维修中", "封存", "待报废"])
                },
                key=f"editor_{dept}"
            )
            all_edited_dfs.append(edited_dept_df)

    # 汇总保存逻辑
    st.markdown("---")
    col_save, col_down, _ = st.columns([1, 1, 4])
    
    if col_save.button("💾 保存所有科室变更"):
        # 合并所有被编辑过的分表数据
        final_df = pd.concat(all_edited_dfs, ignore_index=True)
        # 重新排序，确保序号依然是连续的
        final_df['序号'] = range(1, len(final_df) + 1)
        final_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        st.success("✅ 资产档案库已全局同步！")
        time.sleep(1)
        st.rerun()

    with col_down:
        csv_bin = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 导出全院总表", data=csv_bin, file_name="全院资产总表.csv", mime="text/csv")
