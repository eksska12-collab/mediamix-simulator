# 🚀 캐싱 최적화 가이드

## 개요

미디어믹스 시뮬레이터는 **2종 캐싱 전략**으로 성능을 최적화합니다.

---

## 📊 캐싱 전략

### 1. **데이터 로드 캐싱** (TTL=3600초 / 1시간)

JSON 파일에서 로드하는 상수 데이터는 1시간 동안 캐싱됩니다.

```python
@st.cache_data(ttl=3600)
def load_benchmarks_json():
    """벤치마크 데이터 로드 (1시간 캐싱)"""
    with open('benchmarks.json', 'r', encoding='utf-8') as f:
        return json.load(f)
```

**적용 함수:**
- `load_benchmarks_json()` - 벤치마크 JSON 로드
- `load_media_categories_json()` - 매체 카테고리 JSON 로드
- `get_available_industries()` - 업종 목록
- `get_media_benchmarks()` - 매체 벤치마크

### 2. **계산 결과 캐싱** (TTL 없음 / 영구)

동적 계산 결과는 파라미터 조합별로 영구 캐싱됩니다.

```python
@st.cache_data
def calculate_seasonality(month, industry):
    """계절성 보정 계수 계산 (영구 캐싱)"""
    season_factor = SEASONALITY_COMMON.get(month, 1.0)
    industry_season = INDUSTRY_SEASON_WEIGHT.get(industry, {})
    
    if month in industry_season.get('high_months', []):
        season_factor *= industry_season.get('high_multiplier', 1.0)
    elif month in industry_season.get('low_months', []):
        season_factor *= industry_season.get('low_multiplier', 1.0)
    
    return season_factor
```

**적용 함수:**
- `calculate_seasonality(month, industry)` - 계절성 보정

---

## 🎯 캐싱 규칙

### Rule 1: 데이터 로드는 TTL=3600

```python
@st.cache_data(ttl=3600)
def load_data():
    # JSON 파일 로드
    pass
```

**이유:** JSON 파일 변경 시 앱 재시작이 필요하므로 1시간 캐시로 충분

### Rule 2: 계산 결과는 TTL 없음

```python
@st.cache_data
def calculate(param1, param2):
    # 동적 계산
    pass
```

**이유:** 같은 파라미터는 항상 같은 결과를 반환하므로 영구 캐싱

### Rule 3: 중복 래퍼 함수 금지

```python
# ❌ 나쁜 예: 불필요한 래퍼
@st.cache_data
def calculate_seasonality_cached(month, industry):
    return calculate_seasonality(month, industry)

# ✅ 좋은 예: 직접 사용
result = calculate_seasonality(month, industry)
```

---

## 📝 캐시 함수 목록

### 데이터 로드 (TTL=3600)

| 함수명 | 설명 | 반환값 |
|--------|------|--------|
| `load_benchmarks_json()` | 벤치마크 JSON 로드 | dict |
| `load_media_categories_json()` | 매체 카테고리 JSON 로드 | dict |
| `get_available_industries()` | 업종 목록 | list |
| `get_media_benchmarks(industry, media_key)` | 매체 벤치마크 | dict |

### 계산 결과 (영구 캐싱)

| 함수명 | 설명 | 반환값 |
|--------|------|--------|
| `calculate_seasonality(month, industry)` | 계절성 보정 계수 | float |

---

## 🔄 사용 예시

### 1. 벤치마크 데이터 접근

```python
# 상수 직접 접근
industry_data = BENCHMARKS.get(industry, {})
base_metrics = INDUSTRY_BASE_METRICS.get(industry, {})
```

### 2. 계절성 계산

```python
# 캐시된 계산 함수 사용
season_factor = calculate_seasonality(month, industry)
```

### 3. 매체 벤치마크 조회

```python
# 캐시된 조회 함수 사용
media_data = get_media_benchmarks(industry, media_key)
```

---

## 📈 성능 효과

### 1. **메모리 효율성**
- 중복 캐시 제거로 메모리 절감
- 필요한 데이터만 캐싱

### 2. **코드 간소화**
- 명확한 캐싱 전략
- 중복 함수 제거

### 3. **유지보수성**
- 2종 규칙만 기억하면 됨
- 디버깅 용이

---

## 🚨 주의사항

### 1. JSON 수정 후 앱 재시작

JSON 파일을 수정한 후에는 반드시 앱을 재시작해야 합니다.

```bash
# Ctrl+C로 중단 후 재시작
python -m streamlit run app.py
```

### 2. 캐시 클리어

개발 중 필요 시 캐시를 수동으로 지웁니다.

```python
# Streamlit UI: 우측 상단 메뉴 → "Clear cache"
# 또는 코드:
st.cache_data.clear()

# 특정 함수만:
calculate_seasonality.clear()
```

### 3. TTL 변경 금지

TTL은 신중하게 설정되었으므로 임의로 변경하지 마세요.

---

## 📚 참고 자료

- [Streamlit Caching 공식 문서](https://docs.streamlit.io/library/advanced-features/caching)

---

## 🎉 요약

✅ **데이터 로드**: `@st.cache_data(ttl=3600)`  
✅ **계산 결과**: `@st.cache_data`  
❌ **중복 래퍼 함수 금지**

간결하고 효율적인 2종 캐싱 전략으로 최적화되었습니다!
