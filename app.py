import streamlit as st
import pandas as pd
import re
import os
from collections import Counter
import folium
from streamlit_folium import st_folium
import requests  # 新增：用于请求 GitHub 上的分章节文档

# -------------------------- 1. 初始化配置（关键：GitHub 文档链接 + 地点设置） --------------------------
# GitHub 分章节文档基础路径（替换为你的 GitHub 仓库实际路径，需用 raw 格式链接）
# 格式说明：https://raw.githubusercontent.com/[你的GitHub用户名]/[仓库名]/[分支名]/rulinwaishi/articles/chxx.txt
GITHUB_ARTICLE_BASE_URL = "https://raw.githubusercontent.com/你的GitHub用户名/你的仓库名/main/rulinwaishi/articles/ch"
# 需统计的5个地点（作业指定：南京、苏州、杭州、北京、扬州）
TARGET_LOCATIONS = ["南京", "苏州", "杭州", "北京", "扬州"]
# 对应地点的 CHGIS 坐标（适配 QGIS 与地图可视化，从 CHGIS 数据提取）
LOCATION_COORDS = {
    "南京": (32.0603, 118.7969),    # 明清江宁府
    "苏州": (31.2993, 120.6195),    # 明清苏州府
    "杭州": (30.2500, 120.1689),    # 明清杭州府
    "北京": (39.9042, 116.4074),    # 明清顺天府
    "扬州": (32.3897, 119.4129)     # 明清扬州府
}
# 本地/远程 QGIS 相关文件路径（QGIS 项目文件建议也上传 GitHub，用 raw 链接）
QGIS_PROJECT_GITHUB_URL = "https://raw.githubusercontent.com/你的GitHub用户名/你的仓库名/main/QGIS_Projects/rulin_waishi_gis.qgz"
QGIS_MAP_IMAGE_GITHUB_URL = "https://raw.githubusercontent.com/你的GitHub用户名/你的仓库名/main/QGIS_Projects/location_frequency_map.png"


# -------------------------- 2. 核心函数：从 GitHub 读取 ch10-ch30 文档 + 地点统计 --------------------------
def fetch_github_chapter(chapter_num):
    """根据章节号，从 GitHub 读取对应的 chxx.txt 文档内容"""
    # 拼接完整 GitHub raw 链接（如 ch10.txt → .../ch10.txt）
    github_url = f"{GITHUB_ARTICLE_BASE_URL}{chapter_num}.txt"
    try:
        # 发送请求获取文档内容（超时设为10秒，避免网络问题卡死）
        response = requests.get(github_url, timeout=10)
        response.raise_for_status()  # 若链接无效（404/500），抛出异常
        # 处理编码：优先用 UTF-8，若乱码则尝试 GBK（中文文档常见编码）
        if "charset" in response.headers:
            encoding = response.headers["charset"]
        else:
            encoding = "utf-8" if "�" not in response.text else "gbk"
        return response.text.encode(response.encoding).decode(encoding)
    except requests.exceptions.HTTPError as e:
        st.warning(f"章节 {chapter_num} 文档未找到（GitHub 链接无效）：{e}")
        return ""
    except requests.exceptions.Timeout:
        st.error(f"章节 {chapter_num} 读取超时，请检查网络连接！")
        return ""
    except Exception as e:
        st.error(f"章节 {chapter_num} 读取失败：{str(e)}")
        return ""


def extract_chapters_10_to_30_from_github():
    """批量读取 GitHub 上的 ch10.txt 至 ch30.txt，整合为完整文本"""
    target_chapters_text = ""
    # 遍历 10-30 章，逐个读取并拼接
    for chapter_num in range(10, 31):
        st.spinner(f"正在读取 GitHub 上的 ch{chapter_num}.txt...")
        chapter_content = fetch_github_chapter(chapter_num)
        if chapter_content:
            # 为每章添加标识，便于后续追溯
            target_chapters_text += f"=== 第{chapter_num}章 ===\n{chapter_content}\n\n"
    # 检查是否成功读取到内容
    if not target_chapters_text:
        st.warning("未从 GitHub 读取到任何章节内容！请检查 GITHUB_ARTICLE_BASE_URL 是否正确。")
    return target_chapters_text


