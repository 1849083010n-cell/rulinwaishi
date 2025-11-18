import streamlit as st
import pandas as pd
import re
import os
from collections import Counter
import folium  # 辅助显示基础地图，衔接QGIS结果
from streamlit_folium import st_folium

# -------------------------- 1. 初始化配置（需根据本地环境修改） --------------------------
# 本地《儒林外史》TXT文档路径（请替换为你的实际文件路径）
LOCAL_RULIN_FILE = r"E:\Documents\儒林外史_全文.txt"  # Windows示例，macOS/Linux格式："/Users/xxx/儒林外史_全文.txt"
# 需统计的5个地点（作业指定：南京、苏州、杭州、北京、扬州）
TARGET_LOCATIONS = ["南京", "苏州", "杭州", "北京", "扬州"]
# 对应地点的CHGIS坐标（经纬度，适配QGIS与地图可视化，可从CHGIS数据中提取）
LOCATION_COORDS = {
    "南京": (32.0603, 118.7969),    # 明清江宁府坐标
    "苏州": (31.2993, 120.6195),    # 明清苏州府坐标
    "杭州": (30.2500, 120.1689),    # 明清杭州府坐标
    "北京": (39.9042, 116.4074),    # 明清顺天府坐标
    "扬州": (32.3897, 119.4129)     # 明清扬州府坐标
}
# 本地QGIS项目文件路径（用于展示与下载，需替换为你的实际路径）
QGIS_PROJECT_PATH = r"E:\QGIS_Projects\rulin_waishi_gis.qgz"
# QGIS导出的地点频率地图图片路径（用于Streamlit展示）
QGIS_MAP_IMAGE = r"E:\QGIS_Projects\location_frequency_map.png"


# -------------------------- 2. 核心函数：读取本地文档+统计10-30章地点频率 --------------------------
def extract_chapters_10_to_30(file_path):
    """读取本地《儒林外史》TXT，提取10-30章文本内容"""
    if not os.path.exists(file_path):
        st.error(f"本地文档未找到！请检查路径：{file_path}")
        return ""
    
    # 读取文档（假设章节以"第X章"开头，需根据你的文档格式调整匹配规则）
    with open(file_path, "r", encoding="utf-8") as f:
        full_text = f.read()
    
    # 正则匹配"第10章"到"第30章"的内容（需根据文档实际章节格式微调，如"第十回"需改为r"第[十拾]{1,2}回"）
    chapter_pattern = r"第(\d+)章.*?(?=第(\d+)章|$)"  # 匹配"第X章"开头，到下一章或文档结束
    chapters = re.findall(chapter_pattern, full_text, re.DOTALL)
    
    # 筛选10-30章内容
    target_chapters_text = ""
    for chapter in chapters:
        try:
            chapter_num = int(chapter[0])
            if 10 <= chapter_num <= 30:
                # 重新匹配该章节的完整内容（避免漏取）
                chapter_full_pattern = re.compile(f"第{chapter_num}章.*?(?=第({chapter_num + 1}|$)章|$)", re.DOTALL)
                chapter_content = chapter_full_pattern.search(full_text).group()
                target_chapters_text += chapter_content + "\n\n"
        except (ValueError, AttributeError):
            continue
    
    if not target_chapters_text:
        st.warning("未提取到10-30章内容！请检查文档章节格式（如是否为'第X回'而非'第X章'）")
    return target_chapters_text


def count_location_frequency(text, target_locations):
    """统计目标地点在文本中的出现频率"""
    if not text:
        return pd.DataFrame(columns=["地点", "出现频率", "经度", "纬度"])
    
    # 初始化计数器
    location_counter = Counter()
    # 遍历每个地点，统计出现次数（不区分全角/半角，忽略大小写）
    for location in target_locations:
        # 正则匹配地点，允许前后有非文字字符（如标点、空格），避免匹配包含该地点的其他词
        pattern = re.compile(re.escape(location), re.IGNORECASE)
        count = len(pattern.findall(text))
        location_counter[location] = count
    
    # 转换为DataFrame，添加坐标
    frequency_data = []
    for location in target_locations:
        freq = location_counter[location]
        lon, lat = LOCATION_COORDS.get(location, (0.0, 0.0))  # 若坐标缺失，默认(0,0)
        frequency_data.append([location, freq, lon, lat])
    
    return pd.DataFrame(frequency_data, columns=["地点", "出现频率", "经度", "纬度"])


