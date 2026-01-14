"""
상수 및 데이터 로드 모듈
"""

import json
import streamlit as st

# =============================================================================
# JSON 데이터 로드
# =============================================================================

@st.cache_data(ttl=3600)
def load_benchmarks_json():
    """
    벤치마크 데이터를 JSON 파일에서 로드
    
    Returns:
        dict: 벤치마크 데이터 전체
    """
    try:
        with open('benchmarks.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # JSON의 숫자 키를 정수로 변환 (SEASONALITY_COMMON)
        if 'SEASONALITY_COMMON' in data:
            data['SEASONALITY_COMMON'] = {
                int(k) if k.isdigit() else k: v 
                for k, v in data['SEASONALITY_COMMON'].items()
                if k != 'description'
            }
        
        # SEASONALITY도 정수 키로 변환
        if 'SEASONALITY' in data:
            data['SEASONALITY'] = {
                int(k) if k.isdigit() else k: v 
                for k, v in data['SEASONALITY'].items()
                if k != 'note'
            }
        
        return data
    except FileNotFoundError:
        st.error("⚠️ benchmarks.json 파일을 찾을 수 없습니다.")
        return {}
    except json.JSONDecodeError as e:
        st.error(f"⚠️ benchmarks.json 파일 파싱 오류: {e}")
        return {}

@st.cache_data(ttl=3600)
def load_media_categories_json():
    """
    매체 카테고리 데이터를 JSON 파일에서 로드
    
    Returns:
        dict: 매체 카테고리 데이터 전체
    """
    try:
        with open('media_categories.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("⚠️ media_categories.json 파일을 찾을 수 없습니다.")
        return {}
    except json.JSONDecodeError as e:
        st.error(f"⚠️ media_categories.json 파일 파싱 오류: {e}")
        return {}

# JSON 데이터 로드
_benchmarks_data = load_benchmarks_json()
_media_data = load_media_categories_json()

# =============================================================================
# 상수 정의 (JSON에서 로드)
# =============================================================================

BENCHMARKS = _benchmarks_data.get('BENCHMARKS', {})
INDUSTRY_BASE_METRICS = _benchmarks_data.get('INDUSTRY_BASE_METRICS', {})
INDUSTRY_SEASON_WEIGHT = _benchmarks_data.get('INDUSTRY_SEASON_WEIGHT', {})
SEASONALITY_COMMON = _benchmarks_data.get('SEASONALITY_COMMON', {})
SEASONALITY = _benchmarks_data.get('SEASONALITY', {})
MEDIA_MULTIPLIERS = _benchmarks_data.get('MEDIA_MULTIPLIERS', {})
EFFICIENCY_RANGES = _benchmarks_data.get('EFFICIENCY_RANGES', {})

MEDIA_CATEGORIES = _media_data.get('MEDIA_CATEGORIES_WEB', {})

ALL_MEDIA = MEDIA_CATEGORIES.get('SA', []) + MEDIA_CATEGORIES.get('DA', [])

# =============================================================================
# 기타 상수
# =============================================================================

RISK_RATIO_THRESHOLD = 50
EFFICIENCY_WARNING_THRESHOLD = 0.5

# =============================================================================
# 캐시 헬퍼 함수
# =============================================================================

@st.cache_data(ttl=3600)
def get_available_industries():
    """
    사용 가능한 업종 목록 조회 (상수 데이터 캐싱)
    
    Returns:
        list: 업종명 리스트
    """
    return list(BENCHMARKS.keys())

@st.cache_data(ttl=3600)
def get_media_benchmarks(industry, media_key):
    """
    특정 업종/매체의 벤치마크 데이터 조회 (상수 데이터 캐싱)
    
    Args:
        industry (str): 업종명
        media_key (str): 매체 키 (예: '네이버_SA')
    
    Returns:
        dict: 벤치마크 데이터 또는 None
    """
    return BENCHMARKS.get(industry, {}).get(media_key)

