"""
AI 인사이트 및 추천 모듈
"""

from .constants import RISK_RATIO_THRESHOLD, BENCHMARKS, SEASONALITY_COMMON
from .calculations import format_number


def generate_recommendations(scenarios, budget):
    """
    시뮬레이션 결과 기반 스마트 추천 생성 (구체적 수치 포함)

    Args:
        scenarios: 시나리오 데이터 (base 시나리오 사용)
        budget: 총 예산

    Returns:
        recommendations: 추천 리스트
    """
    recommendations = []

    media_data = scenarios.get('base', [])
    if not media_data:
        return recommendations

    sorted_media = sorted([m for m in media_data if m.get('cpa', 0) > 0], key=lambda x: x.get('cpa', 0))

    if len(sorted_media) >= 2:
        best_media = sorted_media[0]
        worst_media = sorted_media[-1]

        if worst_media['cpa'] > best_media['cpa'] * 1.5:
            shift_ratio = worst_media.get('budget_ratio', 0) * 0.1
            shift_budget = budget * (shift_ratio / 100)

            best_cvr = best_media.get('cvr', 0) / 100
            best_cpc = best_media.get('cpc', 0)
            if best_cpc > 0 and best_cvr > 0:
                additional_clicks = shift_budget / best_cpc
                additional_conversions = additional_clicks * best_cvr

                current_total_cv = sum(m.get('estimated_conversions_adjusted', 0) for m in media_data)
                current_avg_cpa = budget / current_total_cv if current_total_cv > 0 else 0
                new_total_cv = current_total_cv + additional_conversions
                new_avg_cpa = budget / new_total_cv if new_total_cv > 0 else 0
                cpa_improvement = current_avg_cpa - new_avg_cpa

                recommendations.append({
                    'type': 'info',
                    'icon': '💡',
                    'message': f"**{worst_media['name']}** 비중 {worst_media['budget_ratio']:.1f}% → **{worst_media['budget_ratio']-shift_ratio:.1f}%** 감소, "
                              f"**{best_media['name']}** 비중 {best_media['budget_ratio']:.1f}% → **{best_media['budget_ratio']+shift_ratio:.1f}%** 증가 시\n"
                              f"📈 전환 **+{additional_conversions:.0f}건**, 평균 CPA **-{cpa_improvement:,.0f}원** 개선 예상"
                })

    for media in sorted_media[:2]:
        ratio = media.get('budget_ratio', 0)
        cpa = media.get('cpa', 0)
        name = media.get('name', '매체')
        cvr = media.get('cvr', 0) / 100
        cpc = media.get('cpc', 0)

        if ratio < 20 and cpa > 0:
            increase_ratio = 10
            increase_budget = budget * (increase_ratio / 100)

            if cpc > 0 and cvr > 0:
                add_clicks = increase_budget / cpc
                add_cv = add_clicks * cvr
                add_cpa_impact = increase_budget / add_cv if add_cv > 0 else 0

                recommendations.append({
                    'type': 'info',
                    'icon': '🚀',
                    'message': f"**{name}** (현재 CPA {cpa:,.0f}원) 비중 {ratio:.1f}% → **{ratio+increase_ratio:.1f}%** 증가 시\n"
                              f"📈 전환 **+{add_cv:.0f}건**, 예상 CPA **{add_cpa_impact:,.0f}원** 유지"
                })

    for media in media_data:
        ratio = media.get('budget_ratio', 0)
        name = media.get('name', '매체')

        if ratio > RISK_RATIO_THRESHOLD:
            recommendations.append({
                'type': 'warning',
                'icon': '⚠️',
                'message': f"**{name}** 의존도({ratio:.1f}%)가 높습니다. 매체 알고리즘 변경이나 정책 변화 시 리스크가 큽니다. "
                          f"다른 매체로 분산을 권장합니다."
            })

    low_roas_media = [m for m in media_data if 0 < m.get('roas', 0) < 150]
    if low_roas_media:
        for media in low_roas_media:
            name = media.get('name', '매체')
            roas = media.get('roas', 0)
            cpa = media.get('cpa', 0)
            revenue_per_cv = media.get('revenue_per_conversion', 0)

            needed_revenue = cpa * 1.5
            current_revenue = revenue_per_cv
            revenue_gap = needed_revenue - current_revenue

            recommendations.append({
                'type': 'warning',
                'icon': '💰',
                'message': f"**{name}** ROAS {roas:.1f}%로 낮습니다. "
                          f"전환당 매출을 현재 {current_revenue:,.0f}원에서 **{needed_revenue:,.0f}원**으로 "
                          f"**(+{revenue_gap:,.0f}원)** 개선 시 ROAS 150% 달성 가능"
            })

    total_conversions = sum(m.get('estimated_conversions_adjusted', 0) for m in media_data)
    if 0 < total_conversions < 200:
        new_budget = budget * 1.3
        estimated_new_cv = total_conversions * 1.3

        recommendations.append({
            'type': 'info',
            'icon': '📈',
            'message': f"현재 예상 전환수({total_conversions:.0f}건)가 부족합니다. "
                      f"총 예산을 {format_number(int(budget))}원 → **{format_number(int(new_budget))}원** "
                      f"**(+30%, +{format_number(int(new_budget - budget))}원)** 증액 시 "
                      f"전환 **{estimated_new_cv:.0f}건** 달성 예상"
        })

    return recommendations


