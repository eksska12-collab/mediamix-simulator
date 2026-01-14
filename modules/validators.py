"""
검증 함수 모듈
"""

from .constants import EFFICIENCY_WARNING_THRESHOLD, EFFICIENCY_RANGES

# =============================================================================
# 입력값 검증 함수
# =============================================================================

def validate_input(input_type, value, **kwargs):
    """
    입력값 통합 검증 함수
    
    Args:
        input_type (str): 검증 타입 ('budget', 'ratio', 'cpc', 'ctr', 'cvr', 'revenue', 'month', 'adjustment')
        value: 검증할 값
        **kwargs: 추가 파라미터 (industry, min_val, max_val 등)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # 1. 예산 검증
        if input_type == 'budget':
            if not isinstance(value, (int, float)) or value <= 0:
                return False, "예산은 0보다 큰 숫자여야 합니다."
            if value < 1000000:
                return False, "예산은 최소 100만원 이상이어야 합니다."
            if value > 10000000000:
                return False, "예산이 너무 큽니다. (최대 100억)"
            return True, None
        
        # 2. 예산 비중 검증
        elif input_type == 'ratio':
            if not isinstance(value, (int, float)) or value < 0 or value > 100:
                return False, "예산 비중은 0~100 사이의 값이어야 합니다."
            return True, None
        
        # 3. CPC 검증
        elif input_type == 'cpc':
            if not isinstance(value, (int, float)) or value <= 0:
                return False, "CPC는 0보다 큰 값이어야 합니다."
            if value < 10 or value > 100000:
                return False, "CPC가 비정상적입니다. (10원~100,000원)"
            return True, None
        
        # 4. CTR 검증
        elif input_type == 'ctr':
            if not isinstance(value, (int, float)) or value < 0 or value > 100:
                return False, "CTR은 0~100 사이의 값이어야 합니다."
            industry = kwargs.get('industry')
            if industry:
                warning = validate_efficiency('CTR', value, industry)
                if warning:
                    return True, warning  # 경고지만 통과
            return True, None
        
        # 5. CVR 검증
        elif input_type == 'cvr':
            if not isinstance(value, (int, float)) or value < 0 or value > 100:
                return False, "CVR은 0~100 사이의 값이어야 합니다."
            industry = kwargs.get('industry')
            if industry:
                warning = validate_efficiency('CVR', value, industry)
                if warning:
                    return True, warning  # 경고지만 통과
            return True, None
        
        # 6. 전환당 매출 검증
        elif input_type == 'revenue':
            if not isinstance(value, (int, float)) or value <= 0:
                return False, "전환당 매출은 0보다 큰 값이어야 합니다."
            if value < 1000 or value > 100000000:
                return False, "전환당 매출이 비정상적입니다. (1,000원~1억원)"
            return True, None
        
        # 7. 월 검증
        elif input_type == 'month':
            if not isinstance(value, int) or value < 1 or value > 12:
                return False, "월은 1~12 사이의 값이어야 합니다."
            return True, None
        
        # 8. 예측 오차 검증
        elif input_type == 'adjustment':
            if not isinstance(value, (int, float)) or value < -100 or value > 100:
                return False, "예측 오차는 -100~100 사이의 값이어야 합니다."
            return True, None
        
        # 9. 범위 검증 (범용)
        elif input_type == 'range':
            min_val = kwargs.get('min_val', float('-inf'))
            max_val = kwargs.get('max_val', float('inf'))
            if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                return False, f"값은 {min_val}~{max_val} 사이여야 합니다."
            return True, None
        
        else:
            return False, f"알 수 없는 검증 타입: {input_type}"
    
    except Exception as e:
        return False, f"검증 중 오류 발생: {str(e)}"

# =============================================================================
# 효율 검증 함수
# =============================================================================

def validate_efficiency(metric_name, value, industry):
    """
    입력 효율값 검증 및 경고
    
    Args:
        metric_name: 'CTR', 'CPC', 'CVR'
        value: 입력값
        industry: 업종
    
    Returns:
        warning_message: 경고 메시지 (없으면 None)
    """
    ranges = EFFICIENCY_RANGES.get(industry, {}).get(metric_name, {})
    if not ranges:
        return None
    
    avg = ranges['avg']
    min_val = ranges['min']
    max_val = ranges['max']
    
    # 평균 대비 ±50% 초과 시 경고
    if value < avg * EFFICIENCY_WARNING_THRESHOLD:
        diff_percent = ((avg - value) / avg) * 100
        return f"⚠️ {metric_name}이 {industry} 업종 평균({avg})보다 {diff_percent:.0f}% 낮습니다."
    
    elif value > avg * 1.5:
        diff_percent = ((value - avg) / avg) * 100
        return f"⚠️ {metric_name}이 {industry} 업종 평균({avg})보다 {diff_percent:.0f}% 높습니다."
    
    # 범위 벗어남
    elif value < min_val or value > max_val:
        return f"⚠️ {metric_name} 값이 일반적인 범위({min_val}~{max_val})를 벗어났습니다."
    
    return None

