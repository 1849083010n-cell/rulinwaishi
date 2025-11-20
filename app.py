import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 页面配置
st.set_page_config(page_title="《儒林外史》GIS 地图", layout="wide")

st.title("📍 《儒林外史》（第10-30回）空间分析")
st.markdown("""
此交互式地图可视化了《儒林外史》第 10 至 30 回中提到的五个关键地点的频率和重要性。
圆圈的大小代表叙事焦点的相对频率/强度。
""")

# 2. 数据准备
# 坐标和估计频率（叙事权重）基于对第 10-30 回的细读
data = {
    "City": ["Huzhou (湖州)", "Hangzhou (杭州)", "Yangzhou (扬州)", "Nanjing (南京)", "Beijing (北京)"],
    "Lat": [30.893, 30.274, 32.394, 32.060, 39.904],
    "Lon": [120.086, 120.155, 119.412, 118.796, 116.407],
    "Frequency": [4, 7, 3, 7, 2],  # 叙事权重（活跃章节数）
    "Key_Characters": [
        "娄氏兄弟, 杨执中",
        "马二先生, 匡超人",
        "牛玉圃, 万雪斋",
        "杜慎卿, 鲍文卿",
        "匡超人, 鲁编修"
    ],
    "Activity": [
        "莺脰湖盛会；寻访隐士",
        "西湖诗会；图书出版；非法诉讼",
        "盐商宴席；招摇撞骗",
        "莫愁湖梨园大会；戏曲文化",
        "科举考试；政治攀附"
    ]
}

df = pd.DataFrame(data)

# 3. 布局 - 分为地图和分析
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("地理分布")
    
    # 创建地图，以华东为中心
    m = folium.Map(location=[34.0, 118.0], zoom_start=5)

    # 向地图添加点
    for index, row in df.iterrows():
        # 创建带有详细信息的弹出窗口
        popup_html = f"""
        <b>{row['City']}</b><br>
        <b>关键人物:</b> {row['Key_Characters']}<br>
        <b>关键事件:</b> {row['Activity']}
        """
        
        folium.CircleMarker(
            location=[row['Lat'], row['Lon']],
            radius=row['Frequency'] * 3,  # 根据频率缩放半径
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row['City'],
            color="crimson",
            fill=True,
            fill_color="crimson",
            fill_opacity=0.6
        ).add_to(m)

    # 渲染地图
    st_folium(m, width=700, height=500)

with col2:
    st.subheader("对比见解")
    
    tab1, tab2, tab3 = st.tabs(["雅集聚会", "商业化", "道德观"])
    
    with tab1:
        st.write("**湖州 vs. 南京**")
        st.info("""
        **湖州 (第 11-12 回):** 娄氏兄弟主持 *莺脰湖* 之会。这是理想主义和政治天真的，旨在寻求“隐逸之才”。
        
        **南京 (第 30 回):** 杜慎卿主持 *莫愁湖* 之会。这是唯美和颓废的，专注于优伶戏子而非道德哲学。
        """)
        
    with tab2:
        st.write("**杭州 vs. 扬州**")
        st.info("""
        **杭州 (第 14-18 回):** 文学即商品。马二先生为了钱选评试卷。
        
        **扬州 (第 22-23 回):** 文化即奢侈品。盐商通过结交（假）学者如牛玉圃来购买声望。
        """)
        
    with tab3:
        st.write("**北京的角色**")
        st.info("""
        北京作为行动场景出现的频率较低，但充当了**腐败的终点站**。
        
        匡超人前往那里（第 20 回）以巩固地位，抛弃了传统道德（和妻子），入赘权贵之家。
        """)

# 4. 数据表显示
st.markdown("### 详细数据源")
st.dataframe(df)
