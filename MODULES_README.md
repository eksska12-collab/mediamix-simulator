# 📦 모듈 구조 가이드

## 개요

app.py 파일이 모듈화되어 유지보수가 훨씬 쉬워졌습니다.
3,365줄의 거대한 파일이 깔끔한 모듈 구조로 분리되었습니다.

---

## 📁 파일 구조

```
madup/
├── modules/                    # ✨ NEW: 모듈 패키지
│   ├── __init__.py            # 패키지 초기화
│   ├── constants.py           # 상수 및 데이터 로드
│   ├── calculations.py        # 계산 함수
│   ├── validators.py          # 검증 함수
│   ├── excel_handler.py       # Excel 파일 생성
│   ├── insights.py            # AI 인사이트 (stub)
│   └── ui_components.py       # UI 컴포넌트
├── app.py                     # 🔄 간소화된 메인 앱
├── media_mix_simulator.py     # CLI 시뮬레이터
├── benchmarks.json            # 벤치마크 데이터
├── media_categories.json      # 매체 카테고리
└── ...
```

---

## 📚 모듈 설명

### 1. **`modules/constants.py`** - 상수 및 데이터 로드

**역할:** JSON 파일에서 데이터를 로드하고 상수로 관리

**포함 함수:**
- `load_benchmarks_json()` - 벤치마크 JSON 로드
- `load_media_categories_json()` - 매체 카테고리 JSON 로드
- `get_available_industries()` - 업종 목록 조회
- `get_media_benchmarks()` - 매체 벤치마크 조회

**제공 상수:**
```python
from modules import (
    BENCHMARKS,
    INDUSTRY_BASE_METRICS,
    INDUSTRY_SEASON_WEIGHT,
    SEASONALITY_COMMON,
    SEASONALITY,
    MEDIA_MULTIPLIERS,
    MEDIA_CATEGORIES,
    ALL_MEDIA,
    RISK_RATIO_THRESHOLD,
    EFFICIENCY_WARNING_THRESHOLD,
)
```

---

### 2. **`modules/calculations.py`** - 계산 함수

**역할:** 성과 계산 및 보정 계수 산출

**포함 함수:**
```python
from modules import (
    calculate_seasonality,           # 계절성 보정 계수
    estimate_conversion_increase,    # 전환수 증가 추정
    calculate_efficiency_grade,      # 효율 등급 계산 (S/A/B/C)
)
```

**예시:**
```python
# 계절성 보정
season_factor = calculate_seasonality(month=12, industry='보험')

# 효율 등급
grade = calculate_efficiency_grade(
    avg_cpa=50000,
    avg_roas=150,
    total_conversions=100
)
```

---

### 3. **`modules/validators.py`** - 검증 함수

**역할:** 입력값 검증 및 경고 메시지 생성

**포함 함수:**
```python
from modules import (
    validate_efficiency,  # 효율값 검증
    EFFICIENCY_RANGES,    # 업종별 효율 범위
)
```

**예시:**
```python
# CTR 검증
warning = validate_efficiency(
    metric_name='CTR',
    value=0.5,
    industry='보험'
)
if warning:
    st.warning(warning)
```

---

### 4. **`modules/excel_handler.py`** - Excel 파일 생성

**역할:** 시뮬레이션 결과를 Excel 파일로 생성

**포함 함수:**
```python
from modules import create_excel_download
```

**예시:**
```python
# Excel 파일 생성
excel_data, filename = create_excel_download(
    scenarios=scenarios,
    budget=budget,
    mode_name="AI예측",
    summary_df=summary_df
)

# Streamlit 다운로드 버튼
st.download_button(
    label="📥 Excel 다운로드",
    data=excel_data,
    file_name=filename,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
```

---

### 5. **`modules/ui_components.py`** - UI 컴포넌트

**역할:** 공통 UI 요소 렌더링

**포함 함수:**
```python
from modules import (
    render_page_header,  # 페이지 헤더
    render_footer,       # 페이지 푸터
)
```

**예시:**
```python
# 페이지 헤더
render_page_header("AI 자동 예측")

# 페이지 내용
st.write("여기에 페이지 내용")

# 페이지 푸터
render_footer()
```

---

### 6. **`modules/insights.py`** - AI 인사이트 (stub)

