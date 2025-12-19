import streamlit as st
import pandas as pd
import os

# --- 1. 初始化配置与文件检查 ---
DATA_DIR = "data"
ASSET_FILE = os.path.join(DATA_DIR, "equipment.csv")
# 模拟 GB/T 14885-2022 基础分类字典 (建议后续您可以扩充这个列表)
GBT_DICT = {
    "关键词": ["呼吸机", "监护仪", "除颤仪", "显微镜", "超声", "CT", "磁共振", "心电图"],
    "分类代码": ["060101", "060205", "060102", "050102", "050201", "050103", "050104", "050301"],
    "分类名称": ["治疗急救设备", "监护设备", "手术室设备", "显微镜设备", "超声诊断设备", "X射线影像设备", "磁共振影像设备", "心电诊断设备"]
}

def init_system():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(ASSET_FILE):
        # 初始化表头 (参考主任提供的图2)
        df = pd.DataFrame(columns=['资产名称', '规格型号', '分类代码', '所属科室', '状态', '登记日期'])
        df.to_csv(ASSET_FILE, index=False, encoding='utf-8-sig')

init_system()

# --- 2. 核心逻辑函数 ---
def get_auto_code(name):
    """根据输入的名称自动识别代码"""
    for i, keyword in enumerate(GBT_DICT["关键词"]):
        if keyword in name:
            return GBT_DICT["分类代码"][i], GBT_DICT["分类名称"][i]
    return "000000", "其他未分类"

def load_data():
    return pd.read_csv(ASSET_FILE)

# --- 3. 界面布局 ---
st.set_page_config(page_title="梅州三院医疗装备管理", layout="wide")

# 侧边栏
st.sidebar.title("🏥 装备部管理系统")
menu = ["资产登记", "资产台账查询", "分类代码字典"]
choice = st.sidebar.selectbox("功能切换", menu)

if choice == "资产登记":
    st.header("📝 新增资产登记")
    st.info("系统已接入 GB/T 14885-2022 分类代码自动识别引擎")
    
    with st.form("add_asset_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            asset_name = st.text_input("资产名称 (输入关键词自动识别代码)")
            spec = st.text_input("规格型号")
        with col2:
            dept = st.selectbox("使用科室", ["ICU", "手术室", "急诊科", "放射科", "内科", "外科"])
            status = st.selectbox("设备状态", ["在用", "备用", "维修中", "待报废"])

        # 实时识别显示
        code, cat_name = get_auto_code(asset_name) if asset_name else ("", "")
        st.write(f"🏷️ **自动匹配结果**：分类代码 `{code}` | 类别 `{cat_name}`")
        
        submit = st.form_submit_button("确认登记")
        if submit:
            if not asset_name:
                st.error("请输入资产名称！")
            else:
                new_data = {
                    '资产名称': asset_name,
                    '规格型号': spec,
                    '分类代码': code,
                    '所属科室': dept,
                    '状态': status,
                    '登记日期': pd.Timestamp.now().strftime('%Y-%m-%d')
                }
                df = load_data()
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                df.to_csv(ASSET_FILE, index=False, encoding='utf-8-sig')
                st.success(f"✅ {asset_name} 登记成功！代码已存入数据库。")

elif choice == "资产台账查询":
    st.header("📊 全院资产台账")
    df = load_data()
    
    # 简单的搜索功能
    search = st.text_input("🔍 搜索设备或科室")
    if search:
        df = df[df.apply(lambda row: search in str(row.values), axis=1)]
    
    st.dataframe(df, use_container_width=True)
    
    # 导出功能
    csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button("📥 下载当前台账(CSV)", data=csv, file_name="asset_export.csv", mime="text/csv")

elif choice == "分类代码字典":
    st.header("📖 GB/T 14885-2022 基础分类参考")
    st.table(pd.DataFrame(GBT_DICT))
