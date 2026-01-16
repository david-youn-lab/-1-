"""
COVID-19 데이터 전처리 모듈
"""

import pandas as pd
import numpy as np
from datetime import datetime

class CovidDataProcessor:
    """코로나19 데이터 전처리 클래스"""
    
    def __init__(self, data_dict):
        """
        Args:
            data_dict: {'confirmed': df, 'deaths': df, 'recovered': df}
        """
        self.raw_data = data_dict
        self.processed_data = None
        
    def process_global_data(self):
        """전세계 데이터 전처리"""
        print("\n데이터 전처리 시작...")
        
        # 확진자 데이터 처리
        confirmed = self._transform_data(self.raw_data['confirmed'], 'confirmed')
        deaths = self._transform_data(self.raw_data['deaths'], 'deaths')
        recovered = self._transform_data(self.raw_data['recovered'], 'recovered')
        
        # 데이터 병합
        df = confirmed.merge(deaths, on=['Country', 'Date'], how='outer')
        df = df.merge(recovered, on=['Country', 'Date'], how='outer')
        
        # 결측치 처리
        df = df.fillna(0)
        
        # 데이터 타입 변환
        df['confirmed'] = df['confirmed'].astype(int)
        df['deaths'] = df['deaths'].astype(int)
        df['recovered'] = df['recovered'].astype(int)
        
        # 일일 신규 확진자, 사망자 계산
        df = df.sort_values(['Country', 'Date'])
        df['daily_confirmed'] = df.groupby('Country')['confirmed'].diff().fillna(0)
        df['daily_deaths'] = df.groupby('Country')['deaths'].diff().fillna(0)
        
        # 음수값 제거 (데이터 수정으로 인한 오류)
        df['daily_confirmed'] = df['daily_confirmed'].clip(lower=0)
        df['daily_deaths'] = df['daily_deaths'].clip(lower=0)
        
        # 치명률 계산 (%)
        df['fatality_rate'] = np.where(
            df['confirmed'] > 0,
            (df['deaths'] / df['confirmed'] * 100).round(2),
            0
        )
        
        # 회복률 계산 (%)
        df['recovery_rate'] = np.where(
            df['confirmed'] > 0,
            (df['recovered'] / df['confirmed'] * 100).round(2),
            0
        )
        
        # 활성 환자 수
        df['active'] = df['confirmed'] - df['deaths'] - df['recovered']
        df['active'] = df['active'].clip(lower=0)
        
        self.processed_data = df
        print("✓ 데이터 전처리 완료")
        
        return df
    
    def _transform_data(self, df, value_name):
        """
        Wide 형식을 Long 형식으로 변환
        
        Args:
            df: 원본 데이터프레임
            value_name: 값 컬럼명 (confirmed, deaths, recovered)
        """
        # 국가별 합계 계산 (Province/State 제거)
        date_cols = df.columns[4:]  # 날짜 컬럼들
        
        # 국가별 그룹화
        country_data = df.groupby('Country/Region')[date_cols].sum()
        
        # Long 형식으로 변환
        country_data = country_data.reset_index()
        country_data = country_data.melt(
            id_vars=['Country/Region'],
            var_name='Date',
            value_name=value_name
        )
        
        # 컬럼명 변경
        country_data.rename(columns={'Country/Region': 'Country'}, inplace=True)
        
        # 날짜 형식 변환
        country_data['Date'] = pd.to_datetime(country_data['Date'])
        
        return country_data
    
    def get_country_summary(self, date=None):
        """
        국가별 최신 통계 요약
        
        Args:
            date: 조회 날짜 (None이면 최신 날짜)
        """
        if self.processed_data is None:
            raise ValueError("데이터를 먼저 전처리하세요 (process_global_data 실행)")
        
        df = self.processed_data
        
        # 최신 날짜 선택
        if date is None:
            date = df['Date'].max()
        
        # 해당 날짜 데이터 필터링
        summary = df[df['Date'] == date].copy()
        
        # 정렬
        summary = summary.sort_values('confirmed', ascending=False)
        
        return summary
    
    def get_global_summary(self):
        """전세계 총계"""
        if self.processed_data is None:
            raise ValueError("데이터를 먼저 전처리하세요 (process_global_data 실행)")
        
        df = self.processed_data
        latest_date = df['Date'].max()
        
        latest_data = df[df['Date'] == latest_date]
        
        summary = {
            'date': latest_date.strftime('%Y-%m-%d'),
            'total_confirmed': int(latest_data['confirmed'].sum()),
            'total_deaths': int(latest_data['deaths'].sum()),
            'total_recovered': int(latest_data['recovered'].sum()),
            'total_active': int(latest_data['active'].sum()),
            'countries': len(latest_data)
        }
        
        return summary
    
    def save_processed_data(self, filename='processed_covid_data.csv'):
        """전처리된 데이터 저장"""
        if self.processed_data is None:
            raise ValueError("데이터를 먼저 전처리하세요")
        
        self.processed_data.to_csv(filename, index=False)
        print(f"✓ 전처리 데이터 저장: {filename}")


if __name__ == "__main__":
    # 테스트
    from data_collector import CovidDataCollector
    
    print("=== COVID-19 데이터 전처리 테스트 ===\n")
    
    # 데이터 수집
    collector = CovidDataCollector()
    raw_data = collector.get_latest_data()
    
    if raw_data:
        # 데이터 전처리
        processor = CovidDataProcessor(raw_data)
        processed_df = processor.process_global_data()
        
        # 전세계 요약
        global_summary = processor.get_global_summary()
        print("\n=== 전세계 통계 ===")
        print(f"기준일: {global_summary['date']}")
        print(f"총 확진자: {global_summary['total_confirmed']:,}")
        print(f"총 사망자: {global_summary['total_deaths']:,}")
        print(f"총 회복자: {global_summary['total_recovered']:,}")
        print(f"활성 환자: {global_summary['total_active']:,}")
        print(f"국가 수: {global_summary['countries']}")
        
        # 상위 10개국
        top10 = processor.get_country_summary().head(10)
        print("\n=== 확진자 상위 10개국 ===")
        print(top10[['Country', 'confirmed', 'deaths', 'recovered', 'fatality_rate']])
        
        # 저장
        processor.save_processed_data('data/processed_covid_data.csv')
