import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class AIClassifier:
    """
    AI活力分类器
    根据调用记录对每个AI进行分类：僵尸、边缘、卡顿、核心、正常
    """

    DEFAULT_THRESHOLDS = {
        'zombie_days': 30,
        'edge_call_threshold': 10,
        'edge_dept_threshold': 1,
        'slow_threshold': 5.0,
        'error_threshold': 0.05,
        'core_call_threshold': 100,
        'core_dept_threshold': 2,
    }

    def __init__(self, thresholds: Optional[Dict] = None):
        self.thresholds = self.DEFAULT_THRESHOLDS.copy()
        if thresholds:
            self.thresholds.update(thresholds)

    def classify(self, records: List[Dict], as_of: Optional[datetime] = None) -> Dict[str, Dict]:
        if as_of is None:
            as_of = datetime.now()

        stats_per_ai = self._aggregate_stats(records)

        result = {}
        for ai_name, stats in stats_per_ai.items():
            classification = self._determine_classification(stats, as_of)
            result[ai_name] = {
                'classification': classification,
                'stats': stats
            }
        return result

    def _aggregate_stats(self, records: List[Dict]) -> Dict[str, Dict]:
        ai_data = defaultdict(lambda: {
            'total_calls': 0,
            'response_times': [],
            'error_count': 0,
            'status_code_count': 0,
            'departments': set(),
            'last_call': None
        })

        for rec in records:
            ai = rec.get('ai_name')
            if not ai:
                logger.warning("记录缺少 ai_name，已跳过: %s", rec)
                continue

            data = ai_data[ai]
            data['total_calls'] += 1

            dept = rec.get('department')
            if dept:
                data['departments'].add(dept)

            resp_time = rec.get('response_time')
            if resp_time is not None:
                try:
                    data['response_times'].append(float(resp_time))
                except (ValueError, TypeError):
                    logger.debug("无效的响应时间: %s", resp_time)

            status = rec.get('status_code')
            if status is not None:
                data['status_code_count'] += 1
                try:
                    code = int(status)
                    if code < 200 or code >= 400:
                        data['error_count'] += 1
                except (ValueError, TypeError):
                    logger.debug("无效的状态码: %s", status)

            ts = rec.get('timestamp')
            if ts:
                if data['last_call'] is None or ts > data['last_call']:
                    data['last_call'] = ts

        stats = {}
        for ai, data in ai_data.items():
            total = data['total_calls']
            avg_resp = None
            if data['response_times']:
                avg_resp = sum(data['response_times']) / len(data['response_times'])

            error_rate = None
            if data['status_code_count'] > 0:
                error_rate = data['error_count'] / data['status_code_count']

            stats[ai] = {
                'total_calls': total,
                'avg_response_time': avg_resp,
                'error_rate': error_rate,
                'departments': list(data['departments']),
                'last_call': data['last_call']
            }
        return stats

    def _determine_classification(self, stats: Dict, as_of: datetime) -> str:
        last_call = stats.get('last_call')
        if last_call:
            days_since_last = (as_of - last_call).days
            if days_since_last > self.thresholds['zombie_days']:
                return '僵尸'

        avg_resp = stats.get('avg_response_time')
        error_rate = stats.get('error_rate')
        if (avg_resp is not None and avg_resp > self.thresholds['slow_threshold']) or \
           (error_rate is not None and error_rate > self.thresholds['error_threshold']):
            return '卡顿'

        total = stats['total_calls']
        dept_count = len(stats['departments'])
        if total > self.thresholds['core_call_threshold'] and dept_count > self.thresholds['core_dept_threshold']:
            return '核心'

        if total < self.thresholds['edge_call_threshold'] and dept_count <= self.thresholds['edge_dept_threshold']:
            return '边缘'

        return '正常'