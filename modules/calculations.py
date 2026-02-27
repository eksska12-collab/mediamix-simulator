"""
계산 함수 모듈
"""

import pandas as pd
import streamlit as st
from .constants import (
    SEASONALITY_COMMON, INDUSTRY_SEASON_WEIGHT,
    INDUSTRY_BASE_METRICS, MEDIA_MULTIPLIERS
)

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


# =============================================================================
# 이동된 순수 계산 함수 (from media_mix_simulator.py)
# =============================================================================

def format_number(number):
    """숫자를 천 단위 쉼표 형식으로 변환"""
    return f"{int(number):,}"


def calculate_budget_competition_factor(budget):
    """
    예산 규모별 경쟁도 보정 계수 계산 (CPC 전용)

    예산이 클수록 경쟁이 심한 키워드를 입찰하게 되어 CPC가 상승하는 효과 반영

    Args:
        budget: 총 예산 (원)

    Returns:
        float: CPC 보정 계수
    """
    if budget < 10_000_000:
        return 0.90
    elif budget < 50_000_000:
        return 1.00
    elif budget < 100_000_000:
        return 1.10
    else:
        return 1.20


def apply_adjustments(industry, month, budget, base_metrics):
    """
    업종/계절성/예산 보정을 통합 적용

    Args:
        industry (str): 업종명
        month (int): 월 (1-12)
        budget (float): 총 예산 (원)
        base_metrics (dict): {'CTR': x, 'CPC': y, 'CVR': z}

    Returns:
        dict: 보정된 지표
    """
    # 1. 계절성 공통 보정
    season_factor = SEASONALITY_COMMON.get(month, 1.0)

    # 2. 업종별 계절성 가중치 적용
    if industry in INDUSTRY_SEASON_WEIGHT:
        industry_season = INDUSTRY_SEASON_WEIGHT[industry]
        if month in industry_season['high_months']:
            season_factor *= industry_season['high_multiplier']
        elif month in industry_season['low_months']:
            season_factor *= industry_season['low_multiplier']

    # 3. 예산 규모 경쟁도 보정 (CPC만)
    competition_factor = calculate_budget_competition_factor(budget)

    return {
        'CTR': base_metrics['CTR'] * season_factor,
        'CVR': base_metrics['CVR'] * season_factor,
        'CPC': base_metrics['CPC'] * competition_factor
    }


def calculate_performance(budget, adjusted_metrics):
    """
    보정된 지표로 예상 성과 계산

    Args:
        budget (float): 예산 (원)
        adjusted_metrics (dict): 보정된 지표 {'CTR': x, 'CPC': y, 'CVR': z}

    Returns:
        dict: 예상 성과 (impressions, clicks, conversions, cpa, ctr, cvr, cpc)
    """
    cpc = adjusted_metrics['CPC']
    ctr = adjusted_metrics['CTR']
    cvr = adjusted_metrics['CVR']

    if cpc <= 0:
        raise ValueError(f"CPC must be greater than 0, got {cpc}")
    if ctr <= 0:
        raise ValueError(f"CTR must be greater than 0, got {ctr}")
    if cvr < 0:
        raise ValueError(f"CVR must be non-negative, got {cvr}")
    if budget <= 0:
        raise ValueError(f"Budget must be greater than 0, got {budget}")

    clicks = budget / cpc
    impressions = clicks / ctr
    conversions = clicks * cvr
    cpa = budget / conversions if conversions > 0 else 0

    return {
        'impressions': round(impressions, 0),
        'clicks': round(clicks, 0),
        'conversions': round(conversions, 2),
        'cpa': round(cpa, 0),
        'ctr': round(ctr * 100, 2),
        'cvr': round(cvr * 100, 2),
        'cpc': round(cpc, 0)
    }


@st.cache_data
def get_media_adjusted_metrics(industry, media_key, month, budget):
    """
    특정 매체의 보정된 성과 지표 계산

    Args:
        industry (str): 업종명
        media_key (str): 매체 키 (예: '네이버_SA', '메타_DA')
        month (int): 월 (1-12)
        budget (float): 해당 매체 예산

    Returns:
        dict: 보정된 지표 또는 None
    """
    if industry not in INDUSTRY_BASE_METRICS:
        return None

    base = INDUSTRY_BASE_METRICS[industry]

    if media_key in MEDIA_MULTIPLIERS:
        multiplier = MEDIA_MULTIPLIERS[media_key]
        media_base = {
            'CTR': base['CTR'] * multiplier['CTR'],
            'CPC': base['CPC'] * multiplier['CPC'],
            'CVR': base['CVR'] * multiplier['CVR']
        }
    else:
        media_base = base.copy()

    return apply_adjustments(industry, month, budget, media_base)


