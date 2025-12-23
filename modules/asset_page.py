import streamlit as st
import pandas as pd
import os
import time

def show_asset():
    # 1. 注入 CSS 解决显示不全（换行）和按钮美化
    st.markdown("""
        <style>
        /* 强制表格单元格内容自动换行，显示完整编号 */
        div[data-testid="stDataFrame"] td {
            white-space: normal !important;
            word-break: break-all !important;
            line-height: 1.5 !important;
        }
        /* 隐藏表格内部自带的添加行按钮，改用我们自定义的科室定位按钮 */
        [data-testid="stDataFrame"] button[title="Add row"] { display: none; }
        
        .dept-stat { color: #60a5fa; font-size: 0.85rem; font-weight: normal; }
        [data-testid="stMetricValue"] { color: #3b82f6 !important; font-size: 1.8rem !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("🏢 医院资产科室树状管理平台")
    file_path = "data/equipment.csv"
    
    if not os.path.exists(file_path):
        st.warning("📂 档案库目前为空，请在后台执行数据合并。")
        return

    # 加载 25 位标准数据
    # 标准目录：序号,科室,设备名称,资产国标代码,国标代码+地点+流水,设备SN码,老编号,价值,设备名,数量,品牌,型号,生产编号,出厂日期,价格,验收日期,设备状态,械字号,使用年限,调拨情况,可报废年限,厂家电话,工作站厂家,工作站厂家电话,备注
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    
    # 核心修复：自动校准序号
    df['序号'] = range(1, len(df) + 1)

    # 顶部统计
    c1, c2, c3 = st.columns(3)
    c1.metric("资产总数", f"{len(df)} 台/套")
    total_val = pd.to_numeric(df['价值'], errors='coerce').sum()
    c2.metric("固定资产总值", f"￥{total_val:,.2f}")
    c3.metric("管理科室", f"{df['科室'].nunique()} 个")

    st.divider()

    # 搜索功能
    search_q = st.text_input("🔍 输入资产编号、SN码或名称在全院范围内搜索...", placeholder="全字段检索")
    if search_q:
        df = df[df.apply(lambda r: r.astype(str).str.contains(search_q, case=False).any(), axis=1)]

    # 2. 树状图核心逻辑：按科室分组折叠
    st.subheader("📁 科室资产清单")
    
    # 获取唯一的科室列表
    all_depts = df['科室'].unique().tolist()
    # 确保空科室显示为“未分类”
    all_depts = [d if pd.notna(d) else "未分类" for d in all_depts]
    
    final_edited_data = []

    for dept in all_depts:
        dept_filter = df['科室'] == dept if dept != "未分类" else df['科室'].isna()
        dept_data = df[dept_filter].copy()
        
        # 每一个科室一个折叠器 
        with st.expander(f"🏢 {dept} (设备数: {len(dept_data)})", expanded=False):
            # 表格编辑区 (支持批量粘贴)
            edited_dept_df = st.data_editor(
                dept_data,
                num_rows="dynamic",
                use_container_width=True,
                height=300,
                column_config={
                    "序号": st.column_config.NumberColumn(disabled=True, width="small"),
                    "老编号": st.column_config.TextColumn("老编号 (完整显示)", width="large"),
                    "设备名称": st.column_config.TextColumn("设备名称", width="medium"),
                    "价值": st.column_config.NumberColumn(format="￥%.2f"),
                    "设备状态": st.column_config.SelectboxColumn(options=["正常", "维修中", "待报废", "封存"])
                },
                key=f"editor_{dept}"
            )
            
            # 添加/删除操作辅助
            c_add, c_del, _ = st.columns([1.5, 1.5, 7])
            if c_add.button(f"➕ 添加到 {dept}", key=f"add_{dept}"):
                new_row = pd.DataFrame([{"科室": dept, "设备状态": "正常"}])
                edited_dept_df = pd.concat([edited_dept_df, new_row], ignore_index=True)
                st.info(f"已在 {dept} 底部新增空白行，请填写后保存。")
            
            final_edited_data.append(edited_dept_df)

    # 3. 全局保存逻辑
    st.markdown("---")
    btn_save, btn_export, _ = st.columns([1, 1, 4])
    
    if btn_save.button("💾 保存所有树状图变更"):
        if final_edited_data:
            # 合并所有科室的数据
            new_df = pd.concat(final_edited_data, ignore_index=True)
            # 重新生成全院唯一的连续序号
            new_df['序号'] = range(1, len(new_df) + 1)
            # 保存
            new_df.to_csv(file_path, index=False, encoding='utf-8-sig')
            st.success("🎉 全院资产档案已同步成功！")
            time.sleep(1)
            st.rerun()

    with btn_export:
        csv_bytes = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 导出全院总表", data=csv_bytes, file_name="三院资产总表.csv", mime="text/csv")
