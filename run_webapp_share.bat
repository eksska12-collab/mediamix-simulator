@echo off
chcp 65001 > nul
echo ====================================
echo 미디어믹스 시뮬레이터 (팀 공유 모드)
echo ====================================
echo.
echo [팀원 공유용 실행]
echo 같은 네트워크의 팀원들이 접속 가능합니다.
echo.
echo 실행 중... Network URL을 팀원에게 공유하세요!
echo.
python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501
pause