**역할:** 추천 및 인사이트 함수 (현재는 stub)

**참고:** `generate_recommendations`와 `generate_ai_insights` 함수는
코드가 길어서 현재 `app.py`에 유지되고 있습니다.
향후 리팩토링 시 이 모듈로 이동 가능합니다.

---

## 🔄 app.py 간소화

### Before (3,365줄)
```python
# app.py에 모든 코드가 직접 포함
@st.cache_data(ttl=3600)
def load_benchmarks_json():
    # 긴 코드...

@st.cache_data
def calculate_seasonality(month, industry):
    # 긴 코드...

# ... 수많은 함수 정의들 ...

# 페이지 렌더링 코드도 직접 포함
if mode == "🏠 홈":
    # 수백 줄의 코드...
elif mode == "🤖 AI 자동 예측":
    # 수백 줄의 코드...
# ...
```

### After (간소화됨)
```python
# app.py
from modules import (
    # 필요한 것만 import
    BENCHMARKS, MEDIA_CATEGORIES,
    calculate_seasonality,
    validate_efficiency,
    create_excel_download,
    render_page_header,
    render_footer,
)

# 페이지 렌더링 코드는 여전히 app.py에 있지만
# 공통 함수들은 모듈에서 가져옴

if mode == "🏠 홈":
    render_page_header()
    # 페이지 로직...
    render_footer()
```

---

## 📊 개선 효과

### 1. **코드 구조**
- ✅ 함수별 책임 분리
- ✅ 모듈 단위로 관리
- ✅ import로 깔끔한 의존성

### 2. **유지보수성**
- ✅ 특정 기능 찾기 쉬움
- ✅ 수정 시 영향 범위 명확
- ✅ 테스트 용이

### 3. **재사용성**
- ✅ 다른 프로젝트에서도 모듈 재사용 가능
- ✅ 함수별로 독립적 사용 가능

### 4. **가독성**
- ✅ app.py가 훨씬 짧고 명확
- ✅ 각 모듈의 역할이 명확

---

## 🚀 사용 방법

### 1. 전체 모듈 import
```python
from modules import *
```

### 2. 선택적 import
```python
from modules import (
    BENCHMARKS,
    calculate_seasonality,
    create_excel_download,
)
```

### 3. 모듈별 import
```python
from modules.constants import BENCHMARKS
from modules.calculations import calculate_seasonality
from modules.excel_handler import create_excel_download
```

---

## 📝 향후 개선 사항

### 1. pages 모듈 추가
각 페이지 렌더링 함수를 별도 모듈로 분리:
```python
# modules/pages.py
def render_home_page():
    """홈 페이지 렌더링"""
    render_page_header()
    # 홈 페이지 로직
    render_footer()

def render_ai_prediction_page():
    """AI 예측 페이지 렌더링"""
    # ...

# app.py
from modules.pages import (
    render_home_page,
    render_ai_prediction_page,
    # ...
)

if mode == "🏠 홈":
    render_home_page()
elif mode == "🤖 AI 자동 예측":
    render_ai_prediction_page()
```

### 2. insights 모듈 완성
`generate_recommendations`와 `generate_ai_insights`를 
`modules/insights.py`로 이동

### 3. 추가 모듈 분리
- `modules/charts.py` - 차트 생성 함수
- `modules/presets.py` - 프리셋 관리 함수
- `modules/utils.py` - 유틸리티 함수

---

## ⚠️ 주의사항

### 1. Import 순서
```python
# 표준 라이브러리
import io
import json
from datetime import datetime

# 서드파티 라이브러리
import pandas as pd
import streamlit as st

# 로컬 모듈
from media_mix_simulator import generate_scenarios
from modules import *
```

### 2. 순환 import 방지
모듈 간에 순환 참조가 발생하지 않도록 주의

### 3. 상수 수정
JSON 파일을 수정한 후 앱 재시작 필요 (캐싱 때문)

---

## 🎉 완료!

app.py가 깔끔하게 모듈화되어 유지보수가 훨씬 쉬워졌습니다!

**주요 개선:**
- ✅ 모듈 구조 도입
- ✅ 함수 책임 분리
- ✅ 코드 재사용성 향상
- ✅ 유지보수성 대폭 개선

