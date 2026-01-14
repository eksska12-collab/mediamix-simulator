# 🏗️ 아키텍처 및 Import 구조

## 개요

미디어믹스 시뮬레이터의 모듈 구조와 import 방향을 문서화합니다.

---

## 📦 모듈 구조

```
madup/
├── app.py                      # Streamlit 웹 애플리케이션
├── media_mix_simulator.py      # CLI 시뮬레이터
├── benchmarks.json             # 벤치마크 데이터
├── media_categories.json       # 매체 카테고리 데이터
└── modules/                    # 공통 모듈 패키지
    ├── __init__.py             # 패키지 초기화 및 export
    ├── constants.py            # 상수 및 JSON 로드
    ├── calculations.py         # 계산 함수
    ├── validators.py           # 검증 함수
    ├── excel_handler.py        # Excel 파일 생성
    ├── ui_components.py        # UI 컴포넌트
    └── insights.py             # AI 인사이트 (stub)
```

---

## 🔄 Import 방향 (단방향)

### Level 0: 외부 의존성
```
json, pandas, streamlit, openpyxl, datetime
```

### Level 1: 데이터 소스
```
benchmarks.json
media_categories.json
```

### Level 2: 상수 모듈
```
modules/constants.py
    ├─ load_benchmarks_json()
    ├─ load_media_categories_json()
    ├─ BENCHMARKS
    ├─ INDUSTRY_BASE_METRICS
    ├─ SEASONALITY_COMMON
    ├─ MEDIA_CATEGORIES
    └─ EFFICIENCY_RANGES
```

### Level 3: 계산 및 검증 모듈
```
modules/calculations.py
    └─ import from constants

modules/validators.py
    └─ import from constants
```

### Level 4: 핸들러 및 UI 모듈
```
modules/excel_handler.py
    └─ No internal imports (독립적)

modules/ui_components.py
    └─ No internal imports (독립적)

modules/insights.py
    └─ No internal imports (stub)
```

### Level 5: 패키지 Export
```
modules/__init__.py
    ├─ import from constants
    ├─ import from calculations
    ├─ import from validators
    ├─ import from excel_handler
    ├─ import from ui_components
    └─ import from insights
```

### Level 6: 애플리케이션
```
app.py
    └─ import from modules

media_mix_simulator.py
    └─ Direct JSON load (독립적)
```

---

## ✅ Import 규칙

### Rule 1: 단방향 의존성
```python
# ✅ 허용
constants.py → JSON 파일
calculations.py → constants.py
app.py → modules

# ❌ 금지 (순환 참조)
constants.py → calculations.py
excel_handler.py → media_mix_simulator.py
```

### Rule 2: 레벨 간 Import만 허용
```python
# ✅ 상위 레벨은 하위 레벨 import 가능
app.py → modules (Level 6 → Level 5)
calculations.py → constants.py (Level 3 → Level 2)

# ❌ 같은 레벨 또는 하위→상위 import 금지
calculations.py → validators.py (Level 3 ↔ Level 3) ❌
constants.py → app.py (Level 2 → Level 6) ❌
```

### Rule 3: 독립 모듈
```python
# 다음 모듈들은 내부 import 없음
- excel_handler.py (외부 라이브러리만)
- ui_components.py (외부 라이브러리만)
- insights.py (stub)
```

---

## 🔍 Import 체크리스트

### 새 모듈 추가 시 확인사항

1. **Import 레벨 확인**
   - 상위 레벨에서 하위 레벨로만 import
   - 같은 레벨 간 import 금지

2. **순환 참조 방지**
   ```bash
   # Python으로 간단 테스트
   python -c "import modules; print('✅ No circular import')"
   ```

3. **의존성 최소화**
   - 필요한 것만 import
   - 전체 모듈 import 금지 (`from module import *` 사용 금지, `__init__.py` 제외)

---

## 🛡️ 안정성 보장

### 1. 실패 복구 (Fail-Safe)

