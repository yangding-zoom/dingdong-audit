import os
import logging
from .parser.factory import ParserFactory
from .core.classifier import AIClassifier
from .report.generator import ReportGenerator

logger = logging.getLogger(__name__)

def run_scan(log_dir, output_dir, thresholds=None):
    """
    执行完整扫描流程：解析日志、分类、生成报告和溯源包。
    返回生成的报告路径。
    """
    # 收集日志文件
    log_files = []
    for root, dirs, files in os.walk(log_dir):
        for file in files:
            if file.endswith(('.log', '.json', '.csv')):
                log_files.append(os.path.join(root, file))
    if not log_files:
        raise ValueError(f"在 {log_dir} 中未找到日志文件")
    
    all_records_with_raw = []
    for file_path in log_files:
        parser = ParserFactory.create_parser(file_path)
        records_with_raw = parser.parse_file(file_path, return_raw=True)
        all_records_with_raw.extend(records_with_raw)
        logger.info(f"解析 {file_path} 得到 {len(records_with_raw)} 条记录")
    
    if not all_records_with_raw:
        raise ValueError("未能解析到任何记录")
    
    records = [r for r, _ in all_records_with_raw]
    classifier = AIClassifier(thresholds=thresholds)
    result = classifier.classify(records)
    
    generator = ReportGenerator(output_dir=output_dir)
    report_path = generator.generate(result, records_with_raw=all_records_with_raw)
    return report_path