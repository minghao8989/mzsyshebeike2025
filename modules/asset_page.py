import streamlit as st
import pandas as pd
import os

def show_asset():
    # --- 修正后的打印优化 CSS ---
    # 删除了错误的参数，修正为 unsafe_allow_html=True
    st.markdown("""
        <style>
        @media print {
            /* 打印时隐藏侧边栏、按钮、搜索框和页眉 */
            [data-testid="stSidebar"], .stButton, .stDownloadButton, .stTextInput, header {
                display:none !important;
            }
            /* 铺满纸张 */
            .main .block-container {
                padding: 0 !important;
                max-width: 100% !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("🏥 医疗装备档案库")
    
    file_path = "data/equipment.csv"
    
    # 1. 检查文件是否存在
    if not os.path.exists(file_path):
        st.error(f"未找到数据文件：{file_path}，请确保 GitHub 中已创建该文件。")
        return

    # 2. 读取数据 (包含编码容错逻辑)
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except:
        try:
            df = pd.read_csv(file_path, encoding='gbk')
        except Exception as e:
            st.error(f"读取数据失败，请检查文件编码。错误信息: {e}")
            return

    # 3. 顶部统计指标 (基于您自定义的列名)
    st.subheader("📊 全院资产概览")
    c1, c2, c3 = st.columns(3)
    c1.metric("管理设备总数", f"{len(df)} 台/套")
    
    # 安全匹配“设备状态”列
    status_col = "设备状态"
    if status_col in df.columns:
        active_count = len(df[df[status_col].isin(['正常', '在用', '运行中'])])
        c2.metric("正常运行设备", active_count)
    else:
        c2.metric("正常运行", "列名未匹配")
    
    # 安全匹配“购置金额”列
    price_col = "购置金额"
    if price_col in df.columns:
        total_money = pd.to_numeric(df[price_col], errors='coerce').sum()
        c3.metric("资产总值", f"￥{total_money:,.2f}")
    else:
        c3.metric("资产总值", "列名未匹配")

    st.divider()

    # 4. 数据查询与 A4 打印模拟区
    st.subheader("🔍 档案明细 (支持 A4 打印预览)")
    
    search = st.text_input("输入关键词搜索（打印前请清空搜索框以显示全部数据）：")
    if search:
        display_df = df[df.apply(lambda row: row.astype(str).str.contains(search).any(), axis=1)]
    else:
        display_df = df

    # 设置表格高度：根据数据行数动态计算，最大 800px 以模拟 A4 长度
    table_height = min(len(display_df) * 35 + 100, 800) 

    # 渲染数据编辑器
    edited_df = st.data_editor(
        display_df, 
        num_rows="dynamic", 
        use_container_width=True, 
        height=table_height,       
        column_config={
            "科室名称": st.column_config.TextColumn("科室名称", width="medium"),
            "设备名称": st.column_config.TextColumn("设备名称", width="large"),
            "购置金额": st.column_config.NumberColumn("金额", format="￥%.2f"),
            "设备状态": st.column_config.SelectboxColumn(
                "状态",
                options=["正常", "维修中", "待报废", "封存", "计量中"],
                required=True
            )
        }
    )
    
    # 5. 操作按钮区
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
    
    if col_btn1.button("💾 保存变动"):
        # 保存时强制使用 utf-8-sig 以兼容 Excel 中文显示
        edited_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        st.success("✅ 档案已成功同步！")
        st.rerun()
    
    with col_btn2:
        csv_data = edited_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📥 导出 Excel", data=csv_data, file_name="医疗装备档案.csv")

    st.caption("🛠️ **打印指南**：按 **Ctrl+P**。建议：纸张选『横向』，缩放选『适应页宽』，并勾选『打印背景图形』。")
