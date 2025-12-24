import streamlit as st
import pandas as pd
import os
import time

def show_asset():
    # 注入高级 CSS：修复金额显示不全，强化点击交互
    st.markdown("""
        <style>
        /* 1. 修复看板金额显示：允许折行或缩小字体，确保不被截断 */
        [data-testid="stMetricValue"] {
            font-size: clamp(1.5rem, 2vw, 2.2rem) !important; 
            font-weight: 800 !important;
            white-space: nowrap !important;
        }
        
        /* 2. 强化表格内容：纯白文字，解决朦胧感 */
        div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
            color: #FFFFFF !important; 
            font-size: 0.95rem !important;
            white-space: normal !important; 
            word-break: break-all !important;
        }

        /* 3. 看板配色：点击感强化 */
        .main-stat [data-testid="stMetricValue"] { color: #38BDF8 !important; }
        .age-stat-5 [data-testid="stMetricValue"] { color: #38BDF8; cursor: pointer; }
        .age-stat-7 [data-testid="stMetricValue"] { color: #FACC15; cursor: pointer; }
        .age-stat-10 [data-testid="stMetricValue"] { color: #FB923C; cursor: pointer; }
        .age-stat-13 [data-testid="stMetricValue"] { color: #F87171; cursor: pointer; }
        
        [data-testid="stTable"] { background-color: #111827 !important; border: 1px solid #374151 !important; }
        </style>
    """, unsafe_allow_html=True)

    st.header("📊 医疗装备综合资产档案")
    path = "data/equipment.csv"
    
    if not os.path.exists(path):
        st.error("❌ 数据未初始化。请前往『后台管理』->『🚀 资产导入』点击同步。")
        return

    # 安全读取数据
    df = pd.read_csv(path, encoding='utf-8-sig')
    
    # 核心：年限计算 (基准2025年)
    curr_yr = 2025
    def calc_age(row):
        try:
            val = str(row['出厂日期'])
            year = int(val[:4]) 
            return curr_yr - year
        except: return 0
    df['age_years'] = df.apply(calc_age, axis=1)

    # --- 第一部分：综合统计看板 ---
    st.subheader("📈 资产数据实时统计")
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        total_val = pd.to_numeric(df['价值'], errors='coerce').sum()
        st.markdown('<div class="main-stat">', unsafe_allow_html=True)
        st.metric("资产总价值", f"￥{total_val:,.2f}") # 增加了逗号分隔和完整位显示
        st.markdown('</div>', unsafe_allow_html=True)
        
    with m2:
        total_qty = pd.to_numeric(df['数量'], errors='coerce').sum()
        st.metric("资产总数量", f"{int(total_qty) if not pd.isna(total_qty) else 0} 台/套")
        
    with m3:
        st.metric("在管科室数", f"{df['科室'].dropna().nunique()} 个")
        
    with m4:
        incomplete = df.drop(columns=['age_years'], errors='ignore').isnull().any(axis=1).sum()
        st.metric("未完善数据量", f"{incomplete} 条")

    st.divider()

    # --- 第二部分：年限统计看板 (支持点击筛选) ---
    st.subheader("⚠️ 关键年限统计 (点击数字可筛选下方列表)")
    
    # 使用 session_state 来存储当前点击的年限筛选条件
    if 'age_filter' not in st.session_state:
        st.session_state.age_filter = 0

    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        count_5 = len(df[df['age_years'] >= 5])
        if st.button(f"5年以上: {count_5}", key="btn_5"): st.session_state.age_filter = 5
    with c2:
        count_7 = len(df[df['age_years'] >= 7])
        if st.button(f"7年以上: {count_7}", key="btn_7"): st.session_state.age_filter = 7
    with c3:
        count_10 = len(df[df['age_years'] >= 10])
        if st.button(f"10年以上: {count_10}", key="btn_10"): st.session_state.age_filter = 10
    with c4:
        count_13 = len(df[df['age_years'] >= 13])
        if st.button(f"13年以上: {count_13}", key="btn_13"): st.session_state.age_filter = 13

    # 重置筛选按钮
    if st.session_state.age_filter > 0:
        if st.button(f"❌ 清除 {st.session_state.age_filter} 年以上筛选，显示全部"):
            st.session_state.age_filter = 0
            st.rerun()

    st.divider()

    # --- 第三部分：数据维护总表 (应用筛选) ---
    st.subheader("⌨️ 数据维护总表")
    
    # 应用年限筛选
    display_df = df.copy()
    if st.session_state.age_filter > 0:
        display_df = display_df[display_df['age_years'] >= st.session_state.age_filter]
        st.warning(f"🔍 当前正在查看：{st.session_state.age_filter} 年及以上的设备明细")

    display_df['序号'] = range(1, len(display_df) + 1)
    edit_ready = display_df.drop(columns=['age_years'], errors='ignore')
    
    edited = st.data_editor(
        edit_ready,
        num_rows="dynamic", use_container_width=True, height=450,
        column_config={
            "序号": st.column_config.NumberColumn(disabled=True),
            "价值": st.column_config.NumberColumn(format="￥%.2f"),
            "价格": st.column_config.NumberColumn(format="￥%.2f")
        },
        key="main_editor"
    )

    if st.button("💾 保存档案所有修改"):
        # 注意：保存时需要同步回原 CSV，不能只保存筛选后的
        # 这里逻辑是：如果是筛选状态，我们建议用户先清除筛选再大规模修改，或者合并保存
        if st.session_state.age_filter > 0:
            st.error("⚠️ 请在清除筛选状态下进行全局保存，以确保数据完整性。")
        else:
            edited['序号'] = range(1, len(edited) + 1)
            edited.to_csv(path, index=False, encoding='utf-8-sig')
            st.success("✅ 数据已保存。")
            time.sleep(1); st.rerun()

    # --- 第四部分：树状视图 ---
    st.subheader("🌳 科室资产树状视图")
    depts = sorted(edit_ready['科室'].dropna().unique().tolist())
    for d in depts:
        d_data = edit_ready[edit_ready['科室'] == d]
        with st.expander(f"📁 {d} ({len(d_data)} 条)"):
            st.dataframe(d_data, use_container_width=True)
