import streamlit as st
import pandas as pd
import os
import time

def show_asset():
    # 1. 注入 CSS：确保科室列高亮，长内容自动换行
    st.markdown("""
        <style>
        /* 核心修复：内容自动换行，确保长编号不被遮挡 */
        div[data-testid="stDataFrame"] td {
            white-space: normal !important;
            word-break: break-all !important;
            line-height: 1.4 !important;
        }
        /* 统计看板美化 */
        [data-testid="stMetricValue"] { color: #3b82f6 !important; font-size: 1.8rem !important; }
        /* 强化表格边框 */
        [data-testid="stTable"] td { border: 1px solid #262730 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📊 医疗装备综合资产档案")
    file_path = "data/equipment.csv"
    
    if not os.path.exists(file_path):
        st.warning("📂 档案库目前为空，请先在后台执行导入。")
        return

    # 读取 25 位标准数据
    df = pd.read_csv(file_path, encoding='utf-8-sig')

    # 核心自动化：无论如何粘贴，保存时都会重排序号 (1 到 N)
    df['序号'] = range(1, len(df) + 1)

    # --- 第一部分：指标看板 ---
    st.subheader("🏥 资产数据实时统计")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("资产总数", f"{len(df)} 条")
    val = pd.to_numeric(df['价值'], errors='coerce').sum()
    c2.metric("固定资产总值", f"￥{val:,.2f}")
    c3.metric("管理科室数", f"{df['科室'].dropna().nunique()} 个")
    c4.metric("空缺字段数", df.isnull().sum().sum())

    st.divider()

    # --- 第二部分：全院总表 (已修复：科室列可打字、可粘贴) ---
    st.subheader("⌨️ 全院数据录入 (支持 Excel 批量粘贴)")
    st.info("💡 **操作指南**：\n1. 您可以在『科室』及任何列直接打字或 Ctrl+V 粘贴。\n2. 修改后请务必点击下方的『保存档案所有修改』。")
    
    # 关键修复：不对任何列进行 disabled 限制，确保全部可编辑
    main_edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        height=500,
        column_config={
            "序号": st.column_config.NumberColumn(width="small", disabled=True), # 序号由系统自动生成
            "科室": st.column_config.TextColumn("科室 (可粘贴/打字)", width="medium"), # 恢复可编辑
            "设备名称": st.column_config.TextColumn("设备名称", width="large"),
            "老编号": st.column_config.TextColumn("老编号/条码", width="large"),
            "价值": st.column_config.NumberColumn(format="￥%.2f"),
            "设备状态": st.column_config.SelectboxColumn(options=["正常", "维修中", "待报废", "封存"])
        },
        key="main_asset_editor"
    )

    if st.button("💾 保存档案所有修改"):
        # 核心逻辑：保存前强制刷新序号
        main_edited_df['序号'] = range(1, len(main_edited_df) + 1)
        main_edited_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        st.success("✅ 数据已同步至云端数据库！")
        time.sleep(1)
        st.rerun()

    st.divider()

    # --- 第三部分：树状展示区 (基于总表数据动态生成) ---
    st.subheader("🌳 科室资产树状视图")
    st.caption("提示：此处会根据您上方输入的『科室』自动分类。点击即可展开查看。")

    # 动态获取当前所有已填写的科室并排序
    valid_depts = sorted(main_edited_df['科室'].dropna().unique().tolist())
    
    for dept in valid_depts:
        dept_data = main_edited_df[main_edited_df['科室'] == dept]
        
        # 使用折叠器实现树状图
        with st.expander(f"📁 {dept} (设备清单: {len(dept_data)} 条)"):
            # 展示该科室数据，并允许局部微调
            st.dataframe(
                dept_data,
                use_container_width=True,
                column_config={
                    "序号": st.column_config.NumberColumn(width="small"),
                    "老编号": st.column_config.TextColumn(width="large")
                }
            )
            # 在该科室快速添加一行
            if st.button(f"➕ 在 {dept} 底部快速增行", key=f"add_{dept}"):
                new_row = pd.DataFrame([{"科室": dept, "设备状态": "正常"}])
                save_df = pd.concat([main_edited_df, new_row], ignore_index=True)
                save_df['序号'] = range(1, len(save_df) + 1)
                save_df.to_csv(file_path, index=False, encoding='utf-8-sig')
                st.rerun()

    # 导出功能
    st.markdown("---")
    csv_bytes = main_edited_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button("📥 导出全院资产 Excel 格式 (CSV)", data=csv_bytes, file_name="资产总表.csv", mime="text/csv")
