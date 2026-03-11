import os
from .json_parser import JSONLogParser
from .csv_parser import CSVLogParser
from .apache_parser import ApacheLogParser

class ParserFactory:
    """根据文件扩展名或格式字符串创建合适的解析器"""
    
    @staticmethod
    def create_parser(file_path: str, format: str = None, **kwargs):
        """
        :param file_path: 日志文件路径，用于判断扩展名
        :param format: 显式指定格式，优先级高于扩展名
        :param kwargs: 传递给具体解析器的参数
        """
        if format is None:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.json':
                format = 'json'
            elif ext == '.csv':
                format = 'csv'
            elif ext == '.log':
                format = 'apache'
            else:
                raise ValueError(f"无法从扩展名 {ext} 推断格式，请显式指定format")
        
        if format == 'json':
            return JSONLogParser(**kwargs)
        elif format == 'csv':
            if 'fieldnames' not in kwargs:
                # 尝试从文件第一行读取
                with open(file_path, 'r') as f:
                    first_line = f.readline().strip()
                    kwargs['fieldnames'] = first_line.split(kwargs.get('delimiter', ','))
            return CSVLogParser(**kwargs)
        elif format == 'apache':
            return ApacheLogParser(**kwargs)
        else:
            raise ValueError(f"不支持的日志格式: {format}")