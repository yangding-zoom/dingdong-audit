import csv
from datetime import datetime
from io import StringIO
from typing import Optional, Dict, List
from .base import LogParser

class CSVLogParser(LogParser):
    """解析CSV格式日志，需指定列名"""
    
    def __init__(self, fieldnames: List[str], delimiter=',', mapping: Dict = None):
        """
        :param fieldnames: CSV文件的列名列表
        :param delimiter: 分隔符
        :param mapping: 字段映射，将列名映射到标准字段
        """
        self.fieldnames = fieldnames
        self.delimiter = delimiter
        self.mapping = mapping or {
            'ai_name': 'ai_name',
            'timestamp': 'timestamp',
            'department': 'department',
            'response_time': 'response_time',
            'status_code': 'status_code'
        }
        # 构建索引映射
        self.field_to_index = {name: idx for idx, name in enumerate(fieldnames)}
    
    def parse_line(self, line: str) -> Optional[Dict]:
        # 使用csv模块解析一行
        reader = csv.reader(StringIO(line), delimiter=self.delimiter)
        try:
            row = next(reader)
        except StopIteration:
            return None
        
        if len(row) != len(self.fieldnames):
            return None
        
        record = {}
        for std_field, log_field in self.mapping.items():
            if log_field in self.field_to_index:
                value = row[self.field_to_index[log_field]].strip()
                if std_field == 'timestamp':
                    for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d/%b/%Y:%H:%M:%S'):
                        try:
                            record['timestamp'] = datetime.strptime(value, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        record['timestamp'] = None
                elif std_field == 'response_time':
                    try:
                        record['response_time'] = float(value) if value else None
                    except ValueError:
                        record['response_time'] = None
                elif std_field == 'status_code':
                    try:
                        record['status_code'] = int(value) if value else None
                    except ValueError:
                        record['status_code'] = None
                else:
                    record[std_field] = value if value else None
            else:
                record[std_field] = None
        
        if record.get('ai_name') is None:
            return None
        return record