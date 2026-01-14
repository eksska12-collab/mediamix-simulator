# 📊 벤치마크 데이터 관리 가이드

## 개요

미디어믹스 시뮬레이터의 벤치마크 데이터가 외부 JSON 파일로 분리되었습니다.
코드 수정 없이 데이터만 업데이트할 수 있어 유지보수가 훨씬 쉬워졌습니다.

## 📁 파일 구조

```
madup/
├── benchmarks.json          # 벤치마크 데이터
├── media_categories.json    # 매체 카테고리 정의
├── app.py                   # Streamlit 웹앱
├── media_mix_simulator.py   # CLI 시뮬레이터
└── DATA_README.md          # 이 문서
```

---

## 📋 benchmarks.json

벤치마크 데이터를 포함하는 메인 파일입니다.

### 포함된 데이터

1. **INDUSTRY_BASE_METRICS** - 업종별 기본 지표
   - 보험, 금융, 패션, IT/테크
   - 각 업종의 기본 CTR, CPC, CVR

2. **SEASONALITY_COMMON** - 월별 계절성 보정 계수
   - 1월~12월 각각의 보정 계수
   - 전체 시장의 일반적인 계절 트렌드

3. **INDUSTRY_SEASON_WEIGHT** - 업종별 계절성 가중치
   - 각 업종의 성수기/비수기 월
   - 성수기/비수기 배율

4. **MEDIA_MULTIPLIERS** - 매체별 성과 배율
   - 각 매체의 CTR, CPC, CVR 배율
   - Base Metrics 대비 조정 값

5. **BENCHMARKS** - 업종별 매체 효율 벤치마크
   - 4개 업종 × 다수 매체
   - 각 매체의 실제 CPC, CTR, CVR 값

6. **SEASONALITY** - 기존 호환용 계절성 테이블

### 수정 방법

```json
{
  "INDUSTRY_BASE_METRICS": {
    "보험": {
      "CTR": 0.008,    // 클릭률 (0.8%)
      "CPC": 2500,     // 클릭당 비용 (원)
      "CVR": 0.02      // 전환율 (2%)
    }
  }
}
```

**주의사항:**
- JSON 형식을 정확히 유지하세요 (쉼표, 따옴표 등)
- 숫자 값은 따옴표 없이 입력
- 비율은 소수점 형태 (예: 2% = 0.02)

---

## 📋 media_categories.json

매체 카테고리와 분류 정보를 포함합니다.

### 포함된 데이터

1. **MEDIA_CATEGORIES_CLI** - CLI 버전용 매체 카테고리
   - 검색광고, 디스플레이광고, 동영상광고

2. **MEDIA_CATEGORIES_WEB** - 웹앱용 매체 카테고리
   - SA (검색광고)
   - DA (디스플레이광고)

3. **MEDIA_TYPE_MAP** - 매체명 → 타입 매핑

4. **MEDIA_DISPLAY_NAMES** - 표시명 매핑

5. **CATEGORY_LABELS** - 카테고리 라벨

### 수정 방법

```json
{
  "MEDIA_CATEGORIES_WEB": {
    "SA": [
      "네이버 검색광고",
      "구글 검색광고",
      "새로운 매체"    // 새 매체 추가
    ]
  }
}
```

---

## 🔧 데이터 수정 가이드

### 1. 새 업종 추가하기

**benchmarks.json** 파일에서:

```json
"INDUSTRY_BASE_METRICS": {
  "기존업종": { ... },
  "새업종": {
    "CTR": 0.015,
    "CPC": 1000,
    "CVR": 0.025,
    "description": "설명"
  }
}
```

**INDUSTRY_SEASON_WEIGHT**와 **BENCHMARKS**에도 추가하세요.

### 2. 새 매체 추가하기

**media_categories.json** 파일에서:

```json
"MEDIA_CATEGORIES_WEB": {
  "SA": [
    "기존 매체",
    "새로운 매체"    // 추가
  ]
}
```

**benchmarks.json**의 **MEDIA_MULTIPLIERS**에도 추가:

```json
"MEDIA_MULTIPLIERS": {
  "새매체_SA": {
    "CTR": 1.0,
    "CPC": 1.0,
    "CVR": 1.0,
    "description": "설명"
  }
}
```

### 3. 벤치마크 값 업데이트하기

**benchmarks.json**의 **BENCHMARKS** 섹션:

```json
"BENCHMARKS": {
  "보험": {
    "네이버_SA": {
      "cpc": 800,    // 업데이트된 값
      "ctr": 2.0,
      "cvr": 3.5
    }
  }
}
```

### 4. 계절성 보정 수정하기

**benchmarks.json**의 **SEASONALITY_COMMON**:

```json
"SEASONALITY_COMMON": {
  "1": 1.10,    // 1월 보정 계수
  "2": 0.95,    // 2월 보정 계수
  ...
}
```

---

## ✅ 수정 후 검증

### 1. JSON 형식 검증

온라인 JSON 검증기 사용:
- https://jsonlint.com/
- 파일 내용을 붙여넣고 "Validate JSON" 클릭

### 2. 앱 테스트

```bash
# 웹앱 실행
python -m streamlit run app.py

# CLI 실행
python media_mix_simulator.py
```

### 3. 오류 확인

- 파일을 찾을 수 없다는 오류: 파일 경로 확인
- 파싱 오류: JSON 형식 오류, 쉼표/괄호 확인
- 데이터 없음: 키 이름이 정확한지 확인

---

## 🔄 버전 관리

JSON 파일을 수정할 때마다 버전을 업데이트하세요:

```json
{
  "version": "1.0.1",
  "last_updated": "2024-12-30",
  "description": "변경 사항 설명"
}
```

### 변경 이력

- **1.0.0** (2024-12-30)
  - 초기 외부화
  - 모든 벤치마크 데이터를 JSON으로 분리

---

## 💡 장점

### Before (하드코딩)
```python
INDUSTRY_BASE_METRICS = {
    '보험': {
        'CTR': 0.008,
        'CPC': 2500,
        'CVR': 0.02
    }
}
```
❌ 데이터 수정 시 코드 재배포 필요
❌ 버전 관리 어려움
❌ 협업 시 충돌 가능성

### After (JSON 외부화)
```json
{
  "INDUSTRY_BASE_METRICS": {
    "보험": {
      "CTR": 0.008,
      "CPC": 2500,
      "CVR": 0.02
    }
  }
}
```
✅ 코드 수정 없이 데이터만 업데이트
✅ 버전 관리 용이
✅ 협업 편리
✅ 데이터 백업 간편

---

## 📞 문의

데이터 수정 중 문제가 발생하면:
1. JSON 형식 검증기로 확인
2. 백업 파일과 비교
3. 개발팀에 문의

---

## 🔐 백업 권장사항

JSON 파일 수정 전 항상 백업하세요:

```bash
# 백업 생성
copy benchmarks.json benchmarks.json.backup
copy media_categories.json media_categories.json.backup
```

날짜별 백업:
```bash
copy benchmarks.json benchmarks_20241230.json
```

---

## 📚 참고 자료

- [JSON 공식 문서](https://www.json.org/json-ko.html)
- [JSON 검증기](https://jsonlint.com/)
- Python json 모듈: https://docs.python.org/ko/3/library/json.html

