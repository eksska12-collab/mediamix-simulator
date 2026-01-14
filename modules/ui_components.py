"""
UI 컴포넌트 모듈
"""

import streamlit as st
from datetime import datetime

# =============================================================================
# 공통 UI 컴포넌트
# =============================================================================

def render_page_header(page_title="미디어믹스 시뮬레이터 v2.0"):
    """
    모든 페이지 상단에 공통 헤더 렌더링
    
    Args:
        page_title: 페이지 제목
    """
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #2196F3 0%, #1976D2 100%); 
                padding: 20px; border-radius: 10px; margin-bottom: 20px; 
                box-shadow: 0 2px 8px rgba(33, 150, 243, 0.15);">
        <h1 style="color: white; margin: 0;">📊 {page_title}</h1>
        <p style="color: rgba(255, 255, 255, 0.9); margin: 5px 0 0 0;">MADUP 마케팅팀 전용 예산 배분 & 성과 예측 툴</p>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    """
    모든 페이지 하단에 푸터 렌더링
    """
    st.markdown("---")
    footer_date = datetime.now().strftime("%Y.%m.%d")
    st.markdown(f"""
    <div style="text-align: center; color: #757575; font-size: 12px; padding: 20px;">
        © 2025 MADUP. All rights reserved. | 
        Performance Marketing Team | 
        v2.5.0 | {footer_date}
    </div>
    """, unsafe_allow_html=True)

