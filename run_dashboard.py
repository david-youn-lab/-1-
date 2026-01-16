"""
COVID-19 대쉬보드 원클릭 실행 스크립트
"""

import subprocess
import sys
import os

def check_requirements():
    """필요 라이브러리 확인 및 설치"""
    print("=" * 60)
    print("COVID-19 대쉬보드 시작")
    print("=" * 60)
    
    try:
        import streamlit
        import plotly
        import pandas
        print("\n✓ 필요 라이브러리 확인 완료")
    except ImportError:
        print("\n필요 라이브러리를 설치합니다...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ 라이브러리 설치 완료")

def run_dashboard():
    """대쉬보드 실행"""
    print("\n대쉬보드를 실행합니다...")
    print("브라우저가 자동으로 열립니다.")
    print("종료하려면 Ctrl+C를 누르세요.\n")
    print("=" * 60)
    
    # Streamlit 실행
    subprocess.run([
        sys.executable, 
        "-m", 
        "streamlit", 
        "run", 
        "dashboard.py",
        "--server.headless=true"
    ])

if __name__ == "__main__":
    try:
        # 현재 디렉토리 확인
        if not os.path.exists("dashboard.py"):
            print("오류: dashboard.py 파일을 찾을 수 없습니다.")
            print("covid19_dashboard 폴더에서 실행해주세요.")
            sys.exit(1)
        
        # 라이브러리 확인
        check_requirements()
        
        # 대쉬보드 실행
        run_dashboard()
        
    except KeyboardInterrupt:
        print("\n\n대쉬보드를 종료합니다.")
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")
        sys.exit(1)
