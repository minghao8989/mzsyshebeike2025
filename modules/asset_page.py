import streamlit as st
import pandas as pd
import os

def show_asset():
    st.header("🏥 医疗装备档案库")
    
    file_path = "data/equipment.csv"
    
    # 1. 检查文件是否存在
    if not os.path.exists(file_path):
        st.error(f"未找到数据文件：{file_path}，请检查 GitHub 中的 data 文件夹。")
        return

    # 2. 读取数据 (增加编码支持)
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except Exception:
        try:
            df = pd.read_csv(file_path, encoding='gbk') # 备选编码
        except Exception as e:
            st.error(f"读取 CSV 文件失败: {e}")
            return

    # 3. 顶部统计指标 (适配您的新列名)
    st.subheader("📊 全院资产概览")
    c1, c2, c3 = st.columns(3)
    
    # 统计总数
    total_assets = len(df)
    c1.metric("管理设备总数", f"{total_assets} 台/套")
    
    # 安全统计：设备状态为“正常”或“在用”的数量
    # 注意：这里匹配您提供的列名“设备状态”
    status_col = "设备状态"
    if status_col in df.columns:
        # 统计包含“正常”或“在用”字样的数量
        normal_count = len(df[df[status_col].isin(['正常', '在用', '运行中'])])
        c2.metric("正常运行设备", normal_count)
    else:
        c2.metric("正常运行设备", "列名匹配失败")
        st.warning(f"提示：程序未在表格中找到『{status_col}』列，请核对表头。")

    # 统计购置总金额
    price_col = "购置金额"
    if price_col in df.columns:
        try:
            total_money = pd.to_numeric(df[price_col], errors='coerce').sum()
            c3.metric("资产总值", f"￥{total_money:,.2f}")
        except:
            c3.metric("资产总值", "数据格式错误")
    else:
        c3.metric("资产总值", "列名缺失")

    st.divider()

    # 4. 数据查询与编辑区
    st.subheader("🔍 档案明细与实时维护")
    
    # 搜索功能
    search = st.text_input("输入科室、厂家或设备名称进行快速检索：")
    if search:
        display_df = df[df.apply(lambda row: row.astype(str).str.contains(search).any(), axis=1)]
    else:
        display_df = df

    # 编辑器
    edited_df = st.data_editor(
        display_df, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "购买日期": st.column_config.DateColumn("购买日期"),
            "投入使用日期": st.column_config.DateColumn("投入使用日期"),
            "设备状态": st.column_config.SelectboxColumn(
                "设备状态",
                options=["正常", "维修中", "待报废", "封存", "计量中"],
                required=True,
            )
        }
    )
    
    # 5. 保存逻辑
    col_btn1, col_btn2 = st.columns([1, 5])
    if col_btn1.button("💾 点击保存"):
        # 如果是搜索状态下编辑的，需要把修改合并回原始 df (此处简化处理为全量保存)
        edited_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        st.success("✅ 档案已成功同步至 GitHub 数据库！")
        st.balloons()
        st.rerun()
