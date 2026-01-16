"""
COVID-19 데이터 수집 모듈
Johns Hopkins University CSSE 데이터 사용
"""

import pandas as pd
import requests
from datetime import datetime
import os

class CovidDataCollector:
    """코로나19 데이터 수집 클래스"""
    
    def __init__(self):
        # Johns Hopkins University GitHub 저장소 URL
        self.base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
        
        # 데이터 파일명
        self.files = {
            'confirmed': 'time_series_covid19_confirmed_global.csv',
            'deaths': 'time_series_covid19_deaths_global.csv',
            'recovered': 'time_series_covid19_recovered_global.csv'
        }
        
        # 데이터 저장 폴더 - Windows 절대 경로로 변경
        self.data_dir = r'C:\Users\PRO\Desktop\프로젝트\코로나19대쉬보드\코로나데이터'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def download_data(self):
        """데이터 다운로드"""
        print("데이터 다운로드 시작...")
        data_dict = {}
        
        for key, filename in self.files.items():
            url = self.base_url + filename
            try:
                print(f"{key} 데이터 다운로드 중...")
                df = pd.read_csv(url)
                data_dict[key] = df
                
                # 로컬에 저장
                save_path = os.path.join(self.data_dir, filename)
                df.to_csv(save_path, index=False)
                print(f"✓ {key} 데이터 저장 완료: {save_path}")
                
            except Exception as e:
                print(f"✗ {key} 데이터 다운로드 실패: {str(e)}")
                return None
        
        print(f"\n전체 데이터 다운로드 완료 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return data_dict
    
    def get_latest_data(self):
        """최신 데이터 조회"""
        return self.download_data()


if __name__ == "__main__":
    # 테스트 실행
    collector = CovidDataCollector()
    data = collector.get_latest_data()
    
    if data:
        print("\n=== 데이터 요약 ===")
        for key, df in data.items():
            print(f"\n{key.upper()}:")
            print(f"  - 행 수: {len(df)}")
            print(f"  - 열 수: {len(df.columns)}")
            print(f"  - 날짜 범위: {df.columns[4]} ~ {df.columns[-1]}")