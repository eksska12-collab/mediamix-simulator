"""
미디어믹스 시뮬레이터 모듈 패키지

모듈 구조:
- constants.py: 상수 및 데이터 로드
- calculations.py: 계산 함수
- validators.py: 검증 함수
- excel_handler.py: Excel 파일 생성
- insights.py: AI 인사이트 및 추천 (stub)
- ui_components.py: UI 컴포넌트
"""

from .constants import (
    BENCHMARKS, INDUSTRY_BASE_METRICS, INDUSTRY_SEASON_WEIGHT,
    SEASONALITY_COMMON, SEASONALITY, MEDIA_MULTIPLIERS,
    MEDIA_CATEGORIES, ALL_MEDIA,
    RISK_RATIO_THRESHOLD, EFFICIENCY_WARNING_THRESHOLD, EFFICIENCY_RANGES,
    load_benchmarks_json, load_media_categories_json,
    get_available_industries, get_media_benchmarks
)

from .calculations import (
    calculate_seasonality,
    estimate_conversion_increase,
    calculate_efficiency_grade
)

from .validators import (
    validate_input,
    validate_efficiency
)

from .excel_handler import (
    create_excel_download
)

from .ui_components import (
    render_page_header,
    render_footer
)

__all__ = [
    # constants
    'BENCHMARKS', 'INDUSTRY_BASE_METRICS', 'INDUSTRY_SEASON_WEIGHT',
    'SEASONALITY_COMMON', 'SEASONALITY', 'MEDIA_MULTIPLIERS',
    'MEDIA_CATEGORIES', 'ALL_MEDIA',
    'RISK_RATIO_THRESHOLD', 'EFFICIENCY_WARNING_THRESHOLD',
    'load_benchmarks_json', 'load_media_categories_json',
    'get_available_industries', 'get_media_benchmarks',
    
    # calculations
    'calculate_seasonality',
    'estimate_conversion_increase',
    'calculate_efficiency_grade',
    
    # validators
    'validate_input',
    'validate_efficiency',
    'EFFICIENCY_RANGES',
    
    # excel_handler
    'create_excel_download',
    
    # ui_components
    'render_page_header',
    'render_footer',
]

