import re
from datetime import datetime
from typing import Optional, Dict
from .base import LogParser

class ApacheLogParser(LogParser):
    """
    解析Apache通用日志格式（Common Log Format）
    示例：127.0.0.1 - - [10/Oct/2023:13:55:36 +0000] "GET /ai/model HTTP/1.1" 200 2326
    我们从中提取时间、状态码，但需要将AI名称映射到URL路径，部门需额外配置或默认。
    """
    
    # 通用日志格式正则
    LOG_PATTERN = re.compile(
        r'(\S+) \S+ \S+ \[([^]]+)\] "(\S+) (\S+) \S+" (\d{3}) (\d+)'
    )
    
    def __init__(self, url_to_ai_func=None, default_department='unknown'):
        """
        :param url_to_ai_func: 函数，从URL中提取AI名称，默认返回整个URL路径
        :param default_department: 默认部门，若无法从日志获取
        """
        self.url_to_ai_func = url_to_ai_func or (lambda url: url.strip('/').split('/')[-1] if url else None)
        self.default_department = default_department
    
    def parse_line(self, line: str) -> Optional[Dict]:
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None
        
        host, timestamp_str, method, url, status_code, size = match.groups()
        
        # 解析时间 [10/Oct/2023:13:55:36 +0000]
        try:
            dt_str = timestamp_str.split()[0]  # "10/Oct/2023:13:55:36"
            timestamp = datetime.strptime(dt_str, '%d/%b/%Y:%H:%M:%S')
        except Exception:
            timestamp = None
        
        ai_name = self.url_to_ai_func(url)
        if not ai_name:
            return None
        
        record = {
            'ai_name': ai_name,
            'timestamp': timestamp,
            'department': self.default_department,
            'response_time': None,  # Apache日志无响应时间
            'status_code': int(status_code) if status_code.isdigit() else None
        }
        return record