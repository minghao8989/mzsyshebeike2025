import streamlit as st
import pandas as pd
import os
import time

def show_asset():
    # 注入高清晰 CSS 样式
    st.markdown("""
        <style>
        /* 强化表格内容显示与对比度 */
        div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
            color: #FFFFFF !important; font-size: 0.95rem !important;
            white-space: normal !important; word-break: break-all !important;
        }
        /* 指标看板颜色分级：蓝色(基础统计)、警告色(年限统计) */
        [data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 800 !important; }
        
        /* 顶部看板配色 */
        .main-stat [data-testid="stMetricValue"] { color: #38BDF8 !important; } /* 天蓝色 */
        .age-stat:nth-child(1) [data-testid="stMetricValue"] { color: #38BDF8; }
        .age-stat:nth-child(2) [data-testid="stMetricValue"] { color: #FACC15; }
        .age-stat:nth-child(3) [data-testid="stMetricValue"] { color: #FB923C; }
        .age-stat:nth-child(4) [data-testid="stMetricValue"] { color: #F87171; }
        
        [data-testid="stTable"] { background-color: #111827 !important; border: 1px solid #374151 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📊 医疗装备综合资产档案")
    path = "data/equipment.csv"
    
    if not os.path.exists(path):
        st.error("❌ 数据未初始化。请前往『后台管理』->『🚀 资产导入』点击一键合并。")
        return

    # 安全读取数据
    df = pd.read_csv(path, encoding='utf-8-sig')
    
    # 核心：安全计算年限 (基准2025年)
    curr_yr = 2025
    def calc_age(row):
        try:
            val = str(row['出厂日期'])
            year = int(val[:4]) 
            return curr_yr - year
        except: return 0
    df['age'] = df.apply(calc_age, axis=1)

    # --- 第一部分：综合统计看板 (新增需求) ---
    st.subheader("📈 资产数据实时统计")
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        total_val = pd.to_numeric(df['价值'], errors='coerce').sum()
        st.markdown('<div class="main-stat">', unsafe_allow_html=True)
        st.metric("资产总价值", f"￥{total_val:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with m2:
        total_qty = pd.to_numeric(df['数量'], errors='coerce').sum()
        st.markdown('<div class="main-stat">', unsafe_allow_html=True)
        st.metric("资产总数量", f"{int(total_qty) if not pd.isna(total_qty) else 0} 台/套")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with m3:
        dept_count = df['科室'].dropna().nunique()
        st.markdown('<div class="main-stat">', unsafe_allow_html=True)
        st.metric("在管科室数", f"{dept_count} 个")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with m4:
        # 统计除辅助计算列外，存在空值的行数
        incomplete_count = df.drop(columns=['age'], errors='ignore').isnull().any(axis=1).sum()
        st.markdown('<div class="main-stat">', unsafe_allow_html=True)
        st.metric("未完善数据量", f"{incomplete_count} 条")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # --- 第二部分：年限看板 ---
    st.subheader("⚠️ 关键年限统计 (基准2025年)")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="age-stat">', unsafe_allow_html=True); st.metric("5年以上", len(df[df['age'] >= 5])); st.markdown('</div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="age-stat">', unsafe_allow_html=True); st.metric("7年以上", len(df[df['age'] >= 7])); st.markdown('</div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="age-stat">', unsafe_allow_html=True); st.metric("10年以上", len(df[df['age'] >= 10])); st.markdown('</div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="age-stat">', unsafe_allow_html=True); st.metric("13年以上", len(df[df['age'] >= 13])); st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # --- 第三部分：全院数据维护 (支持粘贴) ---
    st.subheader("⌨️ 数据维护总表")
    df['序号'] = range(1, len(df) + 1)
    
    # 移除计算辅助列再编辑
    edit_df = df.drop(columns=['age'], errors='ignore')
    
    edited = st.data_editor(
        edit_df,
        num_rows="dynamic", use_container_width=True, height=450,
        column_config={
            "序号": st.column_config.NumberColumn(disabled=True),
            "价值": st.column_config.NumberColumn(format="￥%.2f"),
            "价格": st.column_config.NumberColumn(format="￥%.2f")
        },
        key="main_editor"
    )

    if st.button("💾 保存档案所有修改"):
        edited['序号'] = range(1, len(edited) + 1)
        edited.to_csv(path, index=False, encoding='utf-8-sig')
        st.success("✅ 数据已安全保存。统计看板已刷新。")
        time.sleep(1); st.rerun()

    st.divider()

    # --- 第四部分：树状视图 ---
    st.subheader("🌳 科室资产树状视图")
    depts = sorted(edited['科室'].dropna().unique().tolist())
    for d in depts:
        d_data = edited[edited['科室'] == d]
        with st.expander(f"📁 {d} ({len(d_data)} 条)"):
            st.dataframe(d_data, use_container_width=True)
            if st.button(f"➕ 在 {d} 快速增行", key=f"add_{d}"):
                nr = pd.DataFrame([{"科室": d, "设备状态": "正常"}])
                sdf = pd.concat([edited, nr], ignore_index=True)
                sdf['序号'] = range(1, len(sdf) + 1)
                sdf.to_csv(path, index=False, encoding='utf-8-sig')
                st.rerun()