# -------------------------- 3. Streamlit页面布局与交互逻辑 --------------------------
def main():
    st.title("《儒林外史》10-30章地点频率分析与QGIS可视化")
    st.markdown("### 作业二核心功能：本地文档读取 + 地点统计 + QGIS地理集成")

    # 侧边栏：显示配置信息与操作提示
    with st.sidebar:
        st.subheader("配置提示")
        st.markdown(f"1. 本地文档路径：\n`{LOCAL_RULIN_FILE}`")
        st.markdown(f"2. QGIS项目路径：\n`{QGIS_PROJECT_PATH}`")
        st.warning("若文件路径错误，请修改代码中「初始化配置」部分的路径参数！")


    # -------------------------- 步骤1：读取并展示10-30章文本（可选） --------------------------
    st.subheader("步骤1：提取10-30章文本")
    if st.button("读取本地《儒林外史》10-30章"):
        with st.spinner("正在读取文档并提取章节..."):
            chapter_text = extract_chapters_10_to_30(LOCAL_RULIN_FILE)
            if chapter_text:
                # 显示前500字符预览（避免文本过长）
                st.success("章节提取成功！以下为文本预览（前500字符）：")
                st.text_area("10-30章文本预览", chapter_text[:500] + "...", height=200)
            else:
                st.error("章节提取失败，请检查文档格式或路径！")


    # -------------------------- 步骤2：统计地点频率并展示 --------------------------
    st.subheader("步骤2：地点出现频率统计")
    chapter_text = extract_chapters_10_to_30(LOCAL_RULIN_FILE)  # 重新获取文本（确保最新）
    frequency_df = count_location_frequency(chapter_text, TARGET_LOCATIONS)
    
    # 展示频率表格
    st.dataframe(frequency_df, use_container_width=True, 
                 column_config={"出现频率": st.column_config.NumberColumn("出现频率", format="%d次")})
    
    # 下载频率数据（CSV格式，用于QGIS导入）
    csv_data = frequency_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="下载地点频率CSV（用于QGIS数据关联）",
        data=csv_data,
        file_name="儒林外史_10-30章_地点频率.csv",
        mime="text/csv"
    )


    # -------------------------- 步骤3：QGIS集成与可视化展示 --------------------------
    st.subheader("步骤3：QGIS地理可视化集成")
    st.markdown("#### 3.1 QGIS地图预览（已导出图片）")
    # 展示QGIS生成的频率地图
    if os.path.exists(QGIS_MAP_IMAGE):
        st.image(QGIS_MAP_IMAGE, caption="QGIS制作：《儒林外史》地点频率地图（颜色越深频率越高）", use_container_width=True)
    else:
        st.warning(f"QGIS地图图片未找到！请检查路径：{QGIS_MAP_IMAGE}")
    
    # 展示基础交互地图（衔接QGIS坐标，辅助查看）
    st.markdown("#### 3.2 基础交互地图（基于CHGIS坐标）")
    # 创建folium地图（中心设为南京，缩放级别8）
    m = folium.Map(location=[32.0603, 118.7969], zoom_start=8, tiles="CartoDB positron")
    # 为每个地点添加标记（气泡大小对应频率）
    for _, row in frequency_df.iterrows():
        location = row["地点"]
        freq = row["出现频率"]
        lon, lat = row["经度"], row["纬度"]
        if lon != 0 and lat != 0:  # 仅添加有坐标的地点
            # 气泡大小：频率×5（避免过小）
            folium.CircleMarker(
                location=[lat, lon],
                radius=freq * 5 if freq > 0 else 3,  # 频率为0时显示最小气泡
                color="#e74c3c",
                fill=True,
                fill_color="#e74c3c",
                fill_opacity=0.7,
                popup=f"<b>{location}</b><br>出现频率：{freq}次"
            ).add_to(m)
    # 在Streamlit中显示地图
    st_folium(m, width=700, height=400)

    # QGIS项目文件下载（供查看完整地理处理逻辑）
    st.markdown("#### 3.3 QGIS项目文件下载")
    if os.path.exists(QGIS_PROJECT_PATH):
        with open(QGIS_PROJECT_PATH, "rb") as f:
            st.download_button(
                label="下载QGIS项目文件（.qgz）",
                data=f,
                file_name="儒林外史_地点分析.qgz",
                mime="application/octet-stream"
            )
    else:
        st.error(f"QGIS项目文件未找到！请检查路径：{QGIS_PROJECT_PATH}")


    # -------------------------- 步骤4：作业要求补充（反思与链接） --------------------------
    st.subheader("步骤4：作业要求补充")
    st.markdown("""
    1. **研究问题**：  
       - 问题1：《儒林外史》10-30章中，哪个地点的学者活动频率最高？  
       - 问题2：地点出现频率与小说中该地区的文化地位是否相关？  
    2. **方法与工具**：  
       - 文本处理：本地TXT读取 + Python正则提取（10-30章）  
       - 频率统计：Python Counter + Pandas数据整理  
       - GIS可视化：QGIS（CHGIS数据关联 + 分级渲染） + Streamlit展示  
    3. **结果反思**：  
       - 需结合小说内容分析频率差异（如“扬州”高频可能与盐商文化、文人聚集相关）  
       - QGIS可视化优势：可直观对比不同地点的空间分布与频率关系  
    """)

    # 公开链接提示（需替换为你的GitHub/OneDrive链接）
    st.markdown("""
    > **公开数据链接**（作业要求）：  
    > - 原始文本与频率数据：[GitHub仓库](https://github.com/你的用户名/你的仓库名)  
    > - QGIS项目与地图文件：[OneDrive链接](https://1drv.ms/u/s!你的链接)  
    """)


if __name__ == "__main__":
    main()
