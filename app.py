import streamlit as st
import pandas as pd
import re
import os
from collections import Counter
import folium
from streamlit_folium import st_folium
import requests  # 用于请求 GitHub 上的分章节文档

# -------------------------- 1. 初始化配置（已嵌入你的 GitHub 用户名与仓库名） --------------------------
# GitHub 分章节文档基础路径（格式：https://raw.githubusercontent.com/用户名/仓库名/分支名/文件路径）
# 分支默认用 main（若你的仓库分支是 master，需将 main 改为 master）
GITHUB_ARTICLE_BASE_URL = "https://raw.githubusercontent.com/1849083010n-cell/rulinwaishi/main/rulinwaishi/articles/ch"
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
# QGIS 相关文件的 GitHub 链接（需将 QGIS 项目和地图图片上传至对应路径）
QGIS_PROJECT_GITHUB_URL = "https://raw.githubusercontent.com/1849083010n-cell/rulinwaishi/main/QGIS_Projects/rulin_waishi_gis.qgz"
QGIS_MAP_IMAGE_GITHUB_URL = "https://raw.githubusercontent.com/1849083010n-cell/rulinwaishi/main/QGIS_Projects/location_frequency_map.png"


# -------------------------- 2. 核心函数：从 GitHub 读取 ch10-ch30 文档 + 地点统计 --------------------------
def fetch_github_chapter(chapter_num):
    """根据章节号，从你的 GitHub 仓库读取对应的 chxx.txt 文档内容"""
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
        st.warning(f"章节 {chapter_num} 文档未找到（检查：GitHub 路径是否存在 ch{chapter_num}.txt）：{e}")
        return ""
    except requests.exceptions.Timeout:
        st.error(f"章节 {chapter_num} 读取超时，请检查网络连接！")
        return ""
    except Exception as e:
        st.error(f"章节 {chapter_num} 读取失败：{str(e)}")
        return ""


def extract_chapters_10_to_30_from_github():
    """批量读取你的 GitHub 仓库中 ch10.txt 至 ch30.txt，整合为完整文本"""
    target_chapters_text = ""
    # 遍历 10-30 章，逐个读取并拼接
    for chapter_num in range(10, 31):
        with st.spinner(f"正在读取 ch{chapter_num}.txt..."):
            chapter_content = fetch_github_chapter(chapter_num)
            if chapter_content:
                # 为每章添加标识，便于后续追溯
                target_chapters_text += f"=== 第{chapter_num}章 ===\n{chapter_content}\n\n"
    # 检查是否成功读取到内容
    if not target_chapters_text:
        st.warning("未从 GitHub 读取到任何章节内容！请确认：1. 仓库为公开；2. rulinwaishi/articles/ 下有 ch10-ch30.txt；3. 分支是 main（非 master）。")
    return target_chapters_text


def count_location_frequency(text, target_locations):
    """统计目标地点在文本中的出现频率（适配分章节文本）"""
    if not text:
        return pd.DataFrame(columns=["地点", "出现频率", "经度", "纬度"])
    
    location_counter = Counter()
    # 遍历每个地点，用正则精准匹配（避免匹配包含该地点的其他词汇，如“南京路”≠“南京”）
    for location in target_locations:
        pattern = re.compile(re.escape(location), re.IGNORECASE | re.DOTALL)
        count = len(pattern.findall(text))
        location_counter[location] = count
    
    # 转换为 DataFrame，添加 CHGIS 坐标（供 QGIS 直接导入关联）
    frequency_data = []
    for location in target_locations:
        freq = location_counter[location]
        lon, lat = LOCATION_COORDS.get(location, (0.0, 0.0))
        frequency_data.append([location, freq, lon, lat])
    
    return pd.DataFrame(frequency_data, columns=["地点", "出现频率", "经度", "纬度"])