def calculate_media_performance(media, total_budget):
    """
    매체별 성과 계산 함수

    Args:
        media: 매체 정보 딕셔너리
        total_budget: 총 예산

    Returns:
        성과 데이터가 추가된 매체 딕셔너리
    """
    if total_budget <= 0:
        raise ValueError(f"총 예산은 0보다 커야 합니다: {total_budget}")
    if media.get('budget_ratio', 0) < 0:
        raise ValueError(f"예산 비중은 0 이상이어야 합니다: {media.get('budget_ratio')}")
    if media.get('cpc', 0) <= 0:
        raise ValueError(f"CPC는 0보다 커야 합니다: {media.get('cpc')}")
    if media.get('ctr', 0) <= 0:
        raise ValueError(f"CTR은 0보다 커야 합니다: {media.get('ctr')}")

    media_budget = total_budget * (media['budget_ratio'] / 100)
    estimated_clicks = media_budget / media['cpc']
    estimated_impressions = estimated_clicks / (media['ctr'] / 100)
    cpm = (media_budget / estimated_impressions) * 1000 if estimated_impressions > 0 else 0
    estimated_conversions = estimated_clicks * (media.get('cvr', 0) / 100)
    cpa = media_budget / estimated_conversions if estimated_conversions > 0 else 0
    total_revenue = estimated_conversions * media.get('revenue_per_cv', 0)
    roas = (total_revenue / media_budget) * 100 if media_budget > 0 else 0

    estimated_conversions_adjusted = estimated_conversions * (1 + media.get('adjustment', 0) / 100)
    cpa_adjusted = media_budget / estimated_conversions_adjusted if estimated_conversions_adjusted > 0 else 0
    total_revenue_adjusted = estimated_conversions_adjusted * media.get('revenue_per_cv', 0)
    roas_adjusted = (total_revenue_adjusted / media_budget) * 100 if media_budget > 0 else 0

    performance = {
        'media_budget': media_budget,
        'estimated_impressions': estimated_impressions,
        'estimated_clicks': estimated_clicks,
        'cpm': cpm,
        'estimated_conversions': estimated_conversions,
        'estimated_conversions_adjusted': estimated_conversions_adjusted,
        'cpa': cpa,
        'cpa_adjusted': cpa_adjusted,
        'total_revenue': total_revenue,
        'total_revenue_adjusted': total_revenue_adjusted,
        'roas': roas,
        'roas_adjusted': roas_adjusted
    }

    return {**media, **performance}


