#!/usr/bin/env python
"""
叮咚猫命令行接口
"""
import argparse
import logging
import sys
import os
import json
from dingdong.parser.factory import ParserFactory
from dingdong.runner import run_scan

def setup_logging(log_file=None):
    """配置日志，同时输出到控制台和文件"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 控制台handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    # 文件handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def main():
    parser = argparse.ArgumentParser(description='叮咚猫AI活力审计系统')
    parser.add_argument('--log-dir', required=True, help='日志文件所在目录')
    parser.add_argument('--format', default='auto', help='日志格式: json, csv, apache, auto (默认根据扩展名推断)')
    parser.add_argument('--report', action='store_true', help='生成HTML报告')
    parser.add_argument('--output-dir', default='./reports', help='报告输出目录 (默认 ./reports)')
    parser.add_argument('--thresholds', help='阈值配置文件 (JSON格式)')
    args = parser.parse_args()

    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)

    # 设置日志文件
    log_file = os.path.join(args.output_dir, 'run.log')
    logger = setup_logging(log_file)

    logger.info("叮咚猫启动，日志目录: %s", args.log_dir)

    # 加载阈值配置
    thresholds = None
    if args.thresholds:
        with open(args.thresholds, 'r') as f:
            thresholds = json.load(f)

    try:
        report_path = run_scan(args.log_dir, args.output_dir, thresholds)
        logger.info("报告已生成: %s", report_path)
    except Exception as e:
        logger.error("扫描失败: %s", e)
        sys.exit(1)

    logger.info("叮咚猫运行结束")

if __name__ == '__main__':
    main()