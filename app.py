import streamlit as st
import pandas as pd
import re
from collections import Counter
import requests  # 用于请求 GitHub 上的分章节文档

# -------------------------- 1. 初始化配置（已嵌入你的 GitHub 用户名与仓库名） --------------------------
GITHUB_ARTICLE_BASE_URL = "https://raw.githubusercontent.com/1849083010n-cell/rulinwaishi/main/rulinwaishi/articles/ch"
TARGET_LOCATIONS = ["南京", "苏州", "杭州", "北京", "扬州"]
LOCATION_COORDS = {
    "南京": (32.0603, 118.7969),
    "苏州": (31.2993, 120.6195),
    "杭州": (30.2500, 120.1689),
    "北京": (39.9042, 116.4074),
    "扬州": (32.3897, 119.4129)
}
QGIS_PROJECT_GITHUB_URL = "https://raw.githubusercontent.com/1849083010n-cell/rulinwaishi/main/QGIS_Projects/rulin_waishi_gis.qgz"
QGIS_MAP_IMAGE_GITHUB_URL = "https://raw.githubusercontent.com/1849083010n-cell/rulinwaishi/main/QGIS_Projects/location_frequency_map.png"


# -------------------------- 2. 核心函数（移除 folium 相关代码） --------------------------
def fetch_github_chapter(chapter_num):
    github_url = f"{GITHUB_ARTICLE_BASE_URL}{chapter_num}.txt"
    try:
        response = requests.get(github_url, timeout=10)
        response.raise_for_status()
        encoding = response.headers.get("charset", "utf-8")
        if "�" in response.text:
            encoding = "gbk"
        return response.text.encode(response.encoding).decode(encoding)
    except requests.exceptions.HTTPError as e:
        st.warning(f"章节 {chapter_num} 未找到：{e}")
        return ""
    except Exception as e:
        st.error(f"章节 {chapter_num} 读取失败：{str(e)}")
        return ""


def extract_chapters_10_to_30_from_github():
    target_chapters_text = ""
    for chapter_num in range(10, 31):
        with st.spinner(f"读取 ch{chapter_num}.txt..."):
            chapter_content = fetch_github_chapter(chapter_num)
            if chapter_content:
                target_chapters_text += f"=== 第{chapter_num}章 ===\n{chapter_content}\n\n"
    if not target_chapters_text:
        st.warning("未读取到章节内容！请检查仓库是否公开、文档路径是否正确。")
    return target_chapters_text


def count_location_frequency(text, target_locations):
    if not text:
        return pd.DataFrame(columns=["地点", "出现频率", "经度", "纬度"])
    
    location_counter = Counter()
    for location in target_locations:
        pattern = re.compile(re.escape(location), re.IGNORECASE | re.DOTALL)
        location_counter[location] = len(pattern.findall(text))
    
    frequency_data = []
    for location in target_locations:
        freq = location_counter[location]
        lon, lat = LOCATION_COORDS.get(location, (0.0, 0.0))
        frequency_data.append([location, freq, lon, lat])
    
    return pd.DataFrame(frequency_data, columns=["地点", "出现频率", "经度", "纬度"])


# -------------------------- 3. Streamlit 页面（移除 folium 地图相关代码） --------------------------
def main():
    st.title("《儒林外史》ch10-ch30 地点分析（GitHub 文档 + QGIS 可视化）")
    st.markdown("### 作业二功能：读取 1849083010n-cell/rulinwaishi 仓库文档 + 地点统计 + QGIS 集成")

    # 侧边栏提示
    with st.sidebar:
        st.subheader("配置检查")
        st.markdown(f"用户名：1849083010n-cell\n仓库名：rulinwaishi")
        st.warning("读取失败请检查：1. 仓库公开 2. 文档命名为 ch10-ch30.txt 3. 分支为 main")


    # 步骤1：读取 GitHub 文档
    st.subheader("步骤1：读取 GitHub 分章节文档")
    if st.button("开始读取 ch10.txt - ch30.txt"):
        with st.spinner("批量读取 21 个章节..."):
            chapter_text = extract_chapters_10_to_30_from_github()
            if chapter_text:
                st.success("读取成功！文本预览（前800字符）：")
                st.text_area("ch10-ch30 预览", chapter_text[:800] + "...", height=250)
                st.session_state["chapter_text"] = chapter_text
            else:
                st.error("读取失败，请检查配置！")


    # 步骤2：统计地点频率
    st.subheader("步骤2：地点出现频率统计（QGIS 导入用）")
    chapter_text = st.session_state.get("chapter_text", "")
    if not chapter_text and st.button("重新获取并统计频率"):
        chapter_text = extract_chapters_10_to_30_from_github()
        st.session_state["chapter_text"] = chapter_text
    
    if chapter_text:
        frequency_df = count_location_frequency(chapter_text, TARGET_LOCATIONS)
        st.dataframe(
            frequency_df,
            use_container_width=True,
            column_config={
                "出现频率": st.column_config.NumberColumn("出现频率（次）", format="%d"),
                "经度": st.column_config.NumberColumn("经度", format="%.4f"),
                "纬度": st.column_config.NumberColumn("纬度", format="%.4f")
            }
        )
        
        # 下载 CSV（供 QGIS 使用）
        csv_data = frequency_df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="下载地点频率 CSV",
            data=csv_data,
            file_name="儒林外史_ch10-ch30_地点频率.csv",
            mime="text/csv"
        )
    else:
        st.info("请先读取章节内容！")


    # 步骤3：QGIS 可视化集成
    st.subheader("步骤3：QGIS 地理可视化展示")
    st.markdown("#### 3.1 QGIS 频率地图（GitHub 托管）")
    try:
        response = requests.get(QGIS_MAP_IMAGE_GITHUB_URL, timeout=8)
        response.raise_for_status()
        st.image(response.content, caption="QGIS 地点频率地图（颜色越深频率越高）", use_container_width=True)
    except Exception as e:
        st.warning("请将 QGIS 地图图片上传至 QGIS_Projects 文件夹，命名为 location_frequency_map.png")

    # QGIS 项目文件下载
    st.markdown("#### 3.2 下载 QGIS 项目文件")
    try:
        st.download_button(
            label="下载 QGIS 项目（.qgz）",
            data=requests.get(QGIS_PROJECT_GITHUB_URL).content,
            file_name="儒林外史_地点分析.qgz",
            mime="application/octet-stream"
        )
    except Exception as e:
        st.warning("请将 QGIS 项目文件上传至 QGIS_Projects 文件夹，命名为 rulin_waishi_gis.qgz")


    # 步骤4：作业要求补充
    st.subheader("步骤4：作业规范补充")
    st.markdown("""
    1. 研究问题：  
       - 问题1：ch10-ch30 中5个地点的频率排序？  
       - 问题2：高频地点是否与学者活动场景重合？  
    2. QGIS 操作：  
       ① 下载 CSV → ② 导入 QGIS 并关联 CHGIS 数据 → ③ 分级渲染频率 → ④ 导出地图  
    3. 公开链接：  
       - 原文：[rulinwaishi/articles](https://github.com/1849083010n-cell/rulinwaishi/tree/main/rulinwaishi/articles)  
       - QGIS 成果：[rulinwaishi/QGIS_Projects](https://github.com/1849083010n-cell/rulinwaishi/tree/main/QGIS_Projects)
    """)


if __name__ == "__main__":
    main()
