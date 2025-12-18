import streamlit as st
import pandas as pd
from datetime import datetime

def show_repair():
    st.header("🔧 设备故障报修单")
    
    with st.form("repair_form"):
        eq_id = st.text_input("设备编号/资产条码")
        dept = st.selectbox("报修科室", ["ICU", "手术室", "放射科", "内科"])
        desc = st.text_area("故障详细描述")
        
        submitted = st.form_submit_button("提交报修申请")
        if submitted:
            # 简单模拟保存
            st.success(f"报修已受理！单号：REQ-{datetime.now().strftime('%m%d%H%M')}")
            st.info("维修工程师将收到即时提醒。")