def count_location_frequency(text, target_locations):
    """统计目标地点在文本中的出现频率（复用原逻辑，适配分章节文本）"""
    if not text:
        return pd.DataFrame(columns=["地点", "出现频率", "经度", "纬度"])
    
    location_counter = Counter()
    # 遍历每个地点，用正则精准匹配（避免匹配包含该地点的其他词汇）
    for location in target_locations:
        pattern = re.compile(re.escape(location), re.IGNORECASE | re.DOTALL)
        count = len(pattern.findall(text))
        location_counter[location] = count
    
    # 转换为 DataFrame，添加 CHGIS 坐标（供 QGIS 使用）
    frequency_data = []
    for location in target_locations:
        freq = location_counter[location]
        lon, lat = LOCATION_COORDS.get(location, (0.0, 0.0))
        frequency_data.append([location, freq, lon, lat])
    
    return pd.DataFrame(frequency_data, columns=["地点", "出现频率", "经度", "纬度"])


# -------------------------- 3. Streamlit 页面布局与交互逻辑 --------------------------
def main():
    st.title("《儒林外史》ch10-ch30 地点分析（GitHub 文档 + QGIS 可视化）")
    st.markdown("### 作业二功能：GitHub 分章节读取 + 地点统计 + QGIS 地理集成")

    # 侧边栏：显示关键配置与操作提示
    with st.sidebar:
        st.subheader("GitHub 配置检查")
        st.markdown(f"**分章节文档基础链接**：\n`{GITHUB_ARTICLE_BASE_URL}xx.txt`")
        st.markdown(f"**QGIS 项目 GitHub 链接**：\n`{QGIS_PROJECT_GITHUB_URL}`")
        st.warning("若无法读取文档，请确认：1. GitHub 仓库为公开；2. 链接路径（用户名/仓库名/分支）正确；3. 文档命名为 ch10.txt-ch30.txt。")


    # -------------------------- 步骤1：从 GitHub 读取 ch10-ch30 文本 --------------------------
    st.subheader("步骤1：读取 GitHub 分章节文档")
    if st.button("开始读取 ch10.txt - ch30.txt"):
        with st.spinner("正在批量读取 GitHub 上的 21 个章节文档..."):
            chapter_text = extract_chapters_10_to_30_from_github()
            if chapter_text:
                # 显示前 800 字符预览（分章节文本较长，控制预览长度）
                st.success("所有章节读取成功！以下为文本预览（前800字符）：")
                st.text_area("ch10-ch30 文本预览", chapter_text[:800] + "...", height=250)
                # 存储文本到 session_state，避免后续重复请求 GitHub
                st.session_state["chapter_text"] = chapter_text
            else:
                st.error("章节读取失败，请检查 GitHub 链接或网络！")


    # -------------------------- 步骤2：统计地点频率并生成 QGIS 可用数据 --------------------------
    st.subheader("步骤2：地点出现频率统计（支持 QGIS 导入）")
    # 从 session_state 获取已读取的文本（避免重复请求 GitHub）
    chapter_text = st.session_state.get("chapter_text", "")
    if not chapter_text and st.button("重新获取章节并统计频率"):
        chapter_text = extract_chapters_10_to_30_from_github()
        st.session_state["chapter_text"] = chapter_text
    
    if chapter_text:
        frequency_df = count_location_frequency(chapter_text, TARGET_LOCATIONS)
        # 展示频率表格（突出频率数值）
        st.dataframe(
            frequency_df,
            use_container_width=True,
            column_config={
                "出现频率": st.column_config.NumberColumn("出现频率（次）", format="%d"),
                "经度": st.column_config.NumberColumn("经度", format="%.4f"),
                "纬度": st.column_config.NumberColumn("纬度", format="%.4f")
            }
        )
        
        # 生成 CSV 文件（供 QGIS 直接导入关联 CHGIS 数据）
        csv_data = frequency_df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="下载地点频率 CSV（QGIS 数据关联用）",
            data=csv_data,
            file_name="儒林外史_ch10-ch30_地点频率.csv",
            mime="text/csv"
        )
    else:
        st.info("请先点击「开始读取 ch10.txt - ch30.txt」获取章节内容！")


    # -------------------------- 步骤3：QGIS 可视化集成（GitHub 远程文件） --------------------------
    st.subheader("步骤3：QGIS 地理可视化展示")
    st.markdown("#### 3.1 QGIS 生成的频率地图（GitHub 托管）")
    # 尝试加载 GitHub 上的 QGIS 地图图片
    try:
        response = requests.get(QGIS_MAP_IMAGE_GITHUB_URL, timeout=8)
        response.raise_for_status()
        # 直接在 Streamlit 中显示远程图片
        st.image(
            response.content,
            caption="QGIS 制作：地点出现频率地图（颜色越深频率越高）",
            use_container_width=True
        )
    except Exception as e:
        st.warning(f"无法加载 QGIS 地图图片：{str(e)}")
        st.markdown(f"请手动访问链接查看：[QGIS 频率地图]({QGIS_MAP_IMAGE_GITHUB_URL})")

    # 展示基础交互地图（基于 CHGIS 坐标，辅助验证 QGIS 数据）
    st.markdown("#### 3.2 基础交互地图（与 QGIS 坐标一致）")
    if chapter_text:
        m = folium.Map(location=[32.0603, 118.7969], zoom_start=8, tiles="CartoDB positron")
        # 为每个地点添加气泡标记（大小对应频率）
        for _, row in frequency_df.iterrows():
            location = row["地点"]
            freq = row["出现频率"]
            lon, lat = row["经度"], row["纬度"]
            if lon != 0 and lat != 0:
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=freq * 6 if freq > 0 else 4,  # 频率越大，气泡越大
                    color="#d35400",
                    fill=True,
                    fill_color="#d35400",
                    fill_opacity=0.8,
                    popup=f"<b>{location}</b><br>出现频率：{freq}次<br>坐标：({lat:.4f}, {lon:.4f})"
                ).add_to(m)
        st_folium(m, width=700, height=450)

    # 提供 QGIS 项目文件下载（从 GitHub 直接获取）
    st.markdown("#### 3.3 QGIS 项目文件（完整地理处理逻辑）")
    st.download_button(
        label="下载 QGIS 项目文件（.qgz）",
        data=requests.get(QGIS_PROJECT_GITHUB_URL).content,
        file_name="儒林外史_ch10-ch30_地点分析.qgz",
        mime="application/octet-stream"
    )


    # -------------------------- 步骤4：作业要求补充（研究问题 + 公开链接） --------------------------
    st.subheader("步骤4：作业规范补充")
    st.markdown("""
    1. **核心研究问题**：  
       - 问题1：《儒林外史》ch10-ch30 中，5个目标地点的出现频率排序如何？  
       - 问题2：高频地点（如扬州、南京）是否与小说中学者的核心活动场景高度重合？  
    2. **QGIS 操作流程（关键步骤）**：  
       ① 下载本页面的「地点频率 CSV」；  
       ② 打开 QGIS → 导入 CSV（选择“经度/纬度”为坐标字段）；  
       ③ 加载 CHGIS 明清政区矢量数据（如 chgis_v6_admin1.shp）；  
       ④ 通过「属性表 → 连接」功能，将 CSV 与 CHGIS 数据关联；  
       ⑤ 对关联图层设置「分级渲染」（按“出现频率”字段），导出地图图片并上传 GitHub。  
    3. **公开数据链接（作业要求）**：  
       - 分章节原文：[GitHub articles 文件夹](https://github.com/你的GitHub用户名/你的仓库名/tree/main/rulinwaishi/articles)  
       - QGIS 项目与地图：[GitHub QGIS_Projects 文件夹](https://github.com/你的GitHub用户名/你的仓库名/tree/main/QGIS_Projects)  
    """)


if __name__ == "__main__":
    main()