def generate_ai_insights(result_data, industry, month, goal):
    """
    시뮬레이션 결과 기반 고급 AI 인사이트 생성

    Args:
        result_data: 시뮬레이션 결과 데이터
        industry: 업종
        month: 운영 월
        goal: 캠페인 목표

    Returns:
        insights: 인사이트 리스트
    """
    insights = []

    scenarios = result_data.get('scenarios', {})
    media_data = scenarios.get('base', []) if scenarios else result_data.get('media_list', [])

    total_conversions = sum(m.get('estimated_conversions_adjusted', m.get('conversions', 0)) for m in media_data)

    total_budget = result_data.get('budget', 0)
    avg_cpa = (total_budget / total_conversions) if total_conversions > 0 else 0

    total_revenue = sum(m.get('total_revenue_adjusted', m.get('revenue', 0)) for m in media_data)
    avg_roas = (total_revenue / total_budget * 100) if total_budget > 0 else 0

    # 1. 성과 수준 평가
    if total_conversions >= 1000:
        insights.append({
            'type': 'success',
            'title': '🎯 우수한 전환 성과',
            'message': f'예상 전환수({total_conversions:,.0f}건)가 매우 높습니다. 안정적인 캠페인 운영이 가능합니다.'
        })
    elif total_conversions < 100:
        insights.append({
            'type': 'warning',
            'title': '⚠️ 전환 볼륨 부족',
            'message': f'예상 전환수({total_conversions:,.0f}건)가 적어 통계적 유의성이 낮을 수 있습니다. 예산 증액 또는 목표 조정을 권장합니다.'
        })

    # 2. 업종별 벤치마크 CPA 비교 (BENCHMARKS에서 동적 계산)
    media_benchmarks = BENCHMARKS.get(industry, {})
    cpa_values = [v.get('CPA', 0) for v in media_benchmarks.values() if v.get('CPA', 0) > 0]
    industry_avg_cpa = sum(cpa_values) / len(cpa_values) if cpa_values else 50000

    if avg_cpa > 0:
        if avg_cpa < industry_avg_cpa * 0.8:
            insights.append({
                'type': 'success',
                'title': '💰 효율적인 CPA',
                'message': f'평균 CPA({avg_cpa:,.0f}원)가 {industry} 업종 평균({industry_avg_cpa:,.0f}원)보다 {((industry_avg_cpa - avg_cpa) / industry_avg_cpa * 100):.0f}% 낮습니다.'
            })
        elif avg_cpa > industry_avg_cpa * 1.3:
            insights.append({
                'type': 'error',
                'title': '📈 높은 CPA',
                'message': f'평균 CPA({avg_cpa:,.0f}원)가 {industry} 업종 평균({industry_avg_cpa:,.0f}원)보다 높습니다. 타겟팅 또는 크리에이티브 개선이 필요합니다.'
            })

    # 3. 매체 다각화 분석
    sa_ratio = sum(m.get('budget_ratio', 0) for m in media_data if '검색' in m.get('category', ''))
    da_ratio = sum(m.get('budget_ratio', 0) for m in media_data if '디스플레이' in m.get('category', ''))

    if abs(sa_ratio - da_ratio) > RISK_RATIO_THRESHOLD:
        dominant = "검색광고" if sa_ratio > da_ratio else "디스플레이광고"
        insights.append({
            'type': 'info',
            'title': '🎯 매체 편중',
            'message': f'{dominant} 비중이 높습니다. 균형잡힌 믹스를 위해 다른 매체 확대를 검토하세요.'
        })

    # 4. 계절성 활용
    season_factor = SEASONALITY_COMMON.get(month, 1.0)
    if season_factor >= 1.15:
        insights.append({
            'type': 'success',
            'title': '🔥 최적의 시기',
            'message': f'{month}월은 {industry} 업종의 성수기입니다. 공격적인 집행을 권장합니다.'
        })
    elif season_factor <= 0.85:
        insights.append({
            'type': 'warning',
            'title': '❄️ 비수기 대응',
            'message': f'{month}월은 효율이 낮은 시기입니다. 브랜딩 중심 또는 예산 축소를 고려하세요.'
        })

    # 5. 목표 일치도
    if goal and "전환" in str(goal) and sa_ratio < 60:
        insights.append({
            'type': 'info',
            'title': '🎯 목표-믹스 불일치',
            'message': '전환 중심 목표인데 검색광고 비중이 낮습니다. SA 비중을 60% 이상으로 증가시키면 더 좋은 성과를 기대할 수 있습니다.'
        })

    # 6. ROAS 평가
    if avg_roas > 0:
        if avg_roas >= 200:
            insights.append({
                'type': 'success',
                'title': '💰 높은 수익성',
                'message': f'평균 ROAS({avg_roas:.1f}%)가 우수합니다. 예산 증액을 고려해보세요.'
            })
        elif avg_roas < 100:
            insights.append({
                'type': 'error',
                'title': '⚠️ 낮은 수익성',
                'message': f'평균 ROAS({avg_roas:.1f}%)가 100% 미만입니다. 전환당 매출 증가 또는 CPA 개선이 필요합니다.'
            })

    return insights
