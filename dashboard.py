"""
COVID-19 실시간 대쉬보드
Streamlit + Plotly 사용
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from data_collector import CovidDataCollector
from data_preprocessing import CovidDataProcessor

# 페이지 설정
st.set_page_config(
    page_title="COVID-19 글로벌 대쉬보드",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 캐싱 - 데이터 로딩 최적화
@st.cache_data(ttl=3600)  # 1시간마다 갱신
def load_data():
    """데이터 로드 및 전처리"""
    collector = CovidDataCollector()
    raw_data = collector.get_latest_data()
    
    if raw_data is None:
        st.error("데이터 로딩 실패")
        return None
    
    processor = CovidDataProcessor(raw_data)
    processed_df = processor.process_global_data()
    
    return processed_df, processor

# 메인 함수
def main():
    # 타이틀
    st.title("🦠 COVID-19 글로벌 대쉬보드")
    st.markdown("---")
    
    # 데이터 로딩
    with st.spinner('데이터 로딩 중...'):
        result = load_data()
        
    if result is None:
        st.stop()
    
    df, processor = result
    
    # 사이드바 - 필터
    st.sidebar.header("📊 필터 설정")
    
    # 날짜 범위 선택
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    date_range = st.sidebar.date_input(
        "날짜 범위 선택",
        value=(max_date - timedelta(days=90), max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # 국가 선택
    countries = sorted(df['Country'].unique())
    selected_countries = st.sidebar.multiselect(
        "국가 선택 (최대 10개)",
        countries,
        default=['Korea, South', 'US', 'United Kingdom', 'Japan', 'China'][:5]
    )
    
    if len(selected_countries) > 10:
        st.sidebar.warning("최대 10개 국가까지 선택 가능합니다.")
        selected_countries = selected_countries[:10]
    
    # 데이터 새로고침 버튼
    if st.sidebar.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()
    
    # 최신 업데이트 시간
    st.sidebar.info(f"최종 업데이트: {max_date}")
    
    # 메인 대쉬보드
    # 1. 전세계 주요 지표
    st.header("🌍 전세계 현황")
    
    global_summary = processor.get_global_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="총 확진자",
            value=f"{global_summary['total_confirmed']:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="총 사망자",
            value=f"{global_summary['total_deaths']:,}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="총 회복자",
            value=f"{global_summary['total_recovered']:,}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="활성 환자",
            value=f"{global_summary['total_active']:,}",
            delta=None
        )
    
    st.markdown("---")
    
    # 2. 국가별 비교
    if selected_countries:
        st.header("📈 국가별 추이 비교")
        
        # 날짜 필터링
        if len(date_range) == 2:
            start_date, end_date = date_range
            mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
            filtered_df = df[mask]
        else:
            filtered_df = df
        
        # 선택된 국가 데이터
        country_df = filtered_df[filtered_df['Country'].isin(selected_countries)]
        
        # 탭으로 구분
        tab1, tab2, tab3, tab4 = st.tabs([
            "누적 확진자", "일일 신규 확진자", "사망자", "회복률"
        ])
        
        with tab1:
            # 누적 확진자 추이
            fig = px.line(
                country_df,
                x='Date',
                y='confirmed',
                color='Country',
                title='누적 확진자 추이',
                labels={'confirmed': '확진자 수', 'Date': '날짜'},
                template='plotly_white'
            )
            fig.update_layout(height=500, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # 일일 신규 확진자 (7일 이동평균)
            country_df_copy = country_df.copy()
            country_df_copy['daily_avg'] = country_df_copy.groupby('Country')['daily_confirmed'].transform(
                lambda x: x.rolling(window=7, min_periods=1).mean()
            )
            
            fig = px.line(
                country_df_copy,
                x='Date',
                y='daily_avg',
                color='Country',
                title='일일 신규 확진자 (7일 이동평균)',
                labels={'daily_avg': '신규 확진자 수', 'Date': '날짜'},
                template='plotly_white'
            )
            fig.update_layout(height=500, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # 누적 사망자
            fig = px.area(
                country_df,
                x='Date',
                y='deaths',
                color='Country',
                title='누적 사망자 추이',
                labels={'deaths': '사망자 수', 'Date': '날짜'},
                template='plotly_white'
            )
            fig.update_layout(height=500, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            # 회복률 비교
            fig = px.line(
                country_df,
                x='Date',
                y='recovery_rate',
                color='Country',
                title='회복률 추이 (%)',
                labels={'recovery_rate': '회복률 (%)', 'Date': '날짜'},
                template='plotly_white'
            )
            fig.update_yaxis(range=[0, 100])
            fig.update_layout(height=500, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 3. 상위 국가 랭킹
    st.header("🏆 국가별 순위")
    
    latest_summary = processor.get_country_summary()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 확진자 상위 20개국
        st.subheader("확진자 상위 20개국")
        top20_confirmed = latest_summary.nlargest(20, 'confirmed')[
            ['Country', 'confirmed', 'deaths', 'fatality_rate']
        ].reset_index(drop=True)
        top20_confirmed.index += 1
        
        st.dataframe(
            top20_confirmed.style.format({
                'confirmed': '{:,.0f}',
                'deaths': '{:,.0f}',
                'fatality_rate': '{:.2f}%'
            }),
            use_container_width=True,
            height=400
        )
    
    with col2:
        # 사망자 상위 20개국
        st.subheader("사망자 상위 20개국")
        top20_deaths = latest_summary.nlargest(20, 'deaths')[
            ['Country', 'deaths', 'confirmed', 'fatality_rate']
        ].reset_index(drop=True)
        top20_deaths.index += 1
        
        st.dataframe(
            top20_deaths.style.format({
                'confirmed': '{:,.0f}',
                'deaths': '{:,.0f}',
                'fatality_rate': '{:.2f}%'
            }),
            use_container_width=True,
            height=400
        )
    
    # 4. 차트 추가 - 확진자 상위 10개국 막대 그래프
    st.markdown("---")
    st.header("📊 확진자 상위 10개국")
    
    top10 = latest_summary.nlargest(10, 'confirmed')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=top10['Country'],
        y=top10['confirmed'],
        name='확진자',
        marker_color='indianred'
    ))
    
    fig.update_layout(
        title='확진자 상위 10개국',
        xaxis_title='국가',
        yaxis_title='확진자 수',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 푸터
    st.markdown("---")
    st.caption("데이터 출처: Johns Hopkins University CSSE COVID-19 Data")
    st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
