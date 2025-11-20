import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from streamlit_option_menu import option_menu

# ---------------------------------------------------------
# 1. 页面配置与 CSS 样式 (UI 核心)
# ---------------------------------------------------------
st.set_page_config(
    page_title="云墨·太白 | 李白情感数据可视化",
    page_icon="🍶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 注入
def local_css():
    st.markdown("""
    <style>
    /* 全局字体设置：优先使用楷体/宋体 */
    html, body, [class*="css"] {
        font-family: "KaiTi", "STKaiti", "Times New Roman", serif;
    }
    
    /* 背景图片：水墨山水风格 */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1518182170546-07661fd94144?q=80&w=2574&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }

    /* 遮罩层：让文字在背景上更清晰 */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
    }

    /* 标题样式 */
    h1, h2, h3 {
        color: #2c3e50;
        text-align: center;
        font-weight: bold;
    }
    
    h1 {
        text-shadow: 2px 2px 4px #aaaaaa;
        font-size: 3.5rem !important;
    }

    /* 侧边栏美化 */
    section[data-testid="stSidebar"] {
        background-color: rgba(240, 242, 246, 0.9);
        border-right: 1px solid #d1d1d1;
    }

    /* 按钮样式 */
    .stButton>button {
        background-color: #2c3e50;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #34495e;
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* 诗词卡片样式 */
    .poem-card {
        background-color: #f9f9f9;
        border-left: 5px solid #2c3e50;
        padding: 15px;
        margin: 10px 0;
        font-size: 1.2rem;
        font-style: italic;
        color: #444;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ---------------------------------------------------------
# 2. 数据准备 (模拟数据，替换为你原来的数据逻辑)
# ---------------------------------------------------------
@st.cache_data
def get_travel_data():
    # 模拟李白游历数据
    data = {
        '地点': ['长安', '成都', '洛阳', '金陵 (南京)', '扬州', '庐山', '宣城'],
        'lat': [34.3416, 30.5728, 34.6197, 32.0603, 32.3945, 29.5643, 30.9407],
        'lon': [108.9398, 104.0668, 112.4540, 118.7969, 119.4122, 115.9881, 118.7587],
        '诗作数': [50, 20, 35, 45, 30, 15, 25],
        '代表作': ['长相思', '蜀道难', '春夜洛城闻笛', '登金陵凤凰台', '黄鹤楼送孟浩然之广陵', '望庐山瀑布', '独坐敬亭山']
    }
    return pd.DataFrame(data)

@st.cache_data
def get_emotion_data():
    # 模拟情感关键词数据
    return pd.DataFrame({
        '意象': ['月亮', '酒', '剑', '水', '山', '花', '孤', '梦'],
        '频率': [120, 95, 40, 85, 110, 60, 55, 30],
        '情感色彩': ['思乡/孤独', '豪迈/解忧', '侠客/抱负', '流逝/愁苦', '归隐/壮阔', '美好/易逝', '寂寞', '虚幻']
    })

# ---------------------------------------------------------
# 3. 侧边栏导航
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Li_Bai_%28Ky%C5%AB_Ying%29.jpg/480px-Li_Bai_%28Ky%C5%AB_Ying%29.jpg", width=150, caption="诗仙·李白")
    
    selected = option_menu(
        "导航", 
        ["太白生平", "足迹漫游", "情感图谱", "与仙对饮"], 
        icons=['book', 'map', 'bar-chart', 'chat-quote'],
        menu_icon="cast", default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#2c3e50", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#2c3e50"},
        }
    )
    
    st.markdown("---")
    st.markdown("### 🎵 听琴")
    st.audio("https://upload.wikimedia.org/wikipedia/commons/transcoded/c/c6/Guqin_Silk_String.ogg/Guqin_Silk_String.ogg.mp3")
    st.caption("古琴曲：流水")

# ---------------------------------------------------------
# 4. 主页面逻辑
# ---------------------------------------------------------

# --- 页面 1: 太白生平 ---
if selected == "太白生平":
    st.title("☁️ 谪仙人：李白")
    st.markdown("**“绣口一吐，就半个盛唐。”**")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info("字：太白")
        st.info("号：青莲居士")
        st.info("朝代：唐朝")
        st.info("评价：诗仙")
        
    with col2:
        st.markdown("""
        <div class="poem-card">
        君不见，黄河之水天上来，奔流到海不复回。<br>
        君不见，高堂明镜悲白发，朝如青丝暮成雪。<br>
        人生得意须尽欢，莫使金樽空对月。
        </div>
        """, unsafe_allow_html=True)
        st.write("李白（701年－762年），字太白，号青莲居士，又号“谪仙人”。他是唐代伟大的浪漫主义诗人，被后人誉为“诗仙”。其诗以七言古诗和绝句成就最高，风格豪迈奔放，清新飘逸，想象丰富，意境奇妙，语言奇采，浪漫主义色彩浓厚。")

# --- 页面 2: 足迹漫游 (地图可视化) ---
elif selected == "足迹漫游":
    st.title("🗺️ 仗剑走天涯")
    st.write("李白一生足迹遍布半个中国，从西域碎叶城到长安，从黄河到长江。")
    
    df_travel = get_travel_data()
    
    # 使用 Plotly 绘制交互式散点地图
    fig = px.scatter_geo(
        df_travel,
        lat='lat',
        lon='lon',
        size='诗作数',
        hover_name='地点',
        hover_data=['代表作'],
        scope='asia',
        center=dict(lat=33, lon=110),
        projection="natural earth",
        color='诗作数',
        color_continuous_scale='Tealgrn', # 青绿色系，符合水墨风
        template='plotly_white',
        title="李白游历热力图 (气泡大小代表产诗量)"
    )
    fig.update_layout(
        geo=dict(
            showland=True, landcolor="rgb(240, 240, 240)",
            showcountries=True, countrycolor="rgb(200, 200, 200)",
            fitbounds="locations"
        ),
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 数据详情
    with st.expander("查看详细游历数据"):
        st.dataframe(df_travel, use_container_width=True)

# --- 页面 3: 情感图谱 (图表可视化) ---
elif selected == "情感图谱":
    st.title("📊 诗中的情感密码")
    
    df_emotion = get_emotion_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("高频意象统计")
        # 饼图
        fig_pie = px.pie(
            df_emotion, 
            values='频率', 
            names='意象', 
            title='李白最爱用的词',
            color_discrete_sequence=px.colors.sequential.Teal,
            hole=0.4
        )
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col2:
        st.subheader("意象背后的情感")
        # 柱状图
        fig_bar = px.bar(
            df_emotion, 
            x='意象', 
            y='频率', 
            color='频率', 
            text='情感色彩',
            title='意象与情感关联',
            color_continuous_scale='Blues'
        )
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("### 情感解读")
    st.markdown("""
    > **月亮** 是李白诗中最孤独的伴侣，出现了 120 次以上。它代表了乡愁与超越世俗的渴望。
    >
    > **酒** 则是他通向自由的钥匙，“百年三万六千日，一日须倾三百杯”。
    """)

# --- 页面 4: 与仙对饮 (交互功能) ---
elif selected == "与仙对饮":
    st.title("🍶 飞花令·互动")
    st.write("告诉李白你现在的心情，他会回赠你一句诗。")
    
    mood = st.selectbox("你现在的心情如何？", ["豪情万丈", "思念故乡", "怀才不遇", "享受自然", "感叹时光"])
    
    if st.button("向太白敬酒"):
        st.toast("举杯邀明月，对影成三人...", icon="🥂")
        
        st.markdown("---")
        st.markdown("### 李白的回应：")
        
        if mood == "豪情万丈":
            st.success("大鹏一日同风起，扶摇直上九万里！")
            st.image("https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1000&q=80", caption="大鹏展翅")
        elif mood == "思念故乡":
            st.info("举头望明月，低头思故乡。")
            st.image("https://images.unsplash.com/photo-1532978796341-128865632d53?auto=format&fit=crop&w=1000&q=80", caption="明月寄相思")
        elif mood == "怀才不遇":
            st.warning("天生我材必有用，千金散尽还复来。")
        elif mood == "享受自然":
            st.success("两岸猿声啼不住，轻舟已过万重山。")
            st.image("https://images.unsplash.com/photo-1518098268026-4e187149659d?auto=format&fit=crop&w=1000&q=80", caption="轻舟万重山")
        elif mood == "感叹时光":
            st.error("弃我去者，昨日之日不可留；乱我心者，今日之日多烦忧。")
            
    st.markdown("---")
    st.caption("输入框：写下你想对李白说的话（数据将用于生成词云）")
    user_input = st.text_area("", placeholder="太白兄，我想对你说...")
    if user_input:
        st.write(f"李白收到了你的信：*{user_input}*")

# ---------------------------------------------------------
# 页脚
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: grey;">
    Designed for Li Bai Emotion Data Project | Created with Streamlit <br>
    UI Design Style: Ink & Cloud (云墨)
</div>
""", unsafe_allow_html=True)