def generate_scenarios(selected_media, total_budget, scenario_adjustment):
    """
    3개 시나리오 생성 함수

    Args:
        selected_media: 선택된 매체 리스트
        total_budget: 총 예산
        scenario_adjustment: 시나리오 조정 폭 (%)

    Returns:
        시나리오 딕셔너리 {'conservative': [], 'base': [], 'aggressive': []}
    """
    scenarios = {
        'conservative': [],
        'base': [],
        'aggressive': []
    }

    for media in selected_media:
        try:
            media_performance = calculate_media_performance(media, total_budget)

            base_media = media_performance.copy()
            scenarios['base'].append(base_media)

            conservative_media = media_performance.copy()
            conservative_media['estimated_conversions_adjusted'] = (
                media_performance['estimated_conversions_adjusted'] * (1 - scenario_adjustment / 100)
            )
            conservative_media['cpa_adjusted'] = (
                conservative_media['media_budget'] / conservative_media['estimated_conversions_adjusted']
                if conservative_media['estimated_conversions_adjusted'] > 0 else 0
            )
            conservative_media['total_revenue_adjusted'] = (
                conservative_media['estimated_conversions_adjusted'] * conservative_media['revenue_per_cv']
            )
            conservative_media['roas_adjusted'] = (
                (conservative_media['total_revenue_adjusted'] / conservative_media['media_budget']) * 100
                if conservative_media['media_budget'] > 0 else 0
            )
            scenarios['conservative'].append(conservative_media)

            aggressive_media = media_performance.copy()
            aggressive_media['estimated_conversions_adjusted'] = (
                media_performance['estimated_conversions_adjusted'] * (1 + scenario_adjustment / 100)
            )
            aggressive_media['cpa_adjusted'] = (
                aggressive_media['media_budget'] / aggressive_media['estimated_conversions_adjusted']
                if aggressive_media['estimated_conversions_adjusted'] > 0 else 0
            )
            aggressive_media['total_revenue_adjusted'] = (
                aggressive_media['estimated_conversions_adjusted'] * aggressive_media['revenue_per_cv']
            )
            aggressive_media['roas_adjusted'] = (
                (aggressive_media['total_revenue_adjusted'] / aggressive_media['media_budget']) * 100
                if aggressive_media['media_budget'] > 0 else 0
            )
            scenarios['aggressive'].append(aggressive_media)

        except Exception as e:
            media_name = media.get('name', 'Unknown')
            error_media = {
                'name': media_name,
                'category': media.get('category', 'N/A'),
                'budget_ratio': media.get('budget_ratio', 0),
                'media_budget': 0,
                'cpm': 0,
                'cpc': media.get('cpc', 0),
                'ctr': media.get('ctr', 0),
                'cvr': media.get('cvr', 0),
                'estimated_impressions': 0,
                'estimated_clicks': 0,
                'estimated_conversions': 0,
                'estimated_conversions_adjusted': 0,
                'cpa_adjusted': 0,
                'revenue_per_cv': media.get('revenue_per_cv', 0),
                'total_revenue_adjusted': 0,
                'roas_adjusted': 0,
                'error': True,
                'error_message': f'계산 실패: {str(e)}'
            }
            scenarios['base'].append(error_media.copy())
            scenarios['conservative'].append(error_media.copy())
            scenarios['aggressive'].append(error_media.copy())

    return scenarios


def create_scenario_dataframe(scenario_data, total_budget):
    """
    시나리오 데이터를 DataFrame으로 변환

    Args:
        scenario_data: 시나리오 매체 리스트
        total_budget: 총 예산

    Returns:
        pandas DataFrame
    """
    data = []

    for media in scenario_data:
        row = {
            '매체명': media['name'],
            '카테고리': media['category'],
            '예산': int(media['media_budget']),
            '예산비중': media['budget_ratio'],
            'CPM': int(media['cpm']),
            '예상노출': int(media['estimated_impressions']),
            '예상클릭': int(media['estimated_clicks']),
            'CTR': media['ctr'],
            'CPC': media['cpc'],
            '예상전환': round(media['estimated_conversions_adjusted'], 1),
            'CVR': media['cvr'],
            'CPA': int(media['cpa_adjusted']),
            'ROAS': round(media['roas_adjusted'], 1)
        }
        data.append(row)

    df = pd.DataFrame(data)

    total_budget_sum = df['예산'].sum()
    total_impressions = df['예상노출'].sum()
    total_clicks = df['예상클릭'].sum()
    total_conversions = df['예상전환'].sum()

    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    avg_cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
    avg_cpa = (total_budget_sum / total_conversions) if total_conversions > 0 else 0

    total_revenue = sum(media['total_revenue_adjusted'] for media in scenario_data)
    avg_roas = (total_revenue / total_budget_sum * 100) if total_budget_sum > 0 else 0

    total_row = {
        '매체명': '합계',
        '카테고리': '',
        '예산': int(total_budget_sum),
        '예산비중': 100.0,
        'CPM': '',
        '예상노출': int(total_impressions),
        '예상클릭': int(total_clicks),
        'CTR': round(avg_ctr, 2),
        'CPC': '',
        '예상전환': round(total_conversions, 1),
        'CVR': round(avg_cvr, 2),
        'CPA': int(avg_cpa),
        'ROAS': round(avg_roas, 1)
    }

    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

    return df


def apply_budget_adjustment(cpc, budget):
    """
    예산 규모에 따른 CPC 보정

    Args:
        cpc: 기본 CPC
        budget: 총 예산

    Returns:
        보정된 CPC
    """
    if budget <= 10000000:
        return int(cpc * 0.9)
    elif budget <= 50000000:
        return int(cpc)
    elif budget <= 100000000:
        return int(cpc * 1.1)
    else:
        return int(cpc * 1.2)