**매체별 계산:**
```python
try:
    media_performance = calculate_media_performance(media, budget)
except Exception as e:
    # 계산 실패 시 더미 데이터 반환
    media_performance = create_error_media(media, str(e))
```

**Excel 생성:**
```python
try:
    row = create_media_row(media)
except Exception as e:
    # 실패 시 빈 행 추가
    row = create_empty_row(media['name'])
```

### 2. 입력 검증 중앙화

**validate_input() 함수:**
```python
# 모든 모드에서 공통 사용
is_valid, error_msg = validate_input('budget', budget_value)
if not is_valid:
    st.error(error_msg)
    return

is_valid, warning_msg = validate_input('ctr', ctr_value, industry=industry)
if warning_msg:
    st.warning(warning_msg)  # 경고만 표시, 계속 진행
```

**검증 타입:**
- `budget`: 예산 (100만원~100억원)
- `ratio`: 예산 비중 (0~100%)
- `cpc`: 클릭당 비용 (10원~100,000원)
- `ctr`: 클릭률 (0~100%, 업종별 경고)
- `cvr`: 전환율 (0~100%, 업종별 경고)
- `revenue`: 전환당 매출 (1,000원~1억원)
- `month`: 월 (1~12)
- `adjustment`: 예측 오차 (-100~100%)

### 3. 오류 전파 방지

**원칙:**
- 매체 하나의 계산 실패가 전체 계산을 중단시키지 않음
- 실패한 매체는 "계산 불가" 표시
- 성공한 매체들로 결과 계속 생성

---

## 📋 의존성 그래프

```
                    ┌─────────────────┐
                    │  JSON Files     │
                    │  (Data Source)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   constants.py  │
                    │  (Level 2)      │
                    └────┬─────┬──────┘
                         │     │
         ┌───────────────┘     └───────────────┐
         │                                      │
┌────────▼────────┐                   ┌────────▼────────┐
│ calculations.py │                   │  validators.py  │
│   (Level 3)     │                   │   (Level 3)     │
└─────────────────┘                   └─────────────────┘
         │                                      │
         └──────────────┬───────────────────────┘
                        │
              ┌─────────▼──────────┐
              │  excel_handler.py  │
              │  ui_components.py  │
              │     (Level 4)      │
              └─────────┬──────────┘
                        │
                ┌───────▼────────┐
                │ __init__.py    │
                │   (Level 5)    │
                └───────┬────────┘
                        │
           ┌────────────┴────────────┐
           │                         │
    ┌──────▼──────┐         ┌───────▼──────┐
    │   app.py    │         │ media_mix_   │
    │  (Level 6)  │         │ simulator.py │
    └─────────────┘         └──────────────┘
```

---

## 🔧 문제 해결

### Import Error 발생 시

1. **순환 참조 확인**
   ```python
   # Python 실행하여 확인
   python -c "import app"
   ```

2. **Import 순서 확인**
   - 상위 레벨 → 하위 레벨만 가능
   - 레벨 그래프 참조

3. **모듈 위치 확인**
   - `modules/` 디렉토리 내부인지
   - `__init__.py`에 export 되었는지

### 순환 참조 해결 방법

1. **함수 내부 import** (최후의 수단)
   ```python
   def my_function():
       from .other_module import helper
       return helper()
   ```

2. **모듈 분리**
   - 공통 부분을 새 모듈로 분리
   - 양쪽에서 새 모듈 import

3. **의존성 제거**
   - 필요한 함수를 복사하거나
   - 파라미터로 전달

---

## 📚 참고

- [Python Import System](https://docs.python.org/3/reference/import.html)
- [Circular Import 피하기](https://stackabuse.com/python-circular-imports/)

---

## ✨ 정리

1. **단방향 의존성**: 상위 → 하위만 허용
2. **레벨 시스템**: 6단계 레벨 구조
3. **안전성 우선**: 실패 복구 및 검증 중앙화
4. **독립 모듈**: 순환 참조 방지

깔끔하고 유지보수 가능한 아키텍처! 🎉

