"""
계산 함수 모듈
"""

import streamlit as st
from .constants import SEASONALITY_COMMON, INDUSTRY_SEASON_WEIGHT

# =============================================================================
# 계산 함수
# =============================================================================

@st.cache_data
def calculate_seasonality(month, industry):
    """
    계절성 보정 계수 계산 (동적 계산 캐싱)
    
    Args:
        month (int): 운영 월 (1-12)
        industry (str): 업종명
    
    Returns:
        float: 계절성 보정 계수
    """
    season_factor = SEASONALITY_COMMON.get(month, 1.0)
    industry_season = INDUSTRY_SEASON_WEIGHT.get(industry, {})
    
    if month in industry_season.get('high_months', []):
        season_factor *= industry_season.get('high_multiplier', 1.0)
    elif month in industry_season.get('low_months', []):
        season_factor *= industry_season.get('low_multiplier', 1.0)
    
    return season_factor

def estimate_conversion_increase(media, ratio_increase):
    """
    비중 증가 시 전환수 증가 추정
    
    Args:
        media: 매체 정보
        ratio_increase: 비중 증가량
    
    Returns:
        float: 예상 전환수 증가
    """
    current_conversions = media.get('conversions', 0)
    current_ratio = media.get('ratio', 0)
    if current_ratio > 0:
        return current_conversions * (ratio_increase / current_ratio)
    return 0

def calculate_efficiency_grade(avg_cpa, avg_roas, total_conversions):
    """
    효율 등급 계산 (S/A/B/C)
    
    Args:
        avg_cpa: 평균 CPA
        avg_roas: 평균 ROAS (%)
        total_conversions: 총 전환수
    
    Returns:
        grade: 효율 등급 (S/A/B/C)
    """
    score = 0
    
    # ROAS 점수 (40점)
    if avg_roas >= 300:
        score += 40
    elif avg_roas >= 200:
        score += 30
    elif avg_roas >= 150:
        score += 20
    elif avg_roas >= 100:
        score += 10
    
    # 전환수 점수 (30점)
    if total_conversions >= 500:
        score += 30
    elif total_conversions >= 300:
        score += 25
    elif total_conversions >= 150:
        score += 20
    elif total_conversions >= 50:
        score += 10
    
    # CPA 점수 (30점) - 업종 평균 50,000원 기준
    if avg_cpa > 0:
        if avg_cpa <= 30000:
            score += 30
        elif avg_cpa <= 40000:
            score += 25
        elif avg_cpa <= 50000:
            score += 20
        elif avg_cpa <= 70000:
            score += 10
    
    # 등급 부여
    if score >= 80:
        return 'S'
    elif score >= 60:
        return 'A'
    elif score >= 40:
        return 'B'
    else:
        return 'C'

