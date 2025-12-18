import streamlit as st
import pandas as pd

def show_asset():
    st.header("📊 医疗装备档案管理")
    
    # 读取数据
    df = pd.read_csv("data/equipment.csv")
    
    # 顶部统计卡片
    c1, c2, c3 = st.columns(3)
    c1.metric("总资产数量", len(df))
    c2.metric("在用设备", len(df[df['状态']=='在用']))
    c3.metric("待强检", "2")
    
    # 可编辑的表格
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("保存资产变动"):
        edited_df.to_csv("data/equipment.csv", index=False, encoding='utf-8-sig')
        st.success("资产数据库已同步！")