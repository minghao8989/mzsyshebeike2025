import streamlit as st
import pandas as pd
import os
import time

def show_asset():
    # 1. 注入 CSS：强制单元格换行（解决内容显示不全）并美化按钮
    st.markdown("""
        <style>
        /* 核心修复：允许单元格内容自动换行，确保长编号显示完整 */
        div[data-testid="stDataFrame"] td {
            white-space: normal !important;
            word-break: break-all !important;
            line-height: 1.4 !important;
            vertical-align: top !important;
        }
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

    # 读取 25 位标准数据
    df = pd.read_csv(file_path, encoding='utf-8-sig')

    # 核心修复：全局自动校准序号 (1 to N)
    df['序号'] = range(1, len(df) + 1)

    # --- 第一部分：看板统计 ---
    st.subheader("🏥 资产概览")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("已录入资产", f"{len(df)} 条")
    val = pd.to_numeric(df['价值'], errors='coerce').sum()
    c2.metric("总资产价值", f"￥{val:,.2f}")
    c3.metric("覆盖科室", f"{df['科室'].dropna().nunique()} 个")
    c4.metric("待完善字段", df.isnull().sum().sum())

    st.divider()

    # --- 第二部分：原有的全院总表编辑器 (支持 Ctrl+V 粘贴) ---
    st.subheader("⌨️ 全院总表快速编辑 (支持 Excel 粘贴)")
    st.info("💡 **操作提醒**：此表用于大批量数据粘贴。修改后请点击下方的『保存档案所有修改』。内容会自动按科室同步到下方的树状图。")
    
    main_edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        height=500,
        column_config={
            "序号": st.column_config.NumberColumn(width="small", disabled=True),
            "设备名称": st.column_config.TextColumn("设备名称", width="large"),
            "老编号": st.column_config.TextColumn("老编号/条码", width="large"),
            "价值": st.column_config.NumberColumn(format="￥%.2f")
        },
        key="main_asset_editor"
    )

    if st.button("💾 保存档案所有修改"):
        # 保存时重新计算序号，确保 100% 连续
        main_edited_df['序号'] = range(1, len(main_edited_df) + 1)
        main_edited_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        st.success("✅ 全院档案已同步保存！")
        time.sleep(1)
        st.rerun()

    st.divider()

    # --- 第三部分：新增的科室树状图功能 ---
    st.subheader("🌳 科室资产树状视图 (支持收缩与局部增删)")
    st.caption("提示：您可以点击下方科室名称展开/收起。这里的修改也需要点击保存才能生效。")

    # 获取唯一科室列表并排序
    all_depts = sorted(main_edited_df['科室'].dropna().unique().tolist())
    
    # 用于树状图编辑的临时存储
    tree_edited_list = []

    for dept in all_depts:
        # 按科室过滤数据
        dept_data = main_edited_df[main_edited_df['科室'] == dept].copy()
        
        with st.expander(f"📁 {dept} (设备数量: {len(dept_data)})"):
            # 科室内部的小编辑器
            sub_edited_df = st.data_editor(
                dept_data,
                num_rows="dynamic",
                use_container_width=True,
                height=300,
                column_config={
                    "序号": st.column_config.NumberColumn(width="small", disabled=True),
                    "设备名称": st.column_config.TextColumn("设备名称", width="medium"),
                    "老编号": st.column_config.TextColumn("老编号", width="large")
                },
                key=f"tree_editor_{dept}"
            )
            tree_edited_list.append(sub_edited_df)
            
            # 科室内的快捷操作
            c_add, _ = st.columns([2, 8])
            if c_add.button(f"➕ 在 {dept} 新增设备", key=f"btn_add_{dept}"):
                # 构造一行新数据
                new_row = pd.DataFrame([{"科室": dept, "设备状态": "正常"}])
                # 直接追加到总数据并保存，实现“树状添加”
                save_df = pd.concat([main_edited_df, new_row], ignore_index=True)
                save_df['序号'] = range(1, len(save_df) + 1)
                save_df.to_csv(file_path, index=False, encoding='utf-8-sig')
                st.rerun()

    # 底部导出功能
    st.markdown("---")
    csv_bin = main_edited_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button("📥 导出全院资产总表", data=csv_bin, file_name="资产档案导出.csv", mime="text/csv")
