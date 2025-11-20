import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 页面配置
st.set_page_config(page_title="《儒林外史》GIS 地图与章节导读", layout="wide")

st.title("🗺️ 《儒林外史》（第10-30回）文学地理志")
st.markdown("""
本应用结合了**地理空间分析**与**文本细读**。
通过地图，您可以直观看到故事发生的地点分布；通过下方的章节导读，您可以深入了解各地的核心情节与文化隐喻。
""")

# 2. 数据准备
data = {
    "City": ["湖州 (Huzhou)", "杭州 (Hangzhou)", "扬州 (Yangzhou)", "南京 (Nanjing)", "北京 (Beijing)"],
    "Lat": [30.893, 30.274, 32.394, 32.060, 39.904],
    "Lon": [120.086, 120.155, 119.412, 118.796, 116.407],
    "Frequency": [4, 7, 3, 7, 2],
    "Key_Characters": [
        "娄氏兄弟, 杨执中, 权勿用",
        "马二先生, 匡超人, 潘三, 景兰江",
        "牛玉圃, 万雪斋, 季葦蕭",
        "杜慎卿, 鲍文卿, 鲍廷玺",
        "匡超人, 鲁编修, 李给谏"
    ],
    "Activity": [
        "莺脰湖高会；寻访隐士",
        "西湖诗会；八股文选评；道德堕落",
        "盐商附庸风雅；冒名顶替",
        "莫愁湖梨园大会；戏曲竞赛",
        "科举钻营；停妻再娶"
    ],
    "Summary_Title": [
        "第11-12回：莺脰湖名士大宴",
        "第14-18回：西湖诗会与匡超人的堕落",
        "第22-23回：盐商与假名士",
        "第24, 30回：莫愁湖梨园绝唱",
        "第19-20回：京师里的背叛与荣华"
    ],
    "Summary_Detail": [
        """
        **核心情节**：娄府二公子为了效仿古人礼贤下士，四处寻访“隐士”，最终找来了杨执中和权勿用。他们在莺脰湖举办了盛大的宴会，琴瑟和鸣，极尽风雅。
        
        **深度解析**：这是书中理想主义幻灭的开始。虽然娄公子诚心求贤，但所聚之人多为沽名钓誉之徒（如张铁臂的“人头会”闹剧）。这场聚会象征着传统文人政治理想的空虚与盲目。
        """,
        
        """
        **核心情节**：
        1. **马二先生**在西湖偶遇匡超人，资助其回乡，这是淳朴的善意。
        2. **匡超人**再次来到杭州后，结识了景兰江等“斗方名士”，在西湖结社吟诗。
        3. 为了名利，匡超人逐渐沦丧，参与潘三的非法勾当，学会了伪造文书。
        
        **深度解析**：杭州是“名士”批量生产的工厂。西湖诗会不再是艺术的殿堂，而是庸俗的社交场。这里见证了一个淳朴孝子如何一步步变成虚伪的奸徒。
        """,
        
        """
        **核心情节**：牛玉圃冒充死去的诗人牛布衣，在扬州投奔盐商万雪斋。万雪斋虽富甲一方，却因书童出身而自卑，试图通过供养文人来提升地位。最终牛玉圃因说漏嘴揭了万雪斋的老底而被赶走。
        
        **深度解析**：扬州代表了金钱对文化的异化。文人沦为商人的装饰品，而商人则通过购买文化来洗白身份。这是一场充满了铜臭味的互骗游戏。
        """,
        
        """
        **核心情节**：
        1. **鲍文卿**（戏子）虽地位低微，却拒绝行贿，展现出比官员更高尚的品德。
        2. **杜慎卿**来到南京，为了夸耀才情与财富，在莫愁湖举办了一场规模空前的戏曲大会，评选最佳小旦（男优）。
        
        **深度解析**：与湖州的“求贤”相比，南京的聚会彻底放弃了政治道德色彩，转向了纯粹的感官享乐和唯美主义。这是文人精神世界的最后退守——从治国平天下退缩到梨园声色之中。
        """,
        
        """
        **核心情节**：匡超人逃亡至北京，凭借钻营手段获得了高官李给谏的赏识。为了仕途，他谎称未婚，入赘相府，抛弃了糟糠之妻。
        
        **深度解析**：北京是权力的中心，也是道德毁灭的终点。匡超人的飞黄腾达标志着“儒林”精神的彻底死亡——成功者往往是最无耻的背叛者。
        """
    ]
}

df = pd.DataFrame(data)

# 3. 布局设计
col1, col2 = st.columns([3, 2])

# --- 左侧：地图可视化 ---
with col1:
    st.subheader("📍 地理分布热力图")
    
    # 创建地图
    m = folium.Map(location=[34.0, 118.0], zoom_start=5.5, tiles="Cartodb Positron")

    # 添加点和交互
    for index, row in df.iterrows():
        # 弹出窗口内容
        popup_html = f"""
        <div style="font-family: sans-serif; width: 200px;">
            <h4>{row['City']}</h4>
            <p><b>关键人物:</b> {row['Key_Characters']}</p>
            <p><b>核心事件:</b> {row['Activity']}</p>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['Lat'], row['Lon']],
            radius=row['Frequency'] * 2.5,  # 缩放半径
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{row['City']} (点击查看)",
            color="#E63946",
            fill=True,
            fill_color="#E63946",
            fill_opacity=0.7
        ).add_to(m)

    st_folium(m, width='100%', height=500)

# --- 右侧：章节与故事详情 ---
with col2:
    st.subheader("📖 章节故事导读")
    st.info("点击下方的地点，查看详细的章节概括与分析。")

    # 使用 Tabs 来组织地点，比 Expander 更直观
    city_tabs = st.tabs(["湖州", "杭州", "扬州", "南京", "北京"])
    
    # 湖州内容
    with city_tabs[0]:
        row = df.iloc[0]
        st.markdown(f"### {row['Summary_Title']}")
        st.write(f"**登场人物**: {row['Key_Characters']}")
        st.markdown("---")
        st.markdown(row['Summary_Detail'])
        
    # 杭州内容
    with city_tabs[1]:
        row = df.iloc[1]
        st.markdown(f"### {row['Summary_Title']}")
        st.write(f"**登场人物**: {row['Key_Characters']}")
        st.markdown("---")
        st.markdown(row['Summary_Detail'])
        
    # 扬州内容
    with city_tabs[2]:
        row = df.iloc[2]
        st.markdown(f"### {row['Summary_Title']}")
        st.write(f"**登场人物**: {row['Key_Characters']}")
        st.markdown("---")
        st.markdown(row['Summary_Detail'])

    # 南京内容
    with city_tabs[3]:
        row = df.iloc[3]
        st.markdown(f"### {row['Summary_Title']}")
        st.write(f"**登场人物**: {row['Key_Characters']}")
        st.markdown("---")
        st.markdown(row['Summary_Detail'])

    # 北京内容
    with city_tabs[4]:
        row = df.iloc[4]
        st.markdown(f"### {row['Summary_Title']}")
        st.write(f"**登场人物**: {row['Key_Characters']}")
        st.markdown("---")
        st.markdown(row['Summary_Detail'])

# 4. 底部数据表
st.markdown("---")
with st.expander("查看完整数据源 (Data Source)"):
    st.dataframe(df)
