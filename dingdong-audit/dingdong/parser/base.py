import abc
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class LogParser(abc.ABC):
    """日志解析器基类，所有具体解析器必须实现 parse_line 方法"""
    
    @abc.abstractmethod
    def parse_line(self, line: str) -> Optional[Dict]:
        """
        解析单行日志，返回统一格式的字典：
        {
            'ai_name': str,           # AI名称/ID
            'timestamp': datetime,     # 调用时间
            'department': str,         # 来源部门
            'response_time': float,    # 响应时间（秒）
            'status_code': int         # HTTP状态码或自定义状态码
        }
        如果行格式不匹配，返回 None
        """
        pass

    def parse_file(self, file_path: str, return_raw: bool = False) -> List:
        """
        解析整个文件，返回记录列表。
        :param return_raw: 如果为True，返回 (record, raw_line) 的列表；否则只返回记录字典。
        """
        results = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip('\n')
                if not line:
                    continue
                try:
                    record = self.parse_line(line)
                    if record:
                        if return_raw:
                            results.append((record, line))
                        else:
                            results.append(record)
                    else:
                        logger.warning(f"第 {line_num} 行无法解析，已忽略: {line[:50]}...")
                except Exception as e:
                    logger.error(f"第 {line_num} 行解析异常: {e}, 行内容: {line[:50]}")
        return results