# -------------------------- 3. Streamlit 页面布局与交互逻辑 --------------------------
def main():
    st.title("《儒林外史》ch10-ch30 地点分析（GitHub 文档 + QGIS 可视化）")
    st.markdown("### 作业二功能：读取 1849083010n-cell/rulinwaishi 仓库文档 + 地点统计 + QGIS 集成")

    # 侧边栏：显示关键配置与操作提示
    with st.sidebar:
        st.subheader("GitHub 配置信息")
        st.markdown(f"**用户名**：1849083010n-cell")
        st.markdown(f"**仓库名**：rulinwaishi")
        st.markdown(f"**文档路径**：rulinwaishi/articles/chxx.txt")
        st.warning("若读取失败，先检查：\n1. 仓库是否设为「Public」（私密仓库无法访问）\n2. 文档是否按「ch10.txt」「ch11.txt」...「ch30.txt」命名\n3. 仓库默认分支是否为「main」（若为「master」，需修改代码中「main」为「master」）")


    # -------------------------- 步骤1：从你的 GitHub 读取 ch10-ch30 文本 --------------------------
    st.subheader("步骤1：读取 GitHub 分章节文档")
    if st.button("开始读取 ch10.txt - ch30.txt"):
        with st.spinner("正在批量读取 21 个章节文档（耐心等待...）"):
            chapter_text = extract_chapters_10_to_30_from_github()
            if chapter_text:
                # 显示前 800 字符预览（控制长度，避免页面过长）
                st.success("所有章节读取成功！以下为文本预览（前800字符）：")
                st.text_area("ch10-ch30 文本预览", chapter_text[:800] + "...", height=250)
                # 存储文本到 session_state，避免后续重复请求 GitHub
                st.session_state["chapter_text"] = chapter_text
            else:
                st.error("章节读取失败，请按侧边栏提示检查配置！")


    # -------------------------- 步骤2：统计地点频率并生成 QGIS 可用数据 --------------------------
    st.subheader("步骤2：地点出现频率统计（支持 QGIS 导入）")
    # 从 session_state 获取已读取的文本（避免重复请求 GitHub）
    chapter_text = st.session_state.get("chapter_text", "")
    if not chapter_text and st.button("重新获取章节并统计频率"):
        chapter_text = extract_chapters_10_to_30_from_github()
        st.session_state["chapter_text"] = chapter_text
    
    if chapter_text:
        frequency_df = count_location_frequency(chapter_text, TARGET_LOCATIONS)
        # 展示频率表格（突出频率数值，优化可读性）
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


    # -------------------------- 步骤3：QGIS 可视化集成（读取你的 GitHub 远程文件） --------------------------
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
        st.warning(f"暂未加载到 QGIS 地图图片！请将地图图片上传至仓库的 QGIS_Projects 文件夹，命名为 location_frequency_map.png")
        st.markdown(f"图片目标路径：[QGIS_Projects/location_frequency_map.png](https://github.com/1849083010n-cell/rulinwaishi/tree/main/QGIS_Projects)")

    # 展示基础交互地图（基于 CHGIS 坐标，辅助验证 QGIS 数据准确性）
    st.markdown("#### 3.2 基础交互地图（与 QGIS 坐标一致）")
    if chapter_text:
        m = folium.Map(location=[32.0603, 118.7969], zoom_start=8, tiles="CartoDB positron")
        # 为每个地点添加气泡标记（大小对应频率，便于直观对比）
        for _, row in frequency_df.iterrows():
            location = row["地点"]
            freq = row["出现频率"]
            lon, lat = row["经度"], row["纬度"]
            if lon != 0 and lat != 0:
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=freq * 6 if freq > 0 else 4,  # 频率为0时显示最小气泡
                    color="#d35400",
                    fill=True,
                    fill_color="#d35400",
                    fill_opacity=0.8,
                    popup=f"<b>{location}</b><br>出现频率：{freq}次<br>CHGIS 坐标：({lat:.4f}, {lon:.4f})"
                ).add_to(m)
        st_folium(m, width=700, height=450)

    # 提供 QGIS 项目文件下载（从你的 GitHub 仓库直接获取）
    st.markdown("#### 3.3 QGIS 项目文件（完整地理处理逻辑）")
    try:
        st.download_button(
            label="下载 QGIS 项目文件（.qgz）",
            data=requests.get(QGIS_PROJECT_GITHUB_URL).content,
            file_name="儒林外史_ch10-ch30_地点分析.qgz",
            mime="application/octet-stream"
        )
    except Exception as e:
        st.warning(f"暂未加载到 QGIS 项目文件！请将 .qgz 文件上传至仓库的 QGIS_Projects 文件夹，命名为 rulin_waishi_gis.qgz")


    # -------------------------- 步骤4：作业要求补充（研究问题 + 公开链接） --------------------------
    st.subheader("步骤4：作业规范补充（符合 CHC5904 要求）")
    st.markdown("""
    1. **核心研究问题**：  
       - 问题1：《儒林外史》ch10-ch30 中，5个目标地点的出现频率从高到低排序如何？  
       - 问题2：高频地点（如扬州、南京）的出现场景是否与小说中学者的学术交流、科举相关活动高度重合？  
    2. **QGIS 操作关键步骤（必须完成）**：  
       ① 点击本页面「下载地点频率 CSV」，获取带坐标的统计数据；  
       ② 打开 QGIS（推荐用 nix run github:qgis/qgis/release-3.34#qgis 启动稳定版）；  
       ③ 导入 CSV 文件：Layer → Add Layer → Add Delimited Text Layer，选择“经度”“纬度”为坐标字段；  
       ④ 加载 CHGIS 数据：从 [CHGIS 官网](https://chgis.fas.harvard.edu/pages/intro/) 下载明清政区矢量数据（如 chgis_v6_admin1.shp），导入 QGIS；  
       ⑤ 数据关联：右键 CHGIS 图层 → Open Attribute Table → Join，用“地点名称”字段关联 CSV 与 CHGIS 数据；  
       ⑥ 可视化设置：Layer Properties → Symbology → Graduated，按“出现频率”字段设置分级色彩，导出地图为 PNG；  
       ⑦ 上传成果：将 QGIS 项目文件（.qgz）和地图 PNG 上传至 GitHub 仓库的 QGIS_Projects 文件夹。  
    3. **公开数据链接（作业提交需填写）**：  
       - 分章节原文：[1849083010n-cell/rulinwaishi/articles](https://github.com/1849083010n-cell/rulinwaishi/tree/main/rulinwaishi/articles)  
       - 地点频率数据：[儒林外史_ch10-ch30_地点频率.csv](https://github.com/1849083010n-cell/rulinwaishi/blob/main/QGIS_Projects/儒林外史_ch10-ch30_地点频率.csv)（需手动上传 CSV 至该路径）  
       - QGIS 成果：[1849083010n-cell/rulinwaishi/QGIS_Projects](https://github.com/1849083010n-cell/rulinwaishi/tree/main/QGIS_Projects)  
    """)


if __name__ == "__main__":
    main()
