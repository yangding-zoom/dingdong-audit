import json
from datetime import datetime
from typing import Optional, Dict
from .base import LogParser

class JSONLogParser(LogParser):
    """解析JSON格式日志，每行一个JSON对象"""
    
    def __init__(self, mapping: Dict = None):
        """
        :param mapping: 字段映射，将日志中的字段名映射到标准字段
        """
        self.mapping = mapping or {
            'ai_name': 'ai_name',
            'timestamp': 'timestamp',
            'department': 'department',
            'response_time': 'response_time',
            'status_code': 'status_code'
        }
    
    def parse_line(self, line: str) -> Optional[Dict]:
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None
        
        # 提取标准字段
        record = {}
        for std_field, log_field in self.mapping.items():
            if log_field in data:
                value = data[log_field]
                # 时间戳转换
                if std_field == 'timestamp':
                    if isinstance(value, (int, float)):
                        record['timestamp'] = datetime.fromtimestamp(value)
                    elif isinstance(value, str):
                        # 尝试常见格式
                        for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d/%b/%Y:%H:%M:%S'):
                            try:
                                record['timestamp'] = datetime.strptime(value, fmt)
                                break
                            except ValueError:
                                continue
                        else:
                            record['timestamp'] = None
                    else:
                        record['timestamp'] = None
                elif std_field == 'response_time':
                    record['response_time'] = float(value) if value is not None else None
                elif std_field == 'status_code':
                    record['status_code'] = int(value) if value is not None else None
                else:
                    record[std_field] = value
            else:
                record[std_field] = None
        
        # 确保关键字段存在
        if record.get('ai_name') is None:
            return None
        